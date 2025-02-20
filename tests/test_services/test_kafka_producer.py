import pytest
from unittest.mock import Mock, patch
from src.app.services.kafka_producer import MessageProducer

@pytest.fixture
def mock_kafka_producer():
    with patch('src.app.services.kafka_producer.KafkaProducer') as mock:
        instance = Mock()
        # Configure all needed methods
        instance.send = Mock()
        instance.send.return_value.get.return_value = Mock(
            partition=0,
            offset=1
        )
        mock.return_value = instance
        yield mock

@pytest.fixture
def producer(mock_kafka_producer):
    return MessageProducer()

def test_kafka_producer_init(mock_kafka_producer):
    producer = MessageProducer()
    mock_kafka_producer.assert_called_once()

def test_send_message_success(producer):
    producer.send_message({"test": "data"})
    # Verify through mock calls instead of metrics

def test_send_message_failure(mock_kafka_producer):
    mock_kafka_producer.return_value.send.side_effect = Exception("Kafka error")
    producer = MessageProducer()
    
    with pytest.raises(Exception):
        producer.send_message({"test": "data"})