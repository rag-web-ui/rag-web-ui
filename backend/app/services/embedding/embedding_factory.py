from app.core.config import settings
from langchain_openai import OpenAIEmbeddings
# If you plan on adding other embeddings, import them here
# from some_other_module import AnotherEmbeddingClass
from langchain_community.embeddings import DashScopeEmbeddings


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
                openai_api_base=settings.OPENAI_API_BASE
            )
        elif embeddings_provider == "dashscope":
            return DashScopeEmbeddings(
                model=settings.EMBEDDINGS_MODEL,
                dashscope_api_key=settings.OPENAI_API_KEY
            )

        # Extend with other providers:
        # elif embeddings_provider == "another_provider":
        #     return AnotherEmbeddingClass(...)
        else:
            raise ValueError(f"Unsupported embeddings provider: {embeddings_provider}")
