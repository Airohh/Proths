"""Retrain : données de base + labels de feedback, puis duel sur le holdout.

Les labels utilisés sont les VRAIS labels renvoyés par /feedback, jamais les
prédictions du modèle (réentraîner sur ses propres prédictions ne fait que
renforcer ses erreurs).
"""

import pandas as pd
from mlflow.tracking import MlflowClient

from config import get_config
from src import data
from src.inference.store import PredictionStore
from src.training.train import TrainingResult, train_and_register


def build_training_set(base: pd.DataFrame, feedback: pd.DataFrame) -> pd.DataFrame:
    """Base + feedback labellisé, dédoublonné sur le texte (le feedback l'emporte)."""
    labeled = feedback.rename(columns={"true_label": "label"})[["text", "label"]]
    combined = pd.concat([base[["text", "label"]], labeled], ignore_index=True)
    return combined.drop_duplicates(subset="text", keep="last").reset_index(drop=True)


def retrain(
    trigger: str,
    *,
    client: MlflowClient,
    store: PredictionStore,
    model_type: str | None = None,
) -> TrainingResult:
    cfg = get_config()
    feedback = store.labeled()
    train_df = build_training_set(data.load("train"), feedback)
    return train_and_register(
        train_df,
        data.load("holdout"),
        client=client,
        model_type=model_type or cfg["model"]["type"],
        trigger=trigger,
        extra_params={"n_feedback": len(feedback)},
        seed=int(cfg["data"]["seed"]),
    )
