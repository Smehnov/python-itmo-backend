import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.app.core.database import Base, get_db
from src.app.services.kafka_producer import MessageProducer
from src.app.services.document import DocumentService
from src.app.models.document import Document
from src.app.core.config import settings
from src.app.main import app
import pytest_asyncio
import os
from fastapi.testclient import TestClient
from tests.utils import TestConsumerService
from prometheus_client import REGISTRY

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session", autouse=True)
def override_settings():
    """Override settings for testing"""
    from src.app.core.config import settings
    settings.DATABASE_URL = SQLALCHEMY_DATABASE_URL
    return settings

@pytest.fixture(scope="session")
def engine():
    """Create test database engine"""
    if os.path.exists("./test.db"):
        os.remove("./test.db")
        
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture
def db_session(engine):
    """Create database session"""
    connection = engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    
    # Override the get_db dependency for all tests
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    # Cleanup
    app.dependency_overrides.clear()
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """Create test client"""
    yield TestClient(app)

@pytest_asyncio.fixture
async def async_client(db_session):
    """Create async test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

class MockProducer:
    def __init__(self):
        self.messages = []
        
    def send_message(self, message):
        self.messages.append(message)

@pytest.fixture
def mock_kafka_producer():
    return MockProducer()

@pytest.fixture(autouse=True)
def mock_kafka_producer_dependency(monkeypatch, mock_kafka_producer):
    """Override Kafka producer in routes"""
    def mock_producer():
        return mock_kafka_producer
    
    from src.app.api.routes import documents
    monkeypatch.setattr(documents, "MessageProducer", mock_producer)

@pytest.fixture
def document_service(db_session, mock_kafka_producer):
    """Create document service with synchronous processing"""
    service = DocumentService(db_session, mock_kafka_producer)
    service._test_mode = True  # Enable test mode
    return service

@pytest.fixture
def sample_document():
    return {
        "title": "Test Document",
        "content": "This is a test document content"
    }

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def clean_db(engine):
    """Clean database between tests"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield 

@pytest.fixture(autouse=True)
def clear_metrics():
    """Clear all metrics before each test"""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    yield