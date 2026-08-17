from typing import Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from app.core.config import settings


class LLMFactory:
    @staticmethod
    def create(
        provider: Optional[str] = None,
        temperature: float = 0,
        streaming: bool = True,
    ) -> BaseChatModel:
        """Create an LLM instance based on the configured chat provider."""
        provider = provider or settings.CHAT_PROVIDER

        if provider.lower() == "openai":
            return ChatOpenAI(
                temperature=temperature,
                streaming=streaming,
                model=settings.OPENAI_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE
            )
        elif provider.lower() == "deepseek":
            return ChatDeepSeek(
                temperature=temperature,
                streaming=streaming,
                model=settings.DEEPSEEK_MODEL,
                api_key=settings.DEEPSEEK_API_KEY,
                api_base=settings.DEEPSEEK_API_BASE
            )
        elif provider.lower() == "ollama":
            return LLMFactory._create_ollama(temperature)
        elif provider.lower() == "minimax":
            # MiniMax API requires temperature in (0.0, 1.0]; clamp to [0.01, 1.0]
            clamped_temperature = max(0.01, min(temperature, 1.0))
            return ChatOpenAI(
                temperature=clamped_temperature,
                streaming=streaming,
                model=settings.MINIMAX_MODEL,
                openai_api_key=settings.MINIMAX_API_KEY,
                openai_api_base=settings.MINIMAX_API_BASE
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def _create_ollama(temperature: float) -> ChatOllama:
        """Build a ChatOllama client from .env settings."""
        ollama_kwargs: dict[str, Any] = {
            "model": settings.OLLAMA_MODEL,
            "base_url": settings.OLLAMA_API_BASE,
            "temperature": (
                settings.OLLAMA_TEMPERATURE
                if settings.OLLAMA_TEMPERATURE is not None
                else temperature
            ),
        }
        if settings.OLLAMA_NUM_CTX is not None:
            ollama_kwargs["num_ctx"] = settings.OLLAMA_NUM_CTX
        if settings.OLLAMA_NUM_PREDICT is not None:
            ollama_kwargs["num_predict"] = settings.OLLAMA_NUM_PREDICT
        if settings.OLLAMA_KEEP_ALIVE:
            ollama_kwargs["keep_alive"] = settings.OLLAMA_KEEP_ALIVE
        if settings.OLLAMA_TOP_K is not None:
            ollama_kwargs["top_k"] = settings.OLLAMA_TOP_K
        if settings.OLLAMA_TOP_P is not None:
            ollama_kwargs["top_p"] = settings.OLLAMA_TOP_P
        if settings.ollama_client_kwargs:
            ollama_kwargs["client_kwargs"] = settings.ollama_client_kwargs
        return ChatOllama(**ollama_kwargs)
