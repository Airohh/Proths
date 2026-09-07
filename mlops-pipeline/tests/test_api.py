"""
Tests pour l'API
"""
import pytest
from fastapi.testclient import TestClient
from src.inference.api import app

client = TestClient(app)


def test_root():
    """Test du endpoint root"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health():
    """Health: 200 si modèle chargé, 503 sinon (CI sans train)."""
    response = client.get("/health")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "model_loaded" in body

