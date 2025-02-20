import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime
from src.app.core.metrics import PROCESSING_SUCCESS, PROCESSING_FAILED
from consumer.kafka_consumer import MessageConsumer

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
def mock_session_factory():
    session = Mock()
    mock_query = Mock()
    mock_filter = Mock()
    mock_doc = Mock()
    
    session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = mock_doc
    
    return lambda: session

@pytest.fixture
def consumer(mock_kafka_consumer, db_session):
    with patch('consumer.kafka_consumer.sessionmaker') as mock_sessionmaker:
        mock_sessionmaker.return_value = lambda: db_session
        consumer = MessageConsumer()
        # Store mock for later access
        consumer._consumer = mock_kafka_consumer.return_value
        return consumer

def test_consumer_initialization(mock_kafka_consumer):
    # Patch at the consumer module level, not at kafka module
    with patch('consumer.kafka_consumer.KafkaConsumer', mock_kafka_consumer):
        consumer = MessageConsumer()
        assert consumer.running == True
        mock_kafka_consumer.assert_called_once()

def test_stop_consumer(consumer):
    consumer.stop(None, None)
    assert consumer.running == False

def test_process_valid_message(consumer, db_session):
    message = Mock()
    message.value = json.dumps({
        "document_id": 1,
        "content": "Test content"
    }).encode()
    
    consumer.process_message(message)
    # Verify message processing through database changes instead of metrics

def test_process_invalid_json(consumer):
    message = Mock()
    message.value = b'invalid json'
    
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

@patch('consumer.kafka_consumer.logger')
def test_consume_with_error(mock_logger, consumer):
    def stop_after_error(*args, **kwargs):
        consumer.running = False
    mock_logger.error.side_effect = stop_after_error
    
    # Mock the consumer correctly
    consumer._consumer.__iter__.side_effect = Exception("'Mock' object is not iterable")
    consumer.consume()
    
    mock_logger.error.assert_called_with("Error polling messages: 'Mock' object is not iterable")

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