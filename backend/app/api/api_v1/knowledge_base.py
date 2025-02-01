import hashlib
from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from sqlalchemy.orm import Session
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.models.knowledge import KnowledgeBase, Document, ProcessingTask, DocumentChunk, DocumentUpload
from app.schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdate,
    DocumentResponse,
    PreviewRequest
)
from app.services.document_processor import process_document_background, upload_document, preview_document, PreviewResult
from app.core.config import settings
from app.core.minio import get_minio_client
from minio.error import MinioException
from app.services.vector_store import VectorStoreFactory

router = APIRouter()

logger = logging.getLogger(__name__)

class TestRetrievalRequest(BaseModel):
    query: str
    kb_id: int
    top_k: int

@router.post("", response_model=KnowledgeBaseResponse)
def create_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_in: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new knowledge base.
    """
    kb = KnowledgeBase(
        name=kb_in.name,
        description=kb_in.description,
        user_id=current_user.id
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    logger.info(f"Knowledge base created: {kb.name} for user {current_user.id}")
    return kb

@router.get("", response_model=List[KnowledgeBaseResponse])
def get_knowledge_bases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve knowledge bases.
    """
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
    """
    Get knowledge base by ID.
    """
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
    """
    Update knowledge base.
    """
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
    logger.info(f"Knowledge base updated: {kb.name} for user {current_user.id}")
    return kb

@router.delete("/{kb_id}")
async def delete_knowledge_base(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete knowledge base and all associated resources.
    """
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

        vector_store = VectorStoreFactory.create(
            store_type=settings.VECTOR_STORE_TYPE,
            collection_name=f"kb_{kb_id}",
            embedding_function=embeddings,
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
            vector_store._store.delete_collection(f"kb_{kb_id}")
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

# Batch upload documents
@router.post("/{kb_id}/documents/upload")
async def upload_kb_documents(
    kb_id: int,
    files: List[UploadFile],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple documents to MinIO.
    """
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    results = []
    for file in files:
        # 1. 计算文件 hash
        file_content = await file.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # 2. 检查是否存在完全相同的文件（名称和hash都相同）
        existing_document = db.query(Document).filter(
            Document.file_name == file.filename,
            Document.file_hash == file_hash,
            Document.knowledge_base_id == kb_id
        ).first()
        
        if existing_document:
            # 完全相同的文件，直接返回
            results.append({
                "document_id": existing_document.id,
                "file_name": existing_document.file_name,
                "status": "exists",
                "message": "文件已存在且已处理完成",
                "skip_processing": True
            })
            continue
        
        # 3. 上传到临时目录
        temp_path = f"kb_{kb_id}/temp/{file.filename}"
        await file.seek(0)
        try:
            minio_client = get_minio_client()
            file_size = len(file_content)  # 使用之前读取的文件内容长度
            minio_client.put_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=temp_path,
                data=file.file,
                length=file_size,  # 指定文件大小
                content_type=file.content_type
            )
        except MinioException as e:
            logger.error(f"Failed to upload file to MinIO: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload file")
        
        # 4. 创建上传记录
        upload = DocumentUpload(
            knowledge_base_id=kb_id,
            file_name=file.filename,
            file_hash=file_hash,
            file_size=len(file_content),
            content_type=file.content_type,
            temp_path=temp_path
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)
        
        results.append({
            "upload_id": upload.id,
            "file_name": file.filename,
            "temp_path": temp_path,
            "status": "pending",
            "skip_processing": False
        })
    
    return results

