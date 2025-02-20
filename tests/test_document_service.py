import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.app.services.document import DocumentService
from src.app.models.document import Document
from src.app.schemas.document import DocumentCreate, DocumentUpdate
from src.app.core.metrics import DOCUMENTS_PROCESSED, KAFKA_MESSAGES_SENT

def test_create_document_with_metrics(db_session: Session):
    # Arrange
    producer_mock = Mock()
    service = DocumentService(db_session, producer_mock)
    doc_data = DocumentCreate(title="Test", content="Test content")
    
    # Get initial metric values
    initial_processed = DOCUMENTS_PROCESSED._value.get()
    initial_sent = KAFKA_MESSAGES_SENT._value.get()

    # Act
    result = service.create(doc_data)

    # Assert
    assert result.title == "Test"
    assert result.content == "Test content"
    assert DOCUMENTS_PROCESSED._value.get() == initial_processed + 1
    assert KAFKA_MESSAGES_SENT._value.get() == initial_sent + 1
    producer_mock.send_message.assert_called_once()

def test_kafka_producer_metrics():
    from src.app.services.kafka_producer import MessageProducer
    from src.app.core.metrics import KAFKA_MESSAGES_SENT, KAFKA_MESSAGES_FAILED
    
    # Mock KafkaProducer
    with patch('src.app.services.kafka_producer.KafkaProducer', autospec=True) as mock_producer:
        # Success case
        producer = MessageProducer()
        mock_producer.return_value.send.return_value.get.return_value = Mock(partition=0, offset=1)
        initial_sent = KAFKA_MESSAGES_SENT._value.get()
        
        producer.send_message({"test": "data"})
        mock_producer.return_value.send.assert_called_once()

        # Failure case
        mock_producer.return_value.send.side_effect = Exception("Kafka error")
        initial_failed = KAFKA_MESSAGES_FAILED._value.get()
        
        with pytest.raises(Exception):
            producer.send_message({"test": "data"})
        assert KAFKA_MESSAGES_FAILED._value.get() == initial_failed + 1 