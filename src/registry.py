"""Accès au Model Registry MLflow.

Promotion par alias (`@champion`) et non par stages, dépréciés depuis MLflow 2.9.
Chaque version porte son profil de référence (`reference_profile.json`) et ses
métriques holdout dans le run qui l'a produite.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import mlflow
from mlflow.exceptions import MlflowException
from mlflow.tracking import MlflowClient

from config import get_config

CHAMPION = "champion"
PROFILE_FILE = "reference_profile.json"


def model_name() -> str:
    return get_config()["model"]["name"]


def setup_mlflow() -> MlflowClient:
    cfg = get_config()["mlflow"]
    uri = cfg["tracking_uri"]
    if uri.startswith("sqlite:///"):
        Path(uri.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment(cfg["experiment_name"])
    return MlflowClient()


@dataclass
class LoadedModel:
    model: Any
    version: str
    run_id: str
    profile: dict
    holdout: dict  # métriques du run d'entraînement : f1_macro, accuracy, ...


def champion_version(client: MlflowClient) -> str | None:
    try:
        # str : le store SQLite renvoie un int, le serveur REST une str.
        return str(client.get_model_version_by_alias(model_name(), CHAMPION).version)
    except MlflowException:
        return None


def version_of_run(client: MlflowClient, run_id: str) -> str:
    versions = client.search_model_versions(f"name='{model_name()}' and run_id='{run_id}'")
    if not versions:
        raise RuntimeError(f"aucune version enregistrée pour le run {run_id}")
    return str(versions[0].version)


def promote(client: MlflowClient, version: str) -> None:
    client.set_registered_model_alias(model_name(), CHAMPION, version)


def load_version(client: MlflowClient, version: str) -> LoadedModel:
    mv = client.get_model_version(model_name(), version)
    model = mlflow.sklearn.load_model(f"models:/{model_name()}/{version}")
    profile = mlflow.artifacts.load_dict(f"runs:/{mv.run_id}/{PROFILE_FILE}")
    run = client.get_run(mv.run_id)
    return LoadedModel(
        model=model,
        version=str(version),
        run_id=mv.run_id,
        profile=profile,
        holdout={
            k.removeprefix("holdout_"): v
            for k, v in run.data.metrics.items()
            if k.startswith("holdout_")
        },
    )


def load_champion(client: MlflowClient) -> LoadedModel | None:
    version = champion_version(client)
    return load_version(client, version) if version else None
