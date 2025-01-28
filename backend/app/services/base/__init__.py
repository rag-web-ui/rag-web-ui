from abc import ABC, abstractmethod
from typing import Any
from langchain_core.embeddings import Embeddings

class EmbeddingsService(ABC):
    """Base class for embeddings services"""
    
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        """Get the embeddings model instance"""
        pass

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict) -> 'EmbeddingsService':
        """Create embeddings service from config"""
        pass 