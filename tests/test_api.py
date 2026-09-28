import pytest
from fastapi.testclient import TestClient

from src import data, registry
from src.inference import api
from src.training.train import train_and_register


@pytest.fixture
def client(workspace, monkeypatch):
    monkeypatch.setattr(api, "service", api.ModelService())
    mlflow_client = registry.setup_mlflow()
    train_and_register(data.load("train"), data.load("holdout"), client=mlflow_client)
    with TestClient(api.app) as test_client:
        yield test_client


def test_health_without_model(workspace, monkeypatch):
    monkeypatch.setattr(api, "service", api.ModelService())
    with TestClient(api.app) as test_client:
        response = test_client.get("/health")
        assert response.status_code == 503
        assert test_client.post("/predict", json={"text": "hello"}).status_code == 503


def test_predict_then_feedback(client):
    response = client.post("/predict", json={"text": "Striker scores late goal in playoff match"})
    assert response.status_code == 200
    body = response.json()
    assert body["prediction"] == "Sports"
    assert body["model_version"] == "1"
    assert set(body["probabilities"]) == {"World", "Sports", "Business", "Sci/Tech"}

    fb = client.post("/feedback", json={"prediction_id": body["prediction_id"], "label": "Sports"})
    assert fb.json() == {"prediction_id": body["prediction_id"], "correct": True}

    assert (
        client.post("/feedback", json={"prediction_id": "nope", "label": "Sports"}).status_code
        == 404
    )
    bad = client.post(
        "/feedback", json={"prediction_id": body["prediction_id"], "label": "Cooking"}
    )
    assert bad.status_code == 422


def test_batch_and_validation(client):
    response = client.post("/predict/batch", json={"texts": ["nasa space chip", "bank shares"]})
    assert response.json()["total"] == 2
    assert client.post("/predict", json={"text": "   "}).status_code == 422
    assert client.post("/predict/batch", json={"texts": []}).status_code == 422


def test_reload_picks_up_a_new_champion(client):
    mlflow_client = registry.setup_mlflow()
    result = train_and_register(
        data.load("train"), data.load("holdout"), client=mlflow_client, min_improvement=-1.0
    )
    assert result.promoted
    assert client.get("/model/info").json()["version"] == "1"
    assert api.service.refresh_if_changed()
    assert client.get("/model/info").json()["version"] == "2"
    assert client.post("/model/reload").json()["version"] == "2"


def test_unchanged_champion_is_not_reloaded(client):
    assert not api.service.refresh_if_changed()
    assert not api.service.refresh_if_changed()


def test_metrics_exposed(client):
    client.post("/predict", json={"text": "election minister summit"})
    text = client.get("/metrics").text
    assert "predictions_total" in text
    assert "prediction_confidence_bucket" in text
    assert "model_version" in text
