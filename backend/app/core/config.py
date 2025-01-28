from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
import os
import json
from dotenv import load_dotenv

from app.services.openai.config import OpenAIConfig
from app.services.ollama.config import OllamaConfig

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Web UI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    
    # CORS settings
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        cors_origins = os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:3000"]')
        try:
            # Attempt to parse the JSON string
            origins = json.loads(cors_origins)
            # If the list contains "*", return ["*"]
            if isinstance(origins, list) and "*" in origins:
                return ["*"]
            # Otherwise, return the original list
            return origins if isinstance(origins, list) else [origins]
        except json.JSONDecodeError:
            # If parsing fails, return the default value
            return ["http://localhost:3000"]
    
    # MySQL settings
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "ragwebui")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "ragwebui")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "ragwebui")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}/{self.MYSQL_DATABASE}"

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # Vector DB settings
    CHROMA_DB_HOST: str = os.getenv("CHROMA_DB_HOST", "localhost")
    CHROMA_DB_PORT: int = int(os.getenv("CHROMA_DB_PORT", "8001"))

    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "documents")

    # OpenAI settings
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    
    # Vector Store Settings
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "chroma")
    VECTOR_STORE_URL: str = os.getenv("VECTOR_STORE_URL", "http://localhost:6333")
    VECTOR_STORE_PREFER_GRPC: bool = os.getenv("VECTOR_STORE_PREFER_GRPC", "true").lower() == "true"
    
    def get_service_config(self, service_type: str) -> Dict[str, Any]:
        """Get service configuration based on type
        
        Args:
            service_type: Type of service ("openai" or "ollama")
            
        Returns:
            Service configuration dictionary
        """
        if service_type == "openai":
            return {
                "api_key": self.OPENAI_API_KEY,
                "api_base": self.OPENAI_API_BASE,
                "model": self.OPENAI_MODEL,
                "embedding_model": self.OPENAI_EMBEDDING_MODEL
            }
        elif service_type == "ollama":
            return {
                "base_url": self.OLLAMA_BASE_URL,
                "model": self.OLLAMA_MODEL,
                "embedding_model": self.OLLAMA_EMBEDDING_MODEL
            }
        else:
            raise ValueError(f"Unknown service type: {service_type}")
    
    def create_openai_config(self) -> OpenAIConfig:
        """Create OpenAI configuration"""
        return OpenAIConfig(**self.get_service_config("openai"))
    
    def create_ollama_config(self) -> OllamaConfig:
        """Create Ollama configuration"""
        return OllamaConfig(**self.get_service_config("ollama"))
    
settings = Settings() 