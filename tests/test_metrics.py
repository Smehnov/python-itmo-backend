import pytest
from fastapi.testclient import TestClient
from prometheus_client import CONTENT_TYPE_LATEST

from src.app.main import app

client = TestClient(app)

def test_metrics_endpoint():
    # Just test that metrics endpoint is accessible
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == CONTENT_TYPE_LATEST 