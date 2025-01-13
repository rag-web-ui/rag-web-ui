import hashlib
from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text
import logging

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.models.knowledge import KnowledgeBase, Document, ProcessingTask, DocumentChunk
from app.schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
    DocumentResponse
)
from app.services.document_processor import process_document_background, upload_document, preview_document, PreviewResult
from app.core.config import settings
from app.core.minio import get_minio_client
from minio.error import MinioException

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
async def delete_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """Delete knowledge base and all associated resources."""
    logger = logging.getLogger(__name__)
    
    kb = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
        .first()
    )
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    try:
        # Get all document file paths before deletion
        document_paths = [doc.file_path for doc in kb.documents]
        
        # Initialize services
        minio_client = get_minio_client()
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )
        vector_store = Chroma(
            collection_name=f"kb_{kb_id}",
            embedding_function=embeddings,
            persist_directory="./chroma_db"
        )
        
        # Clean up external resources first
        cleanup_errors = []
        
        # 1. Clean up MinIO files
        try:
            # Delete all objects with prefix kb_{kb_id}/
            objects = minio_client.list_objects(settings.MINIO_BUCKET_NAME, prefix=f"kb_{kb_id}/")
            for obj in objects:
                minio_client.remove_object(settings.MINIO_BUCKET_NAME, obj.object_name)
            logger.info(f"Cleaned up MinIO files for knowledge base {kb_id}")
        except MinioException as e:
            cleanup_errors.append(f"Failed to clean up MinIO files: {str(e)}")
            logger.error(f"MinIO cleanup error for kb {kb_id}: {str(e)}")
        
        # 2. Clean up vector store
        try:
            vector_store._client.delete_collection(f"kb_{kb_id}")
            logger.info(f"Cleaned up vector store for knowledge base {kb_id}")
        except Exception as e:
            cleanup_errors.append(f"Failed to clean up vector store: {str(e)}")
            logger.error(f"Vector store cleanup error for kb {kb_id}: {str(e)}")
        
        # Finally, delete database records in a single transaction
        db.delete(kb)
        db.commit()
        
        # Report any cleanup errors in the response
        if cleanup_errors:
            return {
                "message": "Knowledge base deleted with cleanup warnings",
                "warnings": cleanup_errors
            }
        
        return {"message": "Knowledge base and all associated resources deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete knowledge base {kb_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete knowledge base: {str(e)}")

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
    
    # First calculate hash from the file content
    file_content = await file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    
    # Clean and normalize filename
    file_name = "".join(c for c in file.filename if c.isalnum() or c in ('-', '_', '.')).strip()
    
    # Check if a document with the same name already exists in this knowledge base
    existing_document = db.query(Document).filter(
        Document.file_name == file_name,
        Document.knowledge_base_id == kb_id
    ).first()
    
    if existing_document:
        return {
            "document_id": existing_document.id,
            "file_path": existing_document.file_path,
            "file_name": existing_document.file_name,
            "is_duplicate": True
        }
    
    # Reset file position for upload
    await file.seek(0)
    # Only upload if the file is new
    upload_result = await upload_document(file, kb_id)
    
    document = Document(
        file_path=upload_result.file_path,
        file_name=upload_result.file_name,
        file_size=upload_result.file_size,
        content_type=upload_result.content_type,
        file_hash=file_hash,
        knowledge_base_id=kb_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return {
        "document_id": document.id,
        "file_path": upload_result.file_path,
        "file_name": document.file_name,
        "is_duplicate": False
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
        document.file_name,
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

# Batch upload documents
@router.post("/{kb_id}/documents/upload")
async def upload_kb_documents(
    kb_id: int,
    files: List[UploadFile],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple documents to MinIO"""
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    results = []
    for file in files:
        # Calculate hash from the file content
        file_content = await file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Clean and normalize filename
        file_name = "".join(c for c in file.filename if c.isalnum() or c in ('-', '_', '.')).strip()
        
        # Check if a document with the same name already exists in this knowledge base
        existing_document = db.query(Document).filter(
            Document.file_name == file_name,
            Document.knowledge_base_id == kb_id
        ).first()
        
        if existing_document:
            results.append({
                "document_id": existing_document.id,
                "file_path": existing_document.file_path,
                "file_name": existing_document.file_name,
                "is_duplicate": True
            })
            continue
        
        # Reset file position for upload
        await file.seek(0)
        # Only upload if the file is new
        upload_result = await upload_document(file, kb_id)
        
        document = Document(
            file_path=upload_result.file_path,
            file_name=upload_result.file_name,
            file_size=upload_result.file_size,
            content_type=upload_result.content_type,
            file_hash=file_hash,
            knowledge_base_id=kb_id
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        results.append({
            "document_id": document.id,
            "file_path": upload_result.file_path,
            "file_name": document.file_name,
            "is_duplicate": False
        })
    
    return results

# Batch preview documents
@router.post("/{kb_id}/documents/preview")
async def preview_kb_documents(
    kb_id: int,
    document_ids: List[int],
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[int, PreviewResult]:
    """Preview multiple documents' chunks"""
    results = {}
    for doc_id in document_ids:
        document = db.query(Document).join(KnowledgeBase).filter(
            Document.id == doc_id,
            Document.knowledge_base_id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        
        preview = await preview_document(
            document.file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        results[doc_id] = preview
    
    return results

# Batch process documents
@router.post("/{kb_id}/documents/process")
async def process_kb_documents(
    kb_id: int,
    document_ids: List[int],
    background_tasks: BackgroundTasks,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process multiple documents asynchronously"""
    tasks = []
    for doc_id in document_ids:
        document = db.query(Document).join(KnowledgeBase).filter(
            Document.id == doc_id,
            Document.knowledge_base_id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        
        task = ProcessingTask(
            document_id=doc_id,
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
            document.file_name,
            kb_id,
            task.id,
            db,
            chunk_size,
            chunk_overlap
        )
        tasks.append({"document_id": doc_id, "task_id": task.id})
    
    return {"tasks": tasks}

# Get batch processing status
@router.get("/{kb_id}/documents/tasks")
async def get_processing_tasks(
    kb_id: int,
    task_ids: str = Query(..., description="Comma-separated list of task IDs to check status for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get status of multiple processing tasks"""
    # Convert comma-separated string to list of integers
    task_id_list = [int(id.strip()) for id in task_ids.split(",")]
    
    tasks = db.query(ProcessingTask).join(KnowledgeBase).filter(
        ProcessingTask.id.in_(task_id_list),
        ProcessingTask.knowledge_base_id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).all()
    
    return {
        task.id: {
            "document_id": task.document_id,
            "status": task.status,
            "error_message": task.error_message
        }
        for task in tasks
    }