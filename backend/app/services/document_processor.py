import os
from typing import Optional
from io import BytesIO
import tempfile
from fastapi import UploadFile
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredMarkdownLoader,
    TextLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings
from app.core.minio import get_minio_client

class ProcessedDocument(BaseModel):
    title: str
    content: str
    file_path: Optional[str] = None
    file_size: int
    content_type: str

async def process_document(file: UploadFile, kb_id: int) -> ProcessedDocument:
    # Read file content
    content = await file.read()
    file_size = len(content)
    
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
    
    # Create a temporary file for document processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
        temp_file.write(content)
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
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_API_BASE
        )
        
        # Store document chunks in ChromaDB
        vector_store = Chroma(
            collection_name=f"kb_{kb_id}",
            embedding_function=embeddings,
            persist_directory="./chroma_db"
        )
        
        # Add documents to vector store
        vector_store.add_documents(chunks)
        
        # Combine all chunks into a single text for the database record
        combined_text = "\n\n".join([chunk.page_content for chunk in chunks])
        
        return ProcessedDocument(
            title=file.filename,
            content=combined_text,
            file_path=object_path,
            file_size=file_size,
            content_type=content_type
        )
    finally:
        # Clean up temporary file
        os.unlink(temp_path) 