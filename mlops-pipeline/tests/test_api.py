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
    """Test du endpoint health"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "model_loaded" in response.json()

