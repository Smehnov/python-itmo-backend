from src.app.services.text_processor import TextProcessor
from src.app.models.document import Document

class TestConsumerService:
    def __init__(self, db_session):
        self.db_session = db_session
        self.text_processor = TextProcessor()
    
    def process_message(self, message):
        if isinstance(message, dict):
            content = message.get('content', '')
        else:
            content = message
        return self.text_processor.generate_description(content) 