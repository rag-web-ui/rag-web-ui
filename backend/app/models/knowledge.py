from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, JSON, BigInteger, TIMESTAMP, text, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from datetime import datetime
import sqlalchemy as sa
import enum

class EmbeddingsServiceType(str, enum.Enum):
    """Embeddings service types"""
    OPENAI = "openai"
    OLLAMA = "ollama"

class KnowledgeBase(Base, TimestampMixin):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    embeddings_service = Column(
        Enum(EmbeddingsServiceType),
        nullable=False,
        default=EmbeddingsServiceType.OPENAI
    )
    embeddings_config = Column(JSON, nullable=True)  # 存储服务特定的配置
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    user = relationship("User", back_populates="knowledge_bases")
    processing_tasks = relationship("ProcessingTask", back_populates="knowledge_base")
    chunks = relationship("DocumentChunk", back_populates="knowledge_base", cascade="all, delete-orphan")
    document_uploads = relationship("DocumentUpload", back_populates="knowledge_base", cascade="all, delete-orphan")

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(255), nullable=False)  # Path in MinIO
    file_name = Column(String(255), nullable=False)  # Actual file name
    file_size = Column(BigInteger, nullable=False)  # File size in bytes
    content_type = Column(String(255), nullable=False)  # MIME type
    file_hash = Column(String(64), nullable=False)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents") 
    processing_tasks = relationship("ProcessingTask", back_populates="document")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        # Ensure file_name is unique within each knowledge base
        sa.UniqueConstraint('knowledge_base_id', 'file_name', name='uq_kb_file_name'),
    )

class DocumentUpload(Base, TimestampMixin):
    __tablename__ = "document_uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    content_type = Column(String(255), nullable=False)
    temp_path = Column(String, nullable=False)
    status = Column(String(50), nullable=False, server_default="pending")
    error_message = Column(Text)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="document_uploads")
    processing_task = relationship("ProcessingTask", back_populates="document_upload", uselist=False)

class ProcessingTask(Base, TimestampMixin):
    __tablename__ = "processing_tasks"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    document_upload_id = Column(Integer, ForeignKey("document_uploads.id"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    knowledge_base = relationship("KnowledgeBase", back_populates="processing_tasks")
    document = relationship("Document", back_populates="processing_tasks")
    document_upload = relationship("DocumentUpload", back_populates="processing_task")

class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True)  # SHA-256 hash as ID
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    chunk_metadata = Column(JSON, nullable=False)
    hash = Column(String(64), nullable=False)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="chunks")
    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        sa.Index('idx_kb_file_name', 'kb_id', 'file_name'),
    ) 