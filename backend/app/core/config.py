from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "RAG Web UI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    
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
    CHROMA_DB_PORT: int = int(os.getenv("CHROMA_DB_PORT", "8000"))

    # MinIO
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "documents")

    # OpenAI settings
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings() 