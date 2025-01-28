from typing import Dict, Type

from app.services.base import EmbeddingsService
from app.services.openai import OpenAIEmbeddingsService
from app.services.ollama import OllamaEmbeddingsService

class ServiceFactory:
    """Factory for creating various services"""
    
    _embeddings_services: Dict[str, Type[EmbeddingsService]] = {
        "openai": OpenAIEmbeddingsService,
        "ollama": OllamaEmbeddingsService
    }
    
    @classmethod
    def create_embeddings_service(cls, service_type: str, config: dict) -> EmbeddingsService:
        """Create an embeddings service instance
        
        Args:
            service_type: Type of embeddings service ("openai" or "ollama")
            config: Configuration for the service
            
        Returns:
            An instance of EmbeddingsService
        """
        if service_type not in cls._embeddings_services:
            raise ValueError(f"Unknown embeddings service type: {service_type}")
            
        service_class = cls._embeddings_services[service_type]
        return service_class.from_config(config) 