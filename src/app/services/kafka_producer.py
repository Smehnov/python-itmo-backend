from kafka import KafkaProducer
import json
from ..core.config import settings
from ..core.logging import logger
from ..core.metrics import KAFKA_MESSAGES_SENT, KAFKA_MESSAGES_FAILED

class MessageProducer:
    def __init__(self):
        logger.info(f"Initializing Kafka producer with bootstrap servers: {settings.KAFKA_BOOTSTRAP_SERVERS}")
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        )
        logger.info("Kafka producer initialized successfully")

    def send_message(self, message: dict):
        try:
            logger.debug(f"Sending message to topic {settings.KAFKA_TOPIC}: {message}")
            message_bytes = json.dumps(message).encode('utf-8')
            self.producer.send(settings.KAFKA_TOPIC, message_bytes)
            KAFKA_MESSAGES_SENT.inc()
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {e}")
            KAFKA_MESSAGES_FAILED.inc()
            raise 