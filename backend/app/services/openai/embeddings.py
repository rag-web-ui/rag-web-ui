from langchain_openai import OpenAIEmbeddings as LangchainOpenAIEmbeddings
from langchain_core.embeddings import Embeddings

from app.services.base import EmbeddingsService
from .config import OpenAIConfig

class OpenAIEmbeddingsService(EmbeddingsService):
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self._embeddings = None

    def get_embeddings(self) -> Embeddings:
        if self._embeddings is None:
            self._embeddings = LangchainOpenAIEmbeddings(
                openai_api_key=self.config.api_key,
                openai_api_base=self.config.api_base,
                model=self.config.embedding_model
            )
        return self._embeddings

    @classmethod
    def from_config(cls, config: dict) -> 'OpenAIEmbeddingsService':
        return cls(OpenAIConfig(**config)) 