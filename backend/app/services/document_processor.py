import logging
import os
import hashlib
import tempfile
import traceback
from io import BytesIO
from typing import Optional, List, Dict
from fastapi import UploadFile
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
    TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangchainDocument
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.minio import get_minio_client
from app.models.knowledge import ProcessingTask

class UploadResult(BaseModel):
    file_path: str
    file_size: int
    content_type: str
    file_hash: str

class TextChunk(BaseModel):
    content: str
    metadata: Dict

class PreviewResult(BaseModel):
    chunks: List[TextChunk]
    total_chunks: int

async def upload_document(file: UploadFile, kb_id: int) -> UploadResult:
    """Step 1: Upload document to MinIO"""
    content = await file.read()
    file_size = len(content)
    
    # Calculate SHA-256 hash of file content
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Get file extension
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()
    
    # Determine content type
    content_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".md": "text/markdown",
        ".txt": "text/plain"
    }
    
    content_type = content_types.get(ext, "application/octet-stream")
    
    # Upload to MinIO
    minio_client = get_minio_client()
    object_path = f"kb_{kb_id}/{file.filename}"
    minio_client.put_object(
        bucket_name=settings.MINIO_BUCKET_NAME,
        object_name=object_path,
        data=BytesIO(content),
        length=file_size,
        content_type=content_type
    )
    
    return UploadResult(
        file_path=object_path,
        file_size=file_size,
        content_type=content_type,
        file_hash=file_hash
    )

async def preview_document(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> PreviewResult:
    """Step 2: Generate preview chunks"""
    # Get file from MinIO
    minio_client = get_minio_client()
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Download to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        minio_client.fget_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=file_path,
            file_path=temp_file.name
        )
        temp_path = temp_file.name
    
    try:
        # Select appropriate loader
        if ext == ".pdf":
            loader = PyPDFLoader(temp_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(temp_path)
        elif ext == ".md":
            loader = UnstructuredMarkdownLoader(temp_path)
        else:  # Default to text loader
            loader = TextLoader(temp_path)
        
        # Load and split the document
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = text_splitter.split_documents(documents)
        
        # Convert to preview format
        preview_chunks = [
            TextChunk(
                content=chunk.page_content,
                metadata=chunk.metadata
            )
            for chunk in chunks
        ]
        
        return PreviewResult(
            chunks=preview_chunks,
            total_chunks=len(chunks)
        )
    finally:
        os.unlink(temp_path)

async def process_document(file_path: str, kb_id: int, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
    """Step 3: Process document and store in vector database"""
    logger = logging.getLogger(__name__)
    
    try:
        preview_result = await preview_document(file_path, chunk_size, chunk_overlap)
        
        # Initialize embeddings
        logger.info("Initializing OpenAI embeddings...")
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )
        
        # Ensure ChromaDB directory exists
        persist_directory = "./chroma_db"
        os.makedirs(persist_directory, exist_ok=True)
        logger.info(f"ChromaDB directory ensured: {persist_directory}")
        
        # Store document chunks in ChromaDB
        logger.info(f"Initializing ChromaDB with collection: kb_{kb_id}")
        vector_store = Chroma(
            collection_name=f"kb_{kb_id}",
            embedding_function=embeddings,
            persist_directory=persist_directory
        )
        
        documents = [
            LangchainDocument(
                page_content=chunk.content,
                metadata=chunk.metadata
            )
            for chunk in preview_result.chunks
        ]
        
        # Add documents to vector store
        logger.info(f"Adding {len(documents)} documents to vector store")
        vector_store.add_documents(documents)
        logger.info("Documents successfully added to vector store")
        
    except Exception as e:
        logger.error(f"Error in process_document: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 

async def process_document_background(
    file_path: str,
    kb_id: int,
    task_id: int,
    db: Session,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
):
    """Background task for processing document"""
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info(f"Starting document processing for file: {file_path}, kb_id: {kb_id}, task_id: {task_id}")
        
        # Process document
        logger.info("Calling process_document...")
        await process_document(file_path, kb_id, chunk_size, chunk_overlap)
        logger.info("Document processing completed successfully")
        
        # Update task status
        logger.info("Updating task status to completed")
        task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
        if task:
            task.status = "completed"
            db.commit()
            logger.info(f"Task {task_id} marked as completed")
            
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Update task status with error
        task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = f"{str(e)}\n{traceback.format_exc()}"
            db.commit()
            logger.error(f"Task {task_id} marked as failed")
        raise e
    finally:
        logger.info("Closing database connection")
        db.close() 