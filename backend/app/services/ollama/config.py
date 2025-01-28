from pydantic import BaseModel, Field

class OllamaConfig(BaseModel):
    """Ollama service configuration"""
    base_url: str = Field(..., description="Ollama API base URL")
    model: str = Field(..., description="Ollama chat model name")
    embedding_model: str = Field(..., description="Ollama embeddings model name") 