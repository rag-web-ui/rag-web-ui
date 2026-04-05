from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import OllamaLLM
from app.core.config import settings

class LLMFactory:
    @staticmethod
    def create(
        provider: Optional[str] = None,
        temperature: float = 0,
        streaming: bool = True,
    ) -> BaseChatModel:
        """
        Create a LLM instance based on the provider
        """
        # If no provider specified, use the one from settings
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
            # Initialize Ollama model
            return OllamaLLM(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_API_BASE,
                temperature=temperature,
                streaming=streaming
            )
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
        # Add more providers here as needed
        # elif provider.lower() == "anthropic":
        #     return ChatAnthropic(...)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")