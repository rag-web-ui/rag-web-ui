from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Web UI"  # Project name
    VERSION: str = "0.1.0"  # Project version
    API_V1_STR: str = "/api"  # API version string

    # General configuration
    # Note: keep auth enabled by default for safety; disable via `.env` when desired.
    AUTH_ENABLED: bool = True
    DEFAULT_USER_ID: str = "admin"

    # Document processing config
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    # Keep in sync with `.env.example` and frontend upload accept lists.
    SUPPORTED_EXTENSIONS: str = (
        ".pdf,.docx,.md,.txt,.pptx,.ppt,.xlsx,.xls"
    )

    @property
    def supported_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.SUPPORTED_EXTENSIONS.split(",") if ext.strip()]

    # MySQL settings
    MYSQL_SERVER: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "ragwebui"
    MYSQL_PASSWORD: str = "ragwebui"
    MYSQL_DATABASE: str = "ragwebui"
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
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # Chat Provider settings
    CHAT_PROVIDER: str = "openai"

    # Embeddings settings
    EMBEDDINGS_PROVIDER: str = "openai"

    # MinIO settings
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "documents"

    # OpenAI settings
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_API_KEY: str = "your-openai-api-key-here"
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_EMBEDDINGS_MODEL: str = "text-embedding-ada-002"

    # DashScope settings
    DASH_SCOPE_API_KEY: str = ""
    DASH_SCOPE_EMBEDDINGS_MODEL: str = ""

    # Vector Store settings
    VECTOR_STORE_TYPE: str = "chroma"

    # Chroma DB settings
    CHROMA_DB_HOST: str = "chromadb"
    CHROMA_DB_PORT: int = 8000

    # Qdrant DB settings
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_PREFER_GRPC: bool = True

    # Deepseek settings
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"  # 默认 API 地址
    DEEPSEEK_MODEL: str = "deepseek-chat"  # 默认模型名称

    # Ollama settings
    OLLAMA_API_BASE: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:7b"
    OLLAMA_EMBEDDINGS_MODEL: str = "nomic-embed-text"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
