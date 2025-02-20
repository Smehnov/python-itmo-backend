import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime
from consumer.kafka_consumer import MessageConsumer
from src.app.core.metrics import PROCESSING_SUCCESS, PROCESSING_FAILED
from src.app.models.document import Document

@pytest.fixture
def mock_kafka_consumer():
    with patch('consumer.kafka_consumer.KafkaConsumer') as mock:
        instance = Mock()
        # Configure all needed methods
        instance.__iter__ = Mock(return_value=iter([]))
        instance.subscribe = Mock()
        instance.close = Mock()
        mock.return_value = instance
        yield mock

@pytest.fixture
def consumer(mock_kafka_consumer, db_session):
    # Patch both Kafka and sessionmaker
    with patch('consumer.kafka_consumer.KafkaConsumer', mock_kafka_consumer), \
         patch('consumer.kafka_consumer.sessionmaker') as mock_sessionmaker:
        mock_sessionmaker.return_value = lambda: db_session
        consumer = MessageConsumer()
        # Store mock for later access
        consumer._consumer = mock_kafka_consumer.return_value
        return consumer

def test_consumer_initialization(mock_kafka_consumer):
    # Use the mock fixture and patch at the correct location
    with patch('consumer.kafka_consumer.KafkaConsumer', mock_kafka_consumer):
        consumer = MessageConsumer()
        assert consumer.running == True
        mock_kafka_consumer.assert_called_once()

def test_stop_consumer(consumer):
    consumer.stop(None, None)  # Signal handler requires two arguments
    assert consumer.running == False

def test_process_valid_message(consumer, db_session):
    # First create a document in the database
    doc = Document(id=1, title="Test", content="Test content")
    db_session.add(doc)
    db_session.commit()

    message = Mock()
    message.value = json.dumps({
        "document_id": 1,
        "content": "Test content"
    }).encode()

    consumer.process_message(message)

    # Verify through database changes
    doc = db_session.query(Document).filter(Document.id == 1).first()
    assert doc is not None
    assert doc.short_description is not None

def test_process_invalid_json(consumer):
    message = Mock()
    message.value = b'invalid json'
    
    # Reset metrics before test
    PROCESSING_FAILED._value.set(0)
    initial_failed = float(PROCESSING_FAILED._value.get())
    
    consumer.process_message(message)
    assert float(PROCESSING_FAILED._value.get()) == initial_failed + 1

@patch('consumer.kafka_consumer.logger')
def test_consume_messages(mock_logger, consumer, mock_kafka_consumer):
    # Create test message
    message = Mock()
    message.value = json.dumps({
        "id": 1,
        "title": "Test",
        "content": "test"
    }).encode()
    
    # Configure mock to return our message
    mock_kafka_consumer.return_value.__iter__.return_value = [message]
    
    def stop_after_message(*args, **kwargs):
        consumer.running = False
    mock_logger.info.side_effect = stop_after_message
    
    consumer.consume()
    mock_logger.info.assert_called()

def test_process_invalid_message_no_id(consumer):
    message = Mock()
    message.value = b'{"content": "Test content"}'
    consumer.process_message(message)

def test_process_invalid_message_no_content(consumer):
    message = Mock()
    message.value = b'{"id": 1}'
    consumer.process_message(message)

def test_process_invalid_message_empty(consumer):
    message = Mock()
    message.value = b'{}'
    consumer.process_message(message)

@patch('consumer.kafka_consumer.signal')
def test_stop_handler(mock_signal, consumer):
    consumer.stop(None, None)
    assert consumer.running is False 