from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(default="", min_length=0)
    short_description: Optional[str] = None
    
class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=0)
    short_description: Optional[str] = None

class Document(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(Document):
    pass 