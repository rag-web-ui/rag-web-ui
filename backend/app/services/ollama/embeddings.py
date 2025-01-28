from langchain_ollama import OllamaEmbeddings
from langchain_core.embeddings import Embeddings

from app.services.base import EmbeddingsService
from .config import OllamaConfig

class OllamaEmbeddingsService(EmbeddingsService):
    def __init__(self, config: OllamaConfig):
        self.config = config
        self._embeddings = None

    def get_embeddings(self) -> Embeddings:
        if self._embeddings is None:
            self._embeddings = OllamaEmbeddings(
                base_url=self.config.base_url,
                model=self.config.embedding_model
            )
        return self._embeddings

    @classmethod
    def from_config(cls, config: dict) -> 'OllamaEmbeddingsService':
        return cls(OllamaConfig(**config)) 