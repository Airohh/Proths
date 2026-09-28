"""Service de monitoring : drift, précision live, déclenchement du retrain.

    python -m src.monitoring.monitor                 # boucle + /metrics sur :8001
    python -m src.monitoring.monitor --once          # un seul passage (cron, CI, démo)
    python -m src.monitoring.monitor --once --force  # retrain immédiat

À chaque passage :
1. drift entre les N dernières prédictions du champion et son profil de référence ;
2. précision live sur les prédictions du champion qui ont reçu un vrai label ;
3. si drift ou chute de précision, ET assez de nouveaux labels, ET cooldown écoulé :
   retrain -> duel sur le holdout -> promotion éventuelle -> l'API recharge.

Le dernier entraînement est lu dans MLflow : le service est sans état et peut
redémarrer à tout moment.
"""

import argparse
import time

import httpx
import mlflow
from mlflow.tracking import MlflowClient
from prometheus_client import Counter, Gauge, start_http_server

from config import get_config
from src import registry
from src.inference.store import PredictionStore
from src.monitoring.drift import detect_drift
from src.retraining.retrain import retrain
from src.utils.logger import get_logger

logger = get_logger(__name__)

DRIFT_PSI = Gauge("drift_psi", "PSI de la répartition des classes prédites")
DRIFT_KS = Gauge("drift_ks_stat", "KS de la confiance vs référence")
DRIFT_CHI2_P = Gauge("drift_chi2_pvalue", "p-value chi² des classes prédites")
DRIFT_DETECTED = Gauge("drift_detected", "1 si drift détecté")
WINDOW_SIZE = Gauge("drift_window_size", "Prédictions dans la fenêtre analysée")
MEAN_CONFIDENCE = Gauge("prediction_mean_confidence", "Confiance moyenne sur la fenêtre")
CLASS_SHARE = Gauge("prediction_class_share", "Part de chaque classe prédite", ["label"])
LIVE_ACCURACY = Gauge("live_accuracy", "Précision sur les prédictions labellisées (feedback)")
LIVE_LABELED = Gauge("live_labeled", "Prédictions du champion ayant reçu un label")
LABELS_SINCE_TRAINING = Gauge(
    "labels_since_training", "Labels reçus depuis le dernier entraînement"
)
CHAMPION_VERSION = Gauge("champion_version", "Version du champion")
CHAMPION_F1 = Gauge("champion_holdout_f1", "F1 macro holdout du champion")
CANDIDATE_F1 = Gauge("last_candidate_holdout_f1", "F1 macro holdout du dernier candidat")
RETRAINS = Counter("retrain_total", "Retrains exécutés", ["trigger", "decision"])


