"""Compare les classifieurs sur le même train et le même holdout.

Écrit reports/model_comparison.{json,md} et logge chaque essai dans l'expérience
MLflow `model-selection` (sans rien enregistrer dans le registry).

    python scripts/compare_models.py                  # tout le train (120k)
    python scripts/compare_models.py --train-size 4000
"""

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mlflow  # noqa: E402

from config import get_config  # noqa: E402
from src import data, registry  # noqa: E402
from src.training.evaluate import evaluate  # noqa: E402
from src.training.pipeline import MODEL_TYPES, build_pipeline  # noqa: E402

warnings.filterwarnings("ignore")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-size", type=int, default=None)
    parser.add_argument("--models", nargs="+", default=list(MODEL_TYPES), choices=MODEL_TYPES)
    parser.add_argument("--out", default="reports/model_comparison")
    args = parser.parse_args()

    seed = int(get_config()["data"]["seed"])
    train_df = data.stratified_sample(data.load("train"), args.train_size, seed)
    holdout_df = data.load("holdout")
    registry.setup_mlflow()
    mlflow.set_experiment("model-selection")

    rows = []
    for model_type in args.models:
        pipeline = build_pipeline(model_type, seed)
        started = time.perf_counter()
        pipeline.fit(train_df["text"], train_df["label"])
        fit_s = time.perf_counter() - started

        started = time.perf_counter()
        metrics = evaluate(pipeline, holdout_df)
        ms_per_doc = (time.perf_counter() - started) / len(holdout_df) * 1000

        row = {
            "model": model_type,
            "n_train": len(train_df),
            "accuracy": round(metrics["accuracy"], 4),
            "f1_macro": round(metrics["f1_macro"], 4),
            "fit_seconds": round(fit_s, 1),
            "ms_per_doc": round(ms_per_doc, 3),
        }
        rows.append(row)
        with mlflow.start_run(run_name=f"compare-{model_type}-{len(train_df)}"):
            mlflow.log_params({"model_type": model_type, "n_train": len(train_df)})
            mlflow.log_metrics({f"holdout_{k}": v for k, v in metrics.items()})
            mlflow.log_metrics({"fit_seconds": fit_s, "ms_per_doc": ms_per_doc})
        print(row, flush=True)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    lines = [
        f"Train : {len(train_df)} articles · holdout : {len(holdout_df)} articles (AG News)\n",
        "| Modèle | Accuracy | F1 macro | Fit (s) | Inférence (ms/doc) |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(rows, key=lambda r: -r["f1_macro"]):
        lines.append(
            f"| {r['model']} | {r['accuracy']:.4f} | {r['f1_macro']:.4f} | "
            f"{r['fit_seconds']} | {r['ms_per_doc']} |"
        )
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
