from pydantic import BaseModel, Field

class OpenAIConfig(BaseModel):
    """OpenAI service configuration"""
    api_key: str = Field(..., description="OpenAI API key")
    api_base: str = Field(..., description="OpenAI API base URL")
    model: str = Field(..., description="OpenAI chat model name")
    embedding_model: str = Field(..., description="OpenAI embeddings model name") 