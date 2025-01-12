from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.models.knowledge import KnowledgeBase, Document, ProcessingTask
from app.schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
    DocumentResponse
)
from app.services.document_processor import process_document_background, upload_document, preview_document, process_document, PreviewResult

router = APIRouter()

@router.post("", response_model=KnowledgeBaseResponse)
def create_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_in: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create new knowledge base."""
    kb = KnowledgeBase(
        name=kb_in.name,
        description=kb_in.description,
        user_id=current_user.id
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb

@router.get("", response_model=List[KnowledgeBaseResponse])
def get_knowledge_bases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Retrieve knowledge bases."""
    knowledge_bases = (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return knowledge_bases

@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
def get_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get knowledge base by ID."""
    from sqlalchemy.orm import joinedload
    
    kb = (
        db.query(KnowledgeBase)
        .options(
            joinedload(KnowledgeBase.documents)
            .joinedload(Document.processing_tasks)
        )
        .filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
        .first()
    )

    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    return kb

@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
def update_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    kb_in: KnowledgeBaseUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Update knowledge base."""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")

    for field, value in kb_in.dict(exclude_unset=True).items():
        setattr(kb, field, value)

    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb

@router.delete("/{kb_id}")
def delete_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete knowledge base."""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    db.delete(kb)
    db.commit()
    return {"message": "Knowledge base deleted"}

# Step 1: Upload document
@router.post("/{kb_id}/document/upload")
async def upload_kb_document(
    kb_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Step 1: Upload document to MinIO"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    upload_result = await upload_document(file, kb_id)
    
    document = Document(
        title=file.filename,
        file_path=upload_result.file_path,
        file_size=upload_result.file_size,
        content_type=upload_result.content_type,
        knowledge_base_id=kb_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return {
        "document_id": document.id,
        "file_path": upload_result.file_path
    }

# Step 2: Preview chunks
@router.post("/{kb_id}/document/{document_id}/preview")
async def preview_kb_document(
    kb_id: int,
    document_id: int,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> PreviewResult:
    """Step 2: Preview document chunks"""
    document = db.query(Document).join(KnowledgeBase).filter(
        Document.id == document_id,
        Document.knowledge_base_id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return await preview_document(
        document.file_path,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

# Step 3: Process document
@router.post("/{kb_id}/document/{document_id}/process")
async def process_kb_document(
    kb_id: int,
    document_id: int,
    background_tasks: BackgroundTasks,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Step 3: Process document asynchronously"""
    document = db.query(Document).join(KnowledgeBase).filter(
        Document.id == document_id,
        Document.knowledge_base_id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    task = ProcessingTask(
        document_id=document_id,
        knowledge_base_id=kb_id,
        status="pending"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    print(f"Processing task created: {task.id}")
    background_tasks.add_task(
        process_document_background,
        document.file_path,
        kb_id,
        task.id,
        db,
        chunk_size,
        chunk_overlap
    )
    
    return {"task_id": task.id}

# Get task status
@router.get("/{kb_id}/document/{document_id}/task/{task_id}")
async def get_processing_task(
    kb_id: int,
    document_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get processing task status"""
    task = db.query(ProcessingTask).join(KnowledgeBase).filter(
        ProcessingTask.id == task_id,
        ProcessingTask.document_id == document_id,
        ProcessingTask.knowledge_base_id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.id,
        "status": task.status,
        "error_message": task.error_message
    }