from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, JSON
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from datetime import datetime
import sqlalchemy as sa

class KnowledgeBase(Base, TimestampMixin):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(LONGTEXT)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    user = relationship("User", back_populates="knowledge_bases")
    processing_tasks = relationship("ProcessingTask", back_populates="knowledge_base")
    chunks = relationship("DocumentChunk", back_populates="knowledge_base", cascade="all, delete-orphan")

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(255), nullable=False)  # Path in MinIO
    file_name = Column(String(255), nullable=False)  # Actual file name
    file_size = Column(Integer)  # File size in bytes
    content_type = Column(String(100))  # MIME type
    file_hash = Column(String(64), index=True)  # SHA-256 hash of file content
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents") 
    processing_tasks = relationship("ProcessingTask", back_populates="document")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        # Ensure file_name is unique within each knowledge base
        sa.UniqueConstraint('knowledge_base_id', 'file_name', name='uq_kb_file_name'),
    )

class ProcessingTask(Base):
    __tablename__ = "processing_tasks"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    knowledge_base = relationship("KnowledgeBase", back_populates="processing_tasks")
    document = relationship("Document", back_populates="processing_tasks")

class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True)  # SHA-256 hash as ID
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    chunk_metadata = Column(JSON, nullable=True)
    hash = Column(String(64), nullable=False, index=True)  # Content hash for change detection
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="chunks")
    document = relationship("Document", back_populates="chunks")

    __table_args__ = (
        sa.Index('idx_kb_file_name', 'kb_id', 'file_name'),
    ) 