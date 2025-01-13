from typing import Optional, List, Dict, Set
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.knowledge import DocumentChunk
import json

class ChunkRecord:
    """Manages chunk-level record keeping for incremental updates"""
    def __init__(self, kb_id: int):
        self.kb_id = kb_id
        self.engine = create_engine(settings.get_database_url)
    
    def list_chunks(self, file_name: Optional[str] = None) -> Set[str]:
        """List all chunk hashes for the given file"""
        with Session(self.engine) as session:
            query = session.query(DocumentChunk.hash).filter(
                DocumentChunk.kb_id == self.kb_id
            )
            
            if file_name:
                query = query.filter(DocumentChunk.file_name == file_name)
                
            return {row[0] for row in query.all()}
    
    def add_chunks(self, chunks: List[Dict]):
        """Add new chunks to the database"""
        if not chunks:
            return
            
        with Session(self.engine) as session:
            for chunk_data in chunks:
                chunk = DocumentChunk(
                    id=chunk_data['id'],
                    kb_id=chunk_data['kb_id'],
                    document_id=chunk_data['document_id'],
                    file_name=chunk_data['file_name'],
                    chunk_metadata=chunk_data['metadata'],
                    hash=chunk_data['hash']
                )
                session.merge(chunk)  # Use merge instead of add to handle updates
            session.commit()
    
    def delete_chunks(self, chunk_ids: List[str]):
        """Delete chunks by their IDs"""
        if not chunk_ids:
            return
            
        with Session(self.engine) as session:
            session.query(DocumentChunk).filter(
                DocumentChunk.kb_id == self.kb_id,
                DocumentChunk.id.in_(chunk_ids)
            ).delete(synchronize_session=False)
            session.commit()
    
    def get_deleted_chunks(self, current_hashes: Set[str], file_name: Optional[str] = None) -> List[str]:
        """Get IDs of chunks that no longer exist in the current version"""
        with Session(self.engine) as session:
            query = session.query(DocumentChunk.id).filter(
                DocumentChunk.kb_id == self.kb_id
            )
            
            if file_name:
                query = query.filter(DocumentChunk.file_name == file_name)
            
            if current_hashes:
                query = query.filter(DocumentChunk.hash.notin_(current_hashes))
            
            return [row[0] for row in query.all()] 