# Batch preview documents
@router.post("/{kb_id}/documents/preview")
async def preview_kb_documents(
    kb_id: int,
    preview_request: PreviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[int, PreviewResult]:
    """
    Preview multiple documents' chunks.
    """
    results = {}
    for doc_id in preview_request.document_ids:
        # 先尝试在 Document 表中查找
        document = db.query(Document).join(KnowledgeBase).filter(
            Document.id == doc_id,
            Document.knowledge_base_id == kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if document:
            file_path = document.file_path
        else:
            # 如果不在 Document 表中，则在 DocumentUpload 表中查找
            upload = db.query(DocumentUpload).join(KnowledgeBase).filter(
                DocumentUpload.id == doc_id,
                DocumentUpload.knowledge_base_id == kb_id,
                KnowledgeBase.user_id == current_user.id
            ).first()
            
            if not upload:
                raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
            
            file_path = upload.temp_path
        
        preview = await preview_document(
            file_path,
            chunk_size=preview_request.chunk_size,
            chunk_overlap=preview_request.chunk_overlap
        )
        results[doc_id] = preview
    
    return results

# Batch process documents
@router.post("/{kb_id}/documents/process")
async def process_kb_documents(
    kb_id: int,
    upload_results: List[dict],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process multiple documents asynchronously.
    """
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    tasks = []
    for result in upload_results:
        # 跳过已存在的文件
        if result.get("skip_processing"):
            continue
            
        upload_id = result["upload_id"]
        upload = db.query(DocumentUpload).get(upload_id)
        if not upload:
            continue
        
        try:
            # 创建处理任务
            task = ProcessingTask(
                document_upload_id=upload_id,  # 使用正确的字段名
                knowledge_base_id=kb_id,
                status="pending"
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            
            background_tasks.add_task(
                process_document_background,
                upload.temp_path,
                upload.file_name,
                kb_id,
                task.id,
                db
            )
            tasks.append({
                "upload_id": upload_id,
                "task_id": task.id
            })
            
        except Exception as e:
            logger.error(f"Failed to create processing task: {str(e)}")
            db.rollback()
            continue
    
    return {"tasks": tasks}

@router.post("/cleanup")
async def cleanup_temp_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up expired temporary files.
    """
    # 找出过期的上传记录（24小时前）
    expired_time = datetime.utcnow() - timedelta(hours=24)
    expired_uploads = db.query(DocumentUpload).filter(
        DocumentUpload.created_at < expired_time
    ).all()
    
    minio_client = get_minio_client()
    for upload in expired_uploads:
        # 清理临时文件
        try:
            minio_client.remove_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=upload.temp_path
            )
        except MinioException as e:
            logger.error(f"Failed to delete temp file {upload.temp_path}: {str(e)}")
        
        # 删除记录
        db.delete(upload)
    
    db.commit()
    
    return {"message": f"Cleaned up {len(expired_uploads)} expired uploads"}

# Get batch processing status
@router.get("/{kb_id}/documents/tasks")
async def get_processing_tasks(
    kb_id: int,
    task_ids: str = Query(..., description="Comma-separated list of task IDs to check status for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get status of multiple processing tasks.
    """
    # Convert comma-separated string to list of integers
    task_id_list = [int(id.strip()) for id in task_ids.split(",")]
    
    tasks = db.query(ProcessingTask).join(DocumentUpload).join(KnowledgeBase).filter(
        ProcessingTask.id.in_(task_id_list),
        ProcessingTask.knowledge_base_id == kb_id,
        KnowledgeBase.user_id == current_user.id
    ).all()
    
    return {
        task.id: {
            "document_id": task.document_id,
            "status": task.status,
            "error_message": task.error_message,
            "upload_id": task.document_upload_id,
            "file_name": task.document_upload.file_name if task.document_upload else None
        }
        for task in tasks
    }

@router.get("/{kb_id}/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    *,
    db: Session = Depends(get_db),
    kb_id: int,
    doc_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get document details by ID.
    """
    document = (
        db.query(Document)
        .join(KnowledgeBase)
        .filter(
            Document.id == doc_id,
            Document.knowledge_base_id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document

@router.post("/test-retrieval")
async def test_retrieval(
    request: TestRetrievalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Test retrieval quality for a given query against a knowledge base.
    """
    try:
        kb = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == request.kb_id,
            KnowledgeBase.user_id == current_user.id
        ).first()
        
        if not kb:
            raise HTTPException(
                status_code=404,
                detail=f"Knowledge base {request.kb_id} not found",
            )
        
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )
        
        vector_store = VectorStoreFactory.create(
            store_type=settings.VECTOR_STORE_TYPE,
            collection_name=f"kb_{request.kb_id}",
            embedding_function=embeddings,
        )
        
        results = vector_store.similarity_search_with_score(request.query, k=request.top_k)
        
        response = []
        for doc, score in results:
            response.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
            
        return {"results": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
