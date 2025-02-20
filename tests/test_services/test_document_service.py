import pytest
from unittest.mock import Mock, patch
from src.app.services.document import DocumentService
from src.app.schemas.document import DocumentCreate, DocumentUpdate
from src.app.core.metrics import DOCUMENTS_PROCESSED, KAFKA_MESSAGES_SENT

@pytest.fixture
def mock_producer():
    producer = Mock()
    producer.messages = []  # Add messages list
    producer.send_message = Mock(side_effect=lambda msg: producer.messages.append(msg))
    return producer

@pytest.fixture
def document_service(db_session, mock_producer):
    return DocumentService(db_session, mock_producer)

def test_create_document(document_service, sample_document):
    doc = DocumentCreate(**sample_document)
    db_doc = document_service.create(doc)
    
    assert db_doc.title == sample_document["title"]
    assert db_doc.content == sample_document["content"]
    # Test with actual word and character counts
    assert db_doc.short_description == "Document contains 6 words and 31 characters"
    
    # Verify Kafka message was sent
    assert len(document_service.producer.messages) == 1
    message = document_service.producer.messages[0]
    assert message["document_id"] == db_doc.id
    assert message["content"] == db_doc.content

def test_get_document(document_service, sample_document):
    # Create document
    doc = DocumentCreate(**sample_document)
    created_doc = document_service.create(doc)
    
    # Get it back
    retrieved_doc = document_service.get(created_doc.id)
    assert retrieved_doc is not None
    assert retrieved_doc.title == sample_document["title"]
    assert retrieved_doc.id == created_doc.id

def test_get_nonexistent_document(document_service):
    assert document_service.get(999) is None

def test_list_documents(document_service, clean_db):
    # Create multiple documents
    doc1 = DocumentCreate(
        title="First Document",
        content="First content"
    )
    doc2 = DocumentCreate(
        title="Second Document",
        content="Second content"
    )

    document_service.create(doc1)
    document_service.create(doc2)

    docs = document_service.list(skip=0, limit=10)
    assert len(docs) == 2
    assert docs[0].title == "First Document"
    assert docs[1].title == "Second Document"

def test_update_document(document_service, sample_document):
    # Create document
    doc = DocumentCreate(**sample_document)
    created_doc = document_service.create(doc)
    
    # Update it
    update_data = DocumentUpdate(title="Updated Title")
    updated_doc = document_service.update(created_doc.id, update_data)
    
    assert updated_doc is not None
    assert updated_doc.title == "Updated Title"
    assert updated_doc.content == sample_document["content"]

def test_remove_document(document_service, sample_document):
    # Create document
    doc = DocumentCreate(**sample_document)
    created_doc = document_service.create(doc)
    
    # Remove it
    result = document_service.remove(created_doc.id)
    assert result is True
    
    # Verify it's gone
    assert document_service.get(created_doc.id) is None

def test_create_document_with_minimum_content(document_service):
    doc = DocumentCreate(title="Short", content="Test")
    db_doc = document_service.create(doc)
    assert db_doc.title == "Short"
    assert db_doc.content == "Test"

def test_list_documents_pagination(document_service, clean_db):
    # Create 5 documents
    for i in range(5):
        doc = DocumentCreate(
            title=f"Document {i}",
            content=f"Content {i}"
        )
        document_service.create(doc)

    # Test pagination
    first_page = document_service.list(skip=0, limit=2)
    assert len(first_page) == 2
    assert first_page[0].title == "Document 0"
    assert first_page[1].title == "Document 1"

def test_update_nonexistent_document(db_session):
    service = DocumentService(db_session, Mock())
    result = service.update(999, DocumentUpdate(title="New Title", content="New Content"))
    assert result is None

def test_update_with_partial_data(document_service, sample_document):
    # Create document
    doc = DocumentCreate(**sample_document)
    created_doc = document_service.create(doc)
    
    # Update only title
    update_data = DocumentUpdate(title="New Title")
    updated_doc = document_service.update(created_doc.id, update_data)
    assert updated_doc.title == "New Title"
    assert updated_doc.content == sample_document["content"]
    
    # Update only content
    update_data = DocumentUpdate(content="New Content")
    updated_doc = document_service.update(created_doc.id, update_data)
    assert updated_doc.title == "New Title"  # Still has the previously updated title
    assert updated_doc.content == "New Content"

def test_remove_nonexistent_document(db_session):
    service = DocumentService(db_session, Mock())
    result = service.remove(999)
    assert result is False

def test_get_nonexistent_document(db_session):
    service = DocumentService(db_session, Mock())
    result = service.get(999)
    assert result is None

def test_create_document_with_metrics(db_session, mock_producer):
    service = DocumentService(db_session, mock_producer)
    
    doc_data = DocumentCreate(title="Test", content="Test content")
    result = service.create(doc_data)
    
    assert result.title == "Test"
    mock_producer.send_message.assert_called_once() 