class Monitor:
    def __init__(self, store: PredictionStore, client: MlflowClient):
        self.store = store
        self.client = client
        self.cfg = get_config()
        self._champion: registry.LoadedModel | None = None

    def champion(self) -> registry.LoadedModel | None:
        version = registry.champion_version(self.client)
        if version is None:
            return None
        if self._champion is None or self._champion.version != version:
            self._champion = registry.load_version(self.client, version)
        return self._champion

    def last_training_ts(self) -> float | None:
        runs = mlflow.search_runs(
            experiment_names=[self.cfg["mlflow"]["experiment_name"]],
            filter_string="tags.kind = 'training'",
            order_by=["start_time DESC"],
            max_results=1,
        )
        return None if runs.empty else runs.iloc[0]["start_time"].timestamp()

    def live_accuracy(self, version: str) -> tuple[float | None, int]:
        labeled = self.store.labeled()
        labeled = labeled[labeled["model_version"] == version].tail(
            self.cfg["monitoring"]["window"]
        )
        if labeled.empty:
            return None, 0
        return float((labeled["predicted"] == labeled["true_label"]).mean()), len(labeled)

    def step(self, force: bool = False) -> dict:
        mon, rt = self.cfg["monitoring"], self.cfg["retrain"]
        champion = self.champion()
        if champion is None:
            logger.warning("pas de champion : lancer `make train`")
            return {"status": "no_champion"}

        recent = self.store.recent(int(mon["window"]), model_version=champion.version)
        report = detect_drift(
            champion.profile,
            recent["predicted"].tolist(),
            recent["confidence"].tolist(),
            psi_threshold=float(mon["psi_threshold"]),
            ks_threshold=float(mon["ks_threshold"]),
            min_samples=int(mon["min_samples"]),
        )
        accuracy, n_labeled = self.live_accuracy(champion.version)
        reference_accuracy = champion.holdout.get("accuracy")
        performance_drop = (
            accuracy is not None
            and reference_accuracy is not None
            and n_labeled >= int(mon["min_labeled"])
            and accuracy < reference_accuracy - float(mon["accuracy_drop"])
        )

        last_ts = self.last_training_ts()
        new_labels = len(self.store.labeled(since=last_ts))
        cooldown_over = last_ts is None or time.time() - last_ts >= float(rt["cooldown_seconds"])

        trigger = (
            "manual"
            if force
            else "drift"
            if report.drift
            else "performance"
            if performance_drop
            else None
        )
        ready = force or (new_labels >= int(rt["min_new_labels"]) and cooldown_over)
        status = {
            "champion_version": champion.version,
            "drift": report.to_dict(),
            "live_accuracy": accuracy,
            "live_labeled": n_labeled,
            "labels_since_training": new_labels,
            "trigger": trigger,
            "retrain": None,
        }

        if trigger and ready:
            result = retrain(trigger, client=self.client, store=self.store)
            decision = "promoted" if result.promoted else "rejected"
            RETRAINS.labels(trigger, decision).inc()
            CANDIDATE_F1.set(result.candidate["f1_macro"])
            status["retrain"] = {
                "version": result.version,
                "decision": decision,
                "reason": result.reason,
                "candidate_f1": result.candidate["f1_macro"],
                "champion_f1": result.champion["f1_macro"] if result.champion else None,
            }
            if result.promoted:
                self._notify_api()
                champion = self.champion()
        elif trigger:
            status["waiting"] = (
                "cooldown"
                if not cooldown_over
                else f"{new_labels}/{rt['min_new_labels']} nouveaux labels"
            )

        self._export(champion, report, accuracy, n_labeled, new_labels)
        logger.info("monitoring", extra={"extra_fields": status})
        return status

    def _export(self, champion, report, accuracy, n_labeled, new_labels) -> None:
        # NaN = « pas de verdict » (fenêtre vide, par ex. juste après une promotion) :
        # exporter 0 afficherait « stable » alors qu'on ne sait rien.
        nan = float("nan")
        has_data = report.n > 0
        DRIFT_PSI.set(report.psi if has_data else nan)
        DRIFT_KS.set(report.ks_stat if has_data else nan)
        DRIFT_CHI2_P.set(report.chi2_pvalue if has_data else nan)
        DRIFT_DETECTED.set(int(report.drift) if report.enough_data else nan)
        WINDOW_SIZE.set(report.n)
        MEAN_CONFIDENCE.set(report.mean_confidence if has_data else nan)
        for label in champion.profile["classes"]:
            CLASS_SHARE.labels(label).set(report.class_distribution.get(label, nan))
        LIVE_ACCURACY.set(accuracy if accuracy is not None else nan)
        LIVE_LABELED.set(n_labeled)
        LABELS_SINCE_TRAINING.set(new_labels)
        CHAMPION_VERSION.set(float(champion.version))
        CHAMPION_F1.set(champion.holdout.get("f1_macro", 0.0))

    def _notify_api(self) -> None:
        """Accélère la bascule ; sans réponse, l'API la fera seule au prochain poll."""
        url = self.cfg["api"]["reload_url"]
        try:
            httpx.post(url, timeout=10).raise_for_status()
        except Exception as exc:
            logger.info("API non notifiée", extra={"extra_fields": {"url": url, "error": str(exc)}})


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitoring drift + retrain")
    parser.add_argument("--once", action="store_true", help="un seul passage puis sortie")
    parser.add_argument("--force", action="store_true", help="retrain sans attendre de signal")
    parser.add_argument("--interval", type=float, default=None)
    args = parser.parse_args()

    cfg = get_config()["monitoring"]
    monitor = Monitor(PredictionStore(), registry.setup_mlflow())
    if args.once:
        monitor.step(force=args.force)
        return

    start_http_server(int(cfg["metrics_port"]))
    interval = args.interval or float(cfg["interval_seconds"])
    while True:
        try:
            monitor.step(force=args.force)
        except Exception:
            logger.error("passage de monitoring en échec", exc_info=True)
        args.force = False
        time.sleep(interval)


if __name__ == "__main__":
    main()
