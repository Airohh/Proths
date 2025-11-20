"""
API FastAPI pour les prédictions avec logging structuré et gestion d'erreurs
"""
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import mlflow.sklearn
import numpy as np
from pathlib import Path
import sys
import time
import traceback

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.training.preprocessing import load_preprocessing_artifacts
from src.utils.logger import get_logger
from src.utils.validators import (
    DocumentInput,
    BatchDocumentInput,
    PredictionResponse,
    BatchPredictionResponse
)
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response
from config import get_config

# Logger
logger = get_logger(__name__)

# Configuration
config = get_config()
api_config = config.get('api', {})

# Métriques Prometheus
REQUEST_COUNT = Counter('api_requests_total', 'Total number of API requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'API request latency', ['method', 'endpoint'])
PREDICTION_COUNT = Counter('predictions_total', 'Total number of predictions', ['model_type'])
PREDICTION_ERRORS = Counter('prediction_errors_total', 'Total prediction errors', ['error_type'])
MODEL_LOADED = Gauge('model_loaded', 'Whether the model is loaded (1) or not (0)')

app = FastAPI(
    title="Document Classification API",
    description="API pour la classification de documents avec monitoring MLOps",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle et les artifacts
logger.info("Chargement du modèle...")
model = None
vectorizer = None
label_encoder = None
model_type = None

try:
    model = mlflow.sklearn.load_model("models:/document-classifier-random_forest/latest")
    vectorizer, label_encoder = load_preprocessing_artifacts()
    model_type = "random_forest"
    MODEL_LOADED.set(1)
    logger.info("Modèle chargé avec succès", extra={'extra_fields': {'model_type': model_type}})
except Exception as e:
    logger.error(f"Erreur lors du chargement du modèle: {e}", exc_info=True)
    MODEL_LOADED.set(0)
    # En production, on pourrait charger un modèle par défaut ou échouer au démarrage


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire global d'exceptions"""
    logger.error(
        f"Exception non gérée: {str(exc)}",
        extra={
            'extra_fields': {
                'path': request.url.path,
                'method': request.method,
                'exception_type': type(exc).__name__
            }
        },
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if logger.level <= 10 else "An error occurred"
        }
    )


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware pour le logging des requêtes"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code}",
        extra={
            'extra_fields': {
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'process_time': process_time
            }
        }
    )
    
    return response


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "healthy",
        "service": "document-classification-api",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check détaillé"""
    health_status = {
        "status": "healthy" if model is not None else "degraded",
        "model_loaded": model is not None,
        "model_type": model_type if model is not None else None
    }
    
    if model is None:
        health_status["status"] = "unhealthy"
        return JSONResponse(status_code=503, content=health_status)
    
    return health_status


@app.post("/predict", response_model=PredictionResponse)
async def predict(document: DocumentInput):
    """
    Prédiction pour un seul document
    
    Args:
        document: Document à classifier
    
    Returns:
        Prédiction avec confiance et probabilités
    """
    if model is None or vectorizer is None or label_encoder is None:
        PREDICTION_ERRORS.labels(error_type="model_not_loaded").inc()
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Veuillez entraîner un modèle d'abord."
        )
    
    try:
        # Preprocessing
        text_vectorized = vectorizer.transform([document.text])
        
        # Prédiction
        prediction = model.predict(text_vectorized)[0]
        probabilities = model.predict_proba(text_vectorized)[0]
        
        # Décodage du label
        label = label_encoder.inverse_transform([prediction])[0]
        confidence = float(max(probabilities))
        
        # Probabilités pour toutes les classes
        prob_dict = {
            label_encoder.inverse_transform([i])[0]: float(prob)
            for i, prob in enumerate(probabilities)
        }
        
        # Métriques
        PREDICTION_COUNT.labels(model_type=model_type).inc()
        
        logger.info(
            "Prédiction effectuée",
            extra={
                'extra_fields': {
                    'prediction': label,
                    'confidence': confidence,
                    'text_length': len(document.text)
                }
            }
        )
        
        return PredictionResponse(
            prediction=label,
            confidence=confidence,
            probabilities=prob_dict
        )
    
    except ValueError as e:
        PREDICTION_ERRORS.labels(error_type="validation_error").inc()
        logger.warning(f"Erreur de validation: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur de validation: {str(e)}")
    except Exception as e:
        PREDICTION_ERRORS.labels(error_type="prediction_error").inc()
        logger.error(f"Erreur lors de la prédiction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(documents: BatchDocumentInput):
    """
    Prédiction pour plusieurs documents
    
    Args:
        documents: Liste de documents à classifier
    
    Returns:
        Liste de prédictions avec confiance et probabilités
    """
    if model is None or vectorizer is None or label_encoder is None:
        PREDICTION_ERRORS.labels(error_type="model_not_loaded").inc()
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé. Veuillez entraîner un modèle d'abord."
        )
    
    try:
        # Preprocessing
        texts_vectorized = vectorizer.transform(documents.texts)
        
        # Prédictions
        predictions = model.predict(texts_vectorized)
        probabilities = model.predict_proba(texts_vectorized)
        
        # Décodage
        results = []
        for pred, probs in zip(predictions, probabilities):
            label = label_encoder.inverse_transform([pred])[0]
            confidence = float(max(probs))
            prob_dict = {
                label_encoder.inverse_transform([i])[0]: float(prob)
                for i, prob in enumerate(probs)
            }
            results.append(
                PredictionResponse(
                    prediction=label,
                    confidence=confidence,
                    probabilities=prob_dict
                )
            )
        
        # Métriques
        PREDICTION_COUNT.labels(model_type=model_type).inc(len(documents.texts))
        
        logger.info(
            f"Batch prédiction effectuée pour {len(documents.texts)} documents",
            extra={'extra_fields': {'batch_size': len(documents.texts)}}
        )
        
        return BatchPredictionResponse(
            predictions=results,
            total=len(results)
        )
    
    except ValueError as e:
        PREDICTION_ERRORS.labels(error_type="validation_error").inc()
        logger.warning(f"Erreur de validation: {e}")
        raise HTTPException(status_code=400, detail=f"Erreur de validation: {str(e)}")
    except Exception as e:
        PREDICTION_ERRORS.labels(error_type="prediction_error").inc()
        logger.error(f"Erreur lors de la prédiction batch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction: {str(e)}")


@app.get("/metrics")
async def metrics():
    """
    Endpoint Prometheus pour les métriques
    """
    return Response(content=generate_latest(), media_type="text/plain")


@app.get("/model/info")
async def model_info():
    """Informations sur le modèle chargé"""
    if model is None:
        raise HTTPException(status_code=404, detail="Aucun modèle chargé")
    
    return {
        "model_type": model_type,
        "model_loaded": True,
        "classes": label_encoder.classes_.tolist() if label_encoder else None,
        "n_features": vectorizer.get_feature_names_out().shape[0] if vectorizer else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=api_config.get('host', '0.0.0.0'),
        port=api_config.get('port', 8000),
        reload=api_config.get('reload', False)
    )

