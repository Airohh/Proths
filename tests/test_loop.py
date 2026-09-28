"""Boucle complète : champion -> trafic biaisé + feedback -> drift -> retrain -> décision."""

import pytest
from fastapi.testclient import TestClient

from scripts.simulate_traffic import run_traffic
from src import data, registry
from src.inference import api
from src.inference.store import PredictionStore
from src.monitoring.monitor import Monitor
from src.training.train import train_and_register


@pytest.fixture
def setup(workspace, monkeypatch):
    monkeypatch.setattr(api, "service", api.ModelService())
    client = registry.setup_mlflow()
    # Démarrage à froid : champion entraîné sur peu d'exemples.
    train_and_register(data.load("train").head(40), data.load("holdout"), client=client)
    with TestClient(api.app) as http:
        yield http, Monitor(PredictionStore(), client)


def test_balanced_traffic_triggers_nothing(setup):
    http, monitor = setup
    run_traffic(http, data.load("stream"), n=300, feedback=0.0)
    status = monitor.step()
    assert status["drift"]["n"] == 300
    assert not status["drift"]["drift"]
    assert status["trigger"] is None
    assert status["retrain"] is None


def test_skewed_traffic_triggers_a_retrain_on_true_labels(setup):
    http, monitor = setup
    stats = run_traffic(http, data.load("stream"), n=300, skew="Sports", ratio=0.8, feedback=1.0)
    assert stats["labeled"] == 300

    status = monitor.step()
    assert status["drift"]["drift"]
    assert status["trigger"] == "drift"
    retrain = status["retrain"]
    assert retrain["decision"] in {"promoted", "rejected"}
    assert retrain["champion_f1"] is not None

    run = registry.setup_mlflow().get_run(
        registry.setup_mlflow().get_model_version(registry.model_name(), retrain["version"]).run_id
    )
    assert run.data.params["n_feedback"] == "300"
    assert run.data.tags["trigger"] == "drift"


def test_drift_waits_for_enough_new_labels(setup):
    http, monitor = setup
    run_traffic(http, data.load("stream"), n=300, skew="Sports", ratio=0.8, feedback=0.1)
    status = monitor.step()
    assert status["trigger"] == "drift"
    assert status["retrain"] is None
    assert "nouveaux labels" in status["waiting"]


def test_empty_window_exports_no_verdict_instead_of_zero(setup):
    """Juste après une promotion, la fenêtre du nouveau champion est vide : NaN, pas « stable »."""
    import math

    from prometheus_client import REGISTRY

    _, monitor = setup
    status = monitor.step()
    assert status["drift"]["n"] == 0
    assert math.isnan(REGISTRY.get_sample_value("drift_psi"))
    assert math.isnan(REGISTRY.get_sample_value("drift_detected"))
