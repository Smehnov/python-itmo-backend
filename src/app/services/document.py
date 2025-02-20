from typing import Optional, List
from sqlalchemy.orm import Session
from ..models.document import Document
from ..schemas.document import DocumentCreate, DocumentUpdate
from ..services.kafka_producer import MessageProducer
from ..core.logging import logger
from src.app.core.metrics import DOCUMENTS_PROCESSED, KAFKA_MESSAGES_SENT
from src.app.services.text_processor import TextProcessor

class DocumentService:
    def __init__(self, db: Session, producer: MessageProducer):
        self.db = db
        self.producer = producer
        self._test_mode = False  # Flag for test mode
    
    def get_document(self, doc_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.db.query(Document).filter(Document.id == doc_id).first()
    
    def create(self, doc: DocumentCreate) -> Document:
        try:
            logger.info(f"Creating new document with title: {doc.title}")
            DOCUMENTS_PROCESSED.inc()
            db_doc = Document(**doc.model_dump())
            db_doc.short_description = TextProcessor.generate_description(doc.content)
            self.db.add(db_doc)
            self.db.commit()
            self.db.refresh(db_doc)
            
            message = {
                "document_id": db_doc.id,
                "content": db_doc.content
            }
            
            self.producer.send_message(message)
            KAFKA_MESSAGES_SENT.inc()
            return db_doc
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            raise
    
    def get(self, doc_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == doc_id).first()
    
    def list(self, skip: int = 0, limit: int = 10) -> List[Document]:
        return self.db.query(Document).offset(skip).limit(limit).all()
    
    def update(self, doc_id: int, doc: DocumentUpdate) -> Optional[Document]:
        db_doc = self.get(doc_id)
        if not db_doc:
            return None
            
        update_data = doc.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_doc, field, value)
            
        self.db.commit()
        self.db.refresh(db_doc)
        return db_doc
    
    def remove(self, doc_id: int) -> bool:
        db_doc = self.get(doc_id)
        if not db_doc:
            return False
            
        self.db.delete(db_doc)
        self.db.commit()
        return True 