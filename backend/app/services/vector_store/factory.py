from typing import Dict, Type, Any
from langchain_core.embeddings import Embeddings

from .base import BaseVectorStore
from .chroma import ChromaVectorStore
from .qdrant import QdrantStore

class VectorStoreFactory:
    """Factory for creating vector store instances"""
    
    _stores: Dict[str, Type[BaseVectorStore]] = {
        'chroma': ChromaVectorStore,
        'qdrant': QdrantStore
    }
    
    @classmethod
    def create(
        cls,
        store_type: str,
        collection_name: str,
        embedding_function: Embeddings,
        **kwargs: Any
    ) -> BaseVectorStore:
        """Create a vector store instance
        
        Args:
            store_type: Type of vector store ('chroma', 'qdrant', etc.)
            collection_name: Name of the collection
            embedding_function: Embedding function to use
            **kwargs: Additional arguments for specific vector store implementations
            
        Returns:
            An instance of the requested vector store
            
        Raises:
            ValueError: If store_type is not supported
        """
        store_class = cls._stores.get(store_type.lower())
        if not store_class:
            raise ValueError(
                f"Unsupported vector store type: {store_type}. "
                f"Supported types are: {', '.join(cls._stores.keys())}"
            )
        
        return store_class(
            collection_name=collection_name,
            embedding_function=embedding_function,
            **kwargs
        )
    
    @classmethod
    def register_store(cls, name: str, store_class: Type[BaseVectorStore]) -> None:
        """Register a new vector store implementation
        
        Args:
            name: Name of the vector store type
            store_class: Vector store class implementation
        """
        cls._stores[name.lower()] = store_class 