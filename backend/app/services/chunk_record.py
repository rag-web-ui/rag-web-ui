from typing import Optional, List, Dict, Set
from sqlalchemy import create_engine, text
from app.core.config import settings
import json

class ChunkRecord:
    """Manages chunk-level record keeping for incremental updates"""
    def __init__(self, kb_id: int):
        self.kb_id = kb_id
        self.engine = create_engine(settings.get_database_url)
    
    def list_chunks(self, file_name: Optional[str] = None) -> Set[str]:
        """List all chunk hashes for the given file"""
        query = """
        SELECT hash FROM document_chunks 
        WHERE kb_id = :kb_id
        """
        params = {"kb_id": self.kb_id}
        
        if file_name:
            query += " AND file_name = :file_name"
            params["file_name"] = file_name
            
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            return {row[0] for row in result}
    
    def add_chunks(self, chunks: List[Dict]):
        """Add new chunks to the database"""
        if not chunks:
            return
            
        # Prepare chunks by serializing metadata to JSON
        prepared_chunks = []
        for chunk in chunks:
            prepared_chunk = chunk.copy()
            if 'metadata' in prepared_chunk:
                prepared_chunk['metadata'] = json.dumps(prepared_chunk['metadata'])
            prepared_chunks.append(prepared_chunk)
            
        insert_sql = """
        INSERT INTO document_chunks (id, kb_id, file_name, metadata, hash)
        VALUES (:id, :kb_id, :file_name, :metadata, :hash)
        ON DUPLICATE KEY UPDATE
            metadata = VALUES(metadata),
            updated_at = CURRENT_TIMESTAMP
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(insert_sql), prepared_chunks)
            conn.commit()
    
    def delete_chunks(self, chunk_ids: List[str]):
        """Delete chunks by their IDs"""
        if not chunk_ids:
            return
            
        # Convert list to comma-separated string for IN clause
        chunk_ids_str = "','".join(chunk_ids)
        if chunk_ids_str:
            chunk_ids_str = f"'{chunk_ids_str}'"
        
        delete_sql = f"""
        DELETE FROM document_chunks 
        WHERE kb_id = :kb_id 
        AND id IN ({chunk_ids_str})
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(delete_sql), {"kb_id": self.kb_id})
            conn.commit()
    
    def get_deleted_chunks(self, current_hashes: Set[str], file_name: Optional[str] = None) -> List[str]:
        """Get IDs of chunks that no longer exist in the current version"""
        if not current_hashes:
            # If no current hashes, return all chunk IDs for the file
            query = """
            SELECT id FROM document_chunks 
            WHERE kb_id = :kb_id
            """
            params = {"kb_id": self.kb_id}
            
            if file_name:
                query += " AND file_name = :file_name"
                params["file_name"] = file_name
        else:
            # Convert set to comma-separated string for IN clause
            hashes_str = "','".join(current_hashes)
            if hashes_str:
                hashes_str = f"'{hashes_str}'"
            
            query = f"""
            SELECT id FROM document_chunks 
            WHERE kb_id = :kb_id 
            AND hash NOT IN ({hashes_str})
            """
            params = {"kb_id": self.kb_id}
            
            if file_name:
                query += " AND file_name = :file_name"
                params["file_name"] = file_name
            
        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            return [row[0] for row in result] 