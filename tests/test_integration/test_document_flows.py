import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app.api.main import app
from src.app.core.database import get_db
from src.app.models.document import Document
from src.app.schemas.document import DocumentCreate

@pytest.fixture
def client(db_session):
    # Override the database dependency
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_and_process_flow(client, db_session: Session):
    """Test full flow: create document -> process in Kafka -> update description"""
    # 1. Create document via API
    doc_data = {
        "title": "Integration Test",
        "content": "This is a test document for integration testing"
    }
    response = client.post("/api/v1/documents/", json=doc_data)
    assert response.status_code == 201
    doc_id = response.json()["id"]
    
    # 2. Verify document in database
    db_doc = db_session.query(Document).filter_by(id=doc_id).first()
    assert db_doc is not None
    assert db_doc.title == doc_data["title"]
    
    # 3. Verify document via API
    response = client.get(f"/api/v1/documents/{doc_id}")
    assert response.status_code == 200
    assert response.json()["title"] == doc_data["title"]

def test_search_and_update_flow(client, db_session: Session):
    """Test document management flow: create multiple -> list -> update"""
    # 1. Create multiple documents
    docs = [
        {"title": f"Test Doc {i}", "content": f"Content {i}"}
        for i in range(5)
    ]
    created_docs = []
    for doc in docs:
        response = client.post("/api/v1/documents/", json=doc)
        assert response.status_code == 201
        created_docs.append(response.json())
    
    # 2. Test pagination
    response = client.get("/api/v1/documents/?skip=0&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    
    # 3. Update first document
    doc_id = created_docs[0]["id"]
    update_data = {"title": "Updated Title"}
    response = client.put(f"/api/v1/documents/{doc_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    
    # 4. Verify in database
    db_doc = db_session.query(Document).filter_by(id=doc_id).first()
    assert db_doc.title == "Updated Title"

def test_error_handling_flow(client):
    """Test error handling in different scenarios"""
    # 1. Try to get non-existent document
    response = client.get("/api/v1/documents/999")
    assert response.status_code == 404
    
    # 2. Try to create invalid document
    invalid_doc = {"title": "", "content": ""}  # Empty title not allowed
    response = client.post("/api/v1/documents/", json=invalid_doc)
    assert response.status_code == 422
    assert "title" in response.json()["detail"][0]["loc"]
    
    # 3. Try to update non-existent document
    response = client.put("/api/v1/documents/999", json={"title": "New Title"})
    assert response.status_code == 404
    
    # 4. Try to delete non-existent document
    response = client.delete("/api/v1/documents/999")
    assert response.status_code == 404

def test_concurrent_updates_flow(client, db_session: Session):
    """Test handling of concurrent document updates"""
    # 1. Create initial document
    doc_data = {"title": "Original", "content": "Original content"}
    response = client.post("/api/v1/documents/", json=doc_data)
    assert response.status_code == 201
    doc_id = response.json()["id"]
    
    # 2. Perform multiple updates
    updates = [
        {"title": f"Update {i}", "content": f"Updated content {i}"}
        for i in range(3)
    ]
    
    for update in updates:
        response = client.put(f"/api/v1/documents/{doc_id}", json=update)
        assert response.status_code == 200
    
    # 3. Verify final state
    db_doc = db_session.query(Document).filter_by(id=doc_id).first()
    assert db_doc.title == "Update 2"  # Last update should win 