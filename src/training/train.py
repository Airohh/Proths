"""Entraînement d'un candidat, duel avec le champion sur le holdout, promotion éventuelle.

Utilisé à la fois pour le premier entraînement (`make train`) et par la boucle de
retrain (src/retraining/retrain.py) : une seule règle de promotion dans tout le projet.

    python -m src.training.train --model-type logreg --train-size 20000 --min-f1 0.85
"""

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.tracking import MlflowClient

from config import get_config
from src import data, registry
from src.training.evaluate import evaluate, reference_profile
from src.training.pipeline import MODEL_TYPES, build_pipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Dépendances du modèle servi : évite l'inférence (lente) faite par MLflow à chaque log.
MODEL_REQUIREMENTS = ["scikit-learn==1.3.2", "scipy==1.11.4", "numpy==1.24.3", "pandas==2.1.3"]


@dataclass
class TrainingResult:
    version: str
    run_id: str
    model_type: str
    n_train: int
    candidate: dict
    champion_version: str | None
    champion: dict | None
    promoted: bool
    reason: str


def decide_promotion(
    champion_f1: float | None, candidate_f1: float, min_improvement: float
) -> tuple[bool, str]:
    """Le candidat remplace le champion s'il gagne au moins `min_improvement` de F1 macro,
    mesuré sur le MÊME holdout, dans le MÊME run."""
    if champion_f1 is None:
        return True, "premier modèle : pas de champion"
    delta = candidate_f1 - champion_f1
    if delta >= min_improvement:
        return True, f"F1 macro {delta:+.4f} (seuil +{min_improvement})"
    return False, f"F1 macro {delta:+.4f} < seuil +{min_improvement}"


def train_and_register(
    train_df: pd.DataFrame,
    holdout_df: pd.DataFrame,
    *,
    client: MlflowClient,
    model_type: str = "logreg",
    trigger: str = "manual",
    extra_params: dict | None = None,
    min_improvement: float | None = None,
    seed: int = 42,
) -> TrainingResult:
    if min_improvement is None:
        min_improvement = float(get_config()["retrain"]["min_improvement"])

    champion = registry.load_champion(client)

    pipeline = build_pipeline(model_type, seed)
    started = time.perf_counter()
    pipeline.fit(train_df["text"], train_df["label"])
    fit_seconds = time.perf_counter() - started

    candidate = evaluate(pipeline, holdout_df)
    champion_metrics = evaluate(champion.model, holdout_df) if champion else None
    promoted, reason = decide_promotion(
        champion_metrics["f1_macro"] if champion_metrics else None,
        candidate["f1_macro"],
        min_improvement,
    )

    with mlflow.start_run(run_name=f"{trigger}-{model_type}") as run:
        mlflow.set_tags(
            {
                "kind": "training",
                "trigger": trigger,
                "decision": "promoted" if promoted else "rejected",
            }
        )
        mlflow.log_params(
            {
                "model_type": model_type,
                "n_train": len(train_df),
                "n_holdout": len(holdout_df),
                "seed": seed,
                "champion_version": champion.version if champion else "none",
                "min_improvement": min_improvement,
                **(extra_params or {}),
            }
        )
        mlflow.log_metrics({f"holdout_{k}": v for k, v in candidate.items()})
        if champion_metrics:
            mlflow.log_metrics({f"champion_holdout_{k}": v for k, v in champion_metrics.items()})
            mlflow.log_metric(
                "delta_f1_macro", candidate["f1_macro"] - champion_metrics["f1_macro"]
            )
        mlflow.log_metric("fit_seconds", fit_seconds)
        mlflow.log_dict(reference_profile(pipeline, holdout_df, seed=seed), registry.PROFILE_FILE)
        mlflow.sklearn.log_model(
            pipeline,
            "model",
            registered_model_name=registry.model_name(),
            pip_requirements=MODEL_REQUIREMENTS,
        )
        run_id = run.info.run_id

    version = registry.version_of_run(client, run_id)
    client.set_model_version_tag(registry.model_name(), version, "decision", reason)
    if promoted:
        registry.promote(client, version)

    result = TrainingResult(
        version=version,
        run_id=run_id,
        model_type=model_type,
        n_train=len(train_df),
        candidate=candidate,
        champion_version=champion.version if champion else None,
        champion=champion_metrics,
        promoted=promoted,
        reason=reason,
    )
    logger.info(
        "promotion" if promoted else "candidat rejeté",
        extra={"extra_fields": {"version": version, "reason": reason, "trigger": trigger}},
    )
    return result


def main(argv: list[str] | None = None) -> int:
    cfg = get_config()
    parser = argparse.ArgumentParser(description="Entraîne un candidat et le compare au champion")
    parser.add_argument("--model-type", default=cfg["model"]["type"], choices=MODEL_TYPES)
    parser.add_argument("--train-size", type=int, default=None, help="sous-échantillon stratifié")
    parser.add_argument("--min-f1", type=float, default=None, help="échoue si F1 holdout < seuil")
    parser.add_argument("--metrics-out", default="reports/metrics.json")
    args = parser.parse_args(argv)

    seed = int(cfg["data"]["seed"])
    train_df = data.stratified_sample(data.load("train"), args.train_size, seed)
    holdout_df = data.load("holdout")
    client = registry.setup_mlflow()

    result = train_and_register(
        train_df, holdout_df, client=client, model_type=args.model_type, trigger="manual", seed=seed
    )

    out = Path(args.metrics_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    print(
        f"version {result.version} | F1 macro holdout {result.candidate['f1_macro']:.4f} | "
        f"{'PROMU' if result.promoted else 'rejeté'} ({result.reason})"
    )

    if args.min_f1 is not None and result.candidate["f1_macro"] < args.min_f1:
        print(f"ÉCHEC gate qualité : F1 {result.candidate['f1_macro']:.4f} < {args.min_f1}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
