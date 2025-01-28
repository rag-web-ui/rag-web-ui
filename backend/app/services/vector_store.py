from typing import Optional
from langchain_core.vectorstores import VectorStore
from langchain_chroma import Chroma
from langchain_community.vectorstores import Qdrant
from app.core.config import settings
from app.services.embeddings.factory import EmbeddingsFactory

class VectorStoreFactory:
    """Factory for creating vector stores"""
    
    @staticmethod
    def create(
        store_type: Optional[str] = None,
        collection_name: str = "default",
        embedding_function = None,
    ) -> VectorStore:
        """Create a vector store instance
        
        Args:
            store_type: Type of vector store ("chroma" or "qdrant")
            collection_name: Name of the collection
            embedding_function: Optional embedding function to use
            
        Returns:
            A VectorStore instance
        """
        if store_type is None:
            store_type = settings.VECTOR_STORE_TYPE
            
        if embedding_function is None:
            embeddings_service = EmbeddingsFactory.create(
                settings.EMBEDDINGS_SERVICE_TYPE,
                settings.embeddings_config
            )
            embedding_function = embeddings_service.get_embeddings()
            
        if store_type == "chroma":
            return Chroma(
                collection_name=collection_name,
                embedding_function=embedding_function,
                client_settings={
                    "host": settings.CHROMA_DB_HOST,
                    "port": settings.CHROMA_DB_PORT,
                }
            )
        elif store_type == "qdrant":
            return Qdrant(
                client={
                    "url": settings.VECTOR_STORE_URL,
                    "prefer_grpc": settings.VECTOR_STORE_PREFER_GRPC
                },
                collection_name=collection_name,
                embeddings=embedding_function
            )
        else:
            raise ValueError(f"Unknown vector store type: {store_type}") 