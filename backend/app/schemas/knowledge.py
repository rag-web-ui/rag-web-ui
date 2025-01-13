from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProcessingTaskResponse(BaseModel):
    id: int
    status: str
    error_message: Optional[str] = None
    document_id: int
    knowledge_base_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    file_path: Optional[str] = None
    file_name: str
    file_size: Optional[int] = None
    content_type: Optional[str] = None
    file_hash: Optional[str] = None

class DocumentCreate(DocumentBase):
    knowledge_base_id: int

class DocumentResponse(DocumentBase):
    id: int
    knowledge_base_id: int
    created_at: datetime
    updated_at: datetime
    processing_tasks: List[ProcessingTaskResponse] = []

    class Config:
        from_attributes = True

class KnowledgeBaseBase(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBaseUpdate(KnowledgeBaseBase):
    pass

class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentResponse] = []

    class Config:
        from_attributes = True 