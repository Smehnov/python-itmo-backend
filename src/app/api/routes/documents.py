from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import time
from ...core.logging import logger

from ...core.database import get_db
from ...schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from ...services.document import DocumentService
from ...services.kafka_producer import MessageProducer
from ...core.metrics import REQUEST_COUNT, REQUEST_DURATION, DOCUMENT_SIZE

router = APIRouter(prefix="/documents", tags=["documents"])

def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    producer = MessageProducer()
    return DocumentService(db, producer)

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(request: Request, doc: DocumentCreate, service: DocumentService = Depends(get_document_service)):
    try:
        result = service.create(doc)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/{doc_id}", response_model=DocumentResponse)
def get_document(
    doc_id: int,
    service: DocumentService = Depends(get_document_service)
):
    doc = service.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/", response_model=List[DocumentResponse])
def list_documents(
    skip: int = 0,
    limit: int = 10,
    service: DocumentService = Depends(get_document_service)
):
    return service.list(skip, limit)

@router.put("/{doc_id}", response_model=DocumentResponse)
def update_document(
    doc_id: int,
    doc: DocumentUpdate,
    service: DocumentService = Depends(get_document_service)
):
    updated_doc = service.update(doc_id, doc)
    if not updated_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return updated_doc

@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    doc_id: int,
    service: DocumentService = Depends(get_document_service)
):
    if not service.remove(doc_id):
        raise HTTPException(status_code=404, detail="Document not found") 