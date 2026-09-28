"""API de classification : prédiction, feedback, rechargement du champion.

    uvicorn src.inference.api:app --port 8000

Le modèle servi est toujours `models:/news-classifier@champion`. L'API vérifie
l'alias toutes les `api.poll_seconds` secondes : chaque worker/replica se met à
jour seul après une promotion, sans dépendre d'un appel à /model/reload.
"""

import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from config import get_config
from src import registry
from src.inference.schemas import (
    BatchDocumentInput,
    BatchPredictionResponse,
    DocumentInput,
    FeedbackInput,
    FeedbackResponse,
    PredictionResponse,
)
from src.inference.store import PredictionStore
from src.utils.logger import get_logger

logger = get_logger(__name__)

REQUESTS = Counter("api_requests_total", "Requêtes HTTP", ["method", "endpoint", "status"])
LATENCY = Histogram("api_request_latency_seconds", "Latence HTTP", ["method", "endpoint"])
PREDICTIONS = Counter("predictions_total", "Prédictions servies", ["label"])
PREDICTION_ERRORS = Counter("prediction_errors_total", "Erreurs de prédiction", ["error_type"])
CONFIDENCE = Histogram(
    "prediction_confidence",
    "Confiance max des prédictions",
    buckets=(0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0),
)
FEEDBACK = Counter("feedback_total", "Labels de feedback reçus", ["correct"])
MODEL_LOADED = Gauge("model_loaded", "1 si un modèle est chargé")
MODEL_VERSION = Gauge("model_version", "Version du champion servi")


class ModelService:
    """Tient le champion chargé ; remplacement atomique sous verrou."""

    def __init__(self):
        self._lock = threading.Lock()
        self._client = None
        self.current: registry.LoadedModel | None = None

    @property
    def client(self):
        if self._client is None:
            self._client = registry.setup_mlflow()
        return self._client

    def reload(self) -> dict:
        loaded = registry.load_champion(self.client)
        if loaded is None:
            raise RuntimeError("aucun modèle avec l'alias @champion dans le registry")
        with self._lock:
            self.current = loaded
        MODEL_LOADED.set(1)
        MODEL_VERSION.set(float(loaded.version))
        logger.info("champion chargé", extra={"extra_fields": {"version": loaded.version}})
        return self.info()

    def refresh_if_changed(self) -> bool:
        version = registry.champion_version(self.client)
        if version and (self.current is None or version != self.current.version):
            self.reload()
            return True
        return False

    def info(self) -> dict:
        current = self.current
        if current is None:
            return {"model_loaded": False}
        return {
            "model_loaded": True,
            "model_name": registry.model_name(),
            "version": current.version,
            "run_id": current.run_id,
            "holdout_f1_macro": current.holdout.get("f1_macro"),
            "classes": list(current.profile["classes"]),
        }


service = ModelService()
store: PredictionStore | None = None


def _poll_champion(interval: float, stop: threading.Event) -> None:
    while not stop.wait(interval):
        try:
            service.refresh_if_changed()
        except Exception as exc:  # registry indisponible : on réessaie au prochain tour
            logger.warning(
                "vérification du champion impossible", extra={"extra_fields": {"error": str(exc)}}
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global store
    store = PredictionStore()
    MODEL_LOADED.set(0)
    try:
        service.reload()
    except Exception as exc:
        logger.error("démarrage sans modèle", extra={"extra_fields": {"error": str(exc)}})
    stop = threading.Event()
    poll = float(get_config()["api"]["poll_seconds"])
    if poll > 0:
        threading.Thread(target=_poll_champion, args=(poll, stop), daemon=True).start()
    yield
    stop.set()


app = FastAPI(
    title="News classifier",
    description="Classification AG News · feedback · drift · retrain champion/challenger",
    version="2.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def observe(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    endpoint = getattr(route, "path", "unmatched")
    LATENCY.labels(request.method, endpoint).observe(time.perf_counter() - started)
    REQUESTS.labels(request.method, endpoint, response.status_code).inc()
    return response


def _predict(texts: list[str]) -> list[PredictionResponse]:
    current = service.current
    if current is None:
        PREDICTION_ERRORS.labels("model_not_loaded").inc()
        raise HTTPException(503, "aucun modèle chargé : lancer `make train`")
    try:
        proba = current.model.predict_proba(texts)
    except Exception as exc:
        PREDICTION_ERRORS.labels("prediction_error").inc()
        logger.error("échec de prédiction", exc_info=True)
        raise HTTPException(500, "erreur de prédiction") from exc

    classes = [str(c) for c in current.model.classes_]
    rows = []
    for text, probs in zip(texts, proba, strict=True):
        best = int(probs.argmax())
        rows.append({"text": text, "predicted": classes[best], "confidence": float(probs[best])})
        PREDICTIONS.labels(classes[best]).inc()
        CONFIDENCE.observe(float(probs[best]))
    ids = store.log(rows, current.version)
    return [
        PredictionResponse(
            prediction_id=pid,
            prediction=row["predicted"],
            confidence=row["confidence"],
            probabilities={c: round(float(p), 6) for c, p in zip(classes, probs, strict=True)},
            model_version=current.version,
        )
        for pid, row, probs in zip(ids, rows, proba, strict=True)
    ]


@app.get("/health")
def health():
    info = service.info()
    status = 200 if info["model_loaded"] else 503
    return JSONResponse({"status": "ok" if status == 200 else "no_model", **info}, status)


@app.post("/predict", response_model=PredictionResponse)
def predict(document: DocumentInput):
    return _predict([document.text])[0]


@app.post("/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(batch: BatchDocumentInput):
    predictions = _predict(batch.texts)
    return BatchPredictionResponse(predictions=predictions, total=len(predictions))


@app.post("/feedback", response_model=FeedbackResponse)
def feedback(item: FeedbackInput):
    """Vrai label d'une prédiction passée : alimente la précision live et le retrain."""
    current = service.current
    if current is not None and item.label not in current.profile["classes"]:
        raise HTTPException(422, f"label inconnu : {item.label}")
    row = store.add_feedback(item.prediction_id, item.label)
    if row is None:
        raise HTTPException(404, "prediction_id inconnu")
    correct = row["predicted"] == row["true_label"]
    FEEDBACK.labels(str(correct).lower()).inc()
    return FeedbackResponse(prediction_id=item.prediction_id, correct=correct)


@app.get("/model/info")
def model_info():
    return service.info()


@app.post("/model/reload")
def reload_model():
    try:
        return service.reload()
    except Exception as exc:
        raise HTTPException(503, f"rechargement impossible : {exc}") from exc


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
