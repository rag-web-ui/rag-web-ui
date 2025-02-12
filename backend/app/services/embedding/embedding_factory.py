from app.core.config import settings
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings
# If you plan on adding other embeddings, import them here
# from some_other_module import AnotherEmbeddingClass


class EmbeddingsFactory:
    @staticmethod
    def create():
        """
        Factory method to create an embeddings instance based on .env config.
        """
        # Suppose your .env has a value like EMBEDDINGS_PROVIDER=openai
        embeddings_provider = settings.EMBEDDINGS_PROVIDER.lower()

        if embeddings_provider == "openai":
            return OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                model=settings.OPENAI_EMBEDDINGS_MODEL
            )
        elif embeddings_provider == "dashscope":
            return DashScopeEmbeddings(
                model=settings.DASH_SCOPE_EMBEDDINGS_MODEL,
                dashscope_api_key=settings.DASH_SCOPE_API_KEY
            )
        elif embeddings_provider == "ollama":
            if not settings.OLLAMA_EMBEDDINGS_MODEL:
                raise ValueError("OLLAMA_EMBEDDINGS_MODEL is not set in the environment variables.")
            return OllamaEmbeddings(
                model=settings.OLLAMA_EMBEDDINGS_MODEL,
                base_url=settings.OLLAMA_API_BASE
            )

        # Extend with other providers:
        # elif embeddings_provider == "another_provider":
        #     return AnotherEmbeddingClass(...)
        else:
            raise ValueError(f"Unsupported embeddings provider: {embeddings_provider}")
