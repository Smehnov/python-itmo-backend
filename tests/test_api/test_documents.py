from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.api.main import app
from src.app.core.database import get_db
from src.app.schemas.document import DocumentCreate

# Override the database dependency
def override_get_db(db_session: Session):
    try:
        yield db_session
    finally:
        pass

@pytest.fixture
def client(db_session):
    # Override the dependency
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    # Clear the override after the test
    app.dependency_overrides.clear()

def test_create_document(client, sample_document):
    response = client.post("/api/v1/documents/", json=sample_document)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_document["title"]
    assert data["content"] == sample_document["content"]
    assert data["short_description"] is not None
    assert "Document contains" in data["short_description"]
    assert isinstance(data["id"], int)  # Changed from UUID to int

def test_get_document(client, sample_document):
    # First create a document
    create_response = client.post("/api/v1/documents/", json=sample_document)
    doc_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == sample_document["title"]
    assert data["id"] == doc_id

def test_get_nonexistent_document(client):
    response = client.get("/api/v1/documents/999")  # Changed from UUID to int
    assert response.status_code == 404

def test_list_documents(client, sample_document):
    # Create multiple documents
    client.post("/api/v1/documents/", json=sample_document)
    client.post("/api/v1/documents/", json={
        "title": "Second Document",
        "content": "Another content"
    })
    
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(isinstance(doc["id"], int) for doc in data)  # Changed from UUID to int

def test_update_document(client, sample_document):
    # Create document
    create_response = client.post("/api/v1/documents/", json=sample_document)
    doc_id = create_response.json()["id"]
    
    # Update it
    update_data = {"title": "Updated Title"}
    response = client.put(f"/api/v1/documents/{doc_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == sample_document["content"]

def test_delete_document(client, sample_document):
    # Create document
    create_response = client.post("/api/v1/documents/", json=sample_document)
    doc_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/v1/documents/{doc_id}")
    assert get_response.status_code == 404 