import pytest
from sqlalchemy.orm import Session
from src.app.schemas.document import DocumentCreate, DocumentUpdate
from src.app.services.document import DocumentService
from src.app.models.document import Document
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.core.database import Base
import os

def test_document_creation_flow(db_session: Session, document_service: DocumentService):
    # Create a document
    doc = DocumentCreate(
        title="Integration Test",
        content="Testing the full flow"
    )
    
    # Save it using the service
    db_doc = document_service.create(doc)
    assert db_doc.id is not None
    assert db_doc.title == doc.title
    assert db_doc.content == doc.content

def test_document_update_flow(db_session: Session, document_service: DocumentService):
    # Create and save a document
    doc = DocumentCreate(
        title="Original Title",
        content="Original content"
    )
    db_doc = document_service.create(doc)
    
    # Update the document
    update_data = DocumentUpdate(title="Updated Title")
    updated_doc = document_service.update(db_doc.id, update_data)
    
    assert updated_doc.title == "Updated Title"
    assert updated_doc.content == "Original content"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture
def test_db(test_engine):
    SessionLocal = sessionmaker(bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close() 