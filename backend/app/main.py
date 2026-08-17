import logging

from fastapi import FastAPI

from app.api.api_v1.api import api_router
from app.api.openapi.api import router as openapi_router
from app.core.config import settings
from app.core.minio import init_minio
from app.db.session import SessionLocal
from app.services.user import get_or_create_default_user
from app.startup.migarate import DatabaseMigrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(openapi_router, prefix="/openapi")


@app.on_event("startup")
async def startup_event():
    # Initialize MinIO
    init_minio()
    # Run database migrations
    migrator = DatabaseMigrator(settings.get_database_url)
    migrator.run_migrations()
    if settings.BYPASS_AUTH:
        db = SessionLocal()
        try:
            user = get_or_create_default_user(db)
            logging.getLogger(__name__).info(
                "Auth bypass enabled; default user is ready: %s", user.username
            )
        finally:
            db.close()


@app.get("/")
def root():
    return {"message": "Welcome to RAG Web UI API"}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }
