from kafka import KafkaConsumer
import json
import signal
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session, sessionmaker
from src.app.core.database import SessionLocal
from src.app.models.document import Document
from src.app.services.text_processor import TextProcessor
from src.app.core.config import settings
from src.app.core.logging import logger
from src.app.core.metrics import PROCESSING_TIME, PROCESSING_SUCCESS, PROCESSING_FAILED

class MessageConsumer:
    def __init__(self):
        self.running = True
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)
        
        # Initialize consumer with retry logic
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                logger.info("Initializing Kafka consumer...")
                self.consumer = KafkaConsumer(
                    settings.KAFKA_TOPIC,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    auto_offset_reset='earliest',  # Start from earliest message if no offset
                    group_id='document_processor',  # Consumer group ID
                    # Add consumer configuration for better reliability
                    enable_auto_commit=True,
                    auto_commit_interval_ms=1000,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000
                )
                self.text_processor = TextProcessor()
                self.Session = sessionmaker(autocommit=False, autoflush=False, bind=SessionLocal().bind)
                logger.info(f"Connected to Kafka at {settings.KAFKA_BOOTSTRAP_SERVERS}")
                break
            except Exception as e:
                retry_count += 1
                logger.error(f"Failed to connect to Kafka (attempt {retry_count}/{max_retries}): {e}")
                if retry_count == max_retries:
                    raise
                time.sleep(5)  # Wait before retrying

    def stop(self, signum, frame):
        """Handle shutdown gracefully"""
        logger.info("Received stop signal. Closing consumer...")
        self.running = False

    def consume(self):
        """Continuously consume messages"""
        logger.info("Starting to consume messages...")
        try:
            while self.running:
                try:
                    messages = self.consumer.poll(timeout_ms=1000)
                    if messages:
                        logger.debug(f"Received {sum(len(msgs) for msgs in messages.values())} messages")
                        for topic_partition, msgs in messages.items():
                            for message in msgs:
                                self.process_message(message)
                except Exception as e:
                    logger.error(f"Error polling messages: {e}")
                    time.sleep(1)  # Wait before retrying
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        finally:
            logger.info("Closing consumer connection...")
            self.consumer.close()

    def process_message(self, message):
        session = self.Session()
        try:
            data = json.loads(message.value.decode())
            logger.debug(f"Processing message: {data}")
            
            if 'document_id' not in data or 'content' not in data:
                logger.warning(f"Invalid message format: {data}")
                PROCESSING_FAILED.inc()
                return
                
            doc_id = data["document_id"]
            content = data["content"]
            
            doc = session.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.short_description = TextProcessor.generate_description(content)
                session.commit()
                PROCESSING_SUCCESS.inc()
            else:
                logger.warning(f"Document {doc_id} not found in database")
                PROCESSING_FAILED.inc()
        except Exception as e:
            PROCESSING_FAILED.inc()
            logger.error(f"Error processing message: {str(e)}")
            session.rollback()
        finally:
            session.close()

def main():
    try:
        consumer = MessageConsumer()
        consumer.consume()
    except Exception as e:
        logger.error(f"Fatal error in consumer: {e}")
        raise

if __name__ == "__main__":
    main() 