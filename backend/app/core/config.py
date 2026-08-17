import os
from typing import Any, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Web UI"  # Project name
    VERSION: str = "0.1.0"  # Project version
    API_V1_STR: str = "/api"  # API version string

    # MySQL settings
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "ragwebui")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "ragwebui")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "ragwebui")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        return (
            f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

    # Auth bypass: when true, skip login and use the default user
    BYPASS_AUTH: bool = os.getenv("BYPASS_AUTH", "false").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )
    DEFAULT_USERNAME: str = os.getenv("DEFAULT_USERNAME", "admin")
    DEFAULT_EMAIL: str = os.getenv("DEFAULT_EMAIL", "admin@example.com")
    DEFAULT_PASSWORD: str = os.getenv("DEFAULT_PASSWORD", "admin")

    @field_validator("BYPASS_AUTH", mode="before")
    @classmethod
    def parse_bypass_auth(cls, value: Any) -> bool:
        """Accept true/1/yes/on from .env for auth bypass."""
        if isinstance(value, bool):
            return value
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes", "on")
        return bool(value)

    @field_validator("OLLAMA_THINK", mode="before")
    @classmethod
    def parse_ollama_think(cls, value: Any) -> bool:
        """Accept true/1/yes/on from .env; default is false so tokens stream immediately."""
        if isinstance(value, bool):
            return value
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return False
        if isinstance(value, str):
            return value.strip().lower() in ("true", "1", "yes", "on")
        return bool(value)

    # Chat Provider settings
    CHAT_PROVIDER: str = os.getenv("CHAT_PROVIDER", "ollama")

    # Embeddings settings
    EMBEDDINGS_PROVIDER: str = os.getenv("EMBEDDINGS_PROVIDER", "ollama")

    # MinIO settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "documents")

    # OpenAI settings
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_EMBEDDINGS_MODEL: str = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-ada-002")

    # DashScope settings
    DASH_SCOPE_API_KEY: str = os.getenv("DASH_SCOPE_API_KEY", "")
    DASH_SCOPE_EMBEDDINGS_MODEL: str = os.getenv("DASH_SCOPE_EMBEDDINGS_MODEL", "")

    # Vector Store settings
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "chroma")

    # Chroma DB settings
    CHROMA_DB_HOST: str = os.getenv("CHROMA_DB_HOST", "chromadb")
    CHROMA_DB_PORT: int = int(os.getenv("CHROMA_DB_PORT", "8000"))

    # Qdrant DB settings
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_PREFER_GRPC: bool = os.getenv("QDRANT_PREFER_GRPC", "true").lower() == "true"

    # Deepseek settings
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"  # 默认 API 地址
    DEEPSEEK_MODEL: str = "deepseek-chat"  # 默认模型名称

    # MiniMax settings
    MINIMAX_API_KEY: str = ""
    MINIMAX_API_BASE: str = "https://api.minimax.io/v1"
    MINIMAX_MODEL: str = "MiniMax-M2.7"

    # Ollama settings (required when CHAT_PROVIDER=ollama or EMBEDDINGS_PROVIDER=ollama)
    OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    OLLAMA_EMBEDDINGS_MODEL: str = os.getenv(
        "OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text"
    )
    OLLAMA_TEMPERATURE: Optional[float] = None
    OLLAMA_NUM_CTX: Optional[int] = None
    OLLAMA_NUM_PREDICT: Optional[int] = None
    OLLAMA_KEEP_ALIVE: Optional[str] = None
    OLLAMA_TOP_K: Optional[int] = None
    OLLAMA_TOP_P: Optional[float] = None
    OLLAMA_TIMEOUT: Optional[float] = None
    # Qwen 3.5 and similar models hide tokens in a thinking phase unless this is false.
    OLLAMA_THINK: bool = False

    @field_validator(
        "OLLAMA_TEMPERATURE",
        "OLLAMA_NUM_CTX",
        "OLLAMA_NUM_PREDICT",
        "OLLAMA_KEEP_ALIVE",
        "OLLAMA_TOP_K",
        "OLLAMA_TOP_P",
        "OLLAMA_TIMEOUT",
        mode="before",
    )
    @classmethod
    def empty_ollama_value_to_none(cls, value: Any) -> Any:
        """Treat blank .env values as unset so optional Ollama fields stay optional."""
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @property
    def ollama_client_kwargs(self) -> dict[str, Any]:
        """HTTP client options for the Ollama LangChain clients."""
        timeout = self.OLLAMA_TIMEOUT if self.OLLAMA_TIMEOUT is not None else 300.0
        return {"timeout": timeout}

    # HuggingFace settings
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_EMBEDDINGS_MODEL: str = os.getenv(
        "HUGGINGFACE_EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )

    class Config:
        env_file = ".env"


settings = Settings()
