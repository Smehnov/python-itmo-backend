from fastapi.testclient import TestClient
from src.app.main import app
from unittest.mock import patch

client = TestClient(app)

def test_create_document():
    doc_data = {"title": "Test", "content": "Test content"}
    response = client.post("/api/v1/documents/", json=doc_data)
    assert response.status_code == 201
    assert "id" in response.json()

def test_error_handling():
    with patch('src.app.services.document.DocumentService.create') as mock_create:
        mock_create.side_effect = Exception("Test error")
        response = client.post("/api/v1/documents/", json={"title": "Test", "content": "Test"})
        assert response.status_code == 500
        assert response.json()["detail"] == "Internal Server Error"