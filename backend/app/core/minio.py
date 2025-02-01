import logging
from minio import Minio
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_minio_client() -> Minio:
    """
    Get a MinIO client instance.
    """
    logger.info("Creating MinIO client instance.")
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False  # Set to True if using HTTPS
    )

def init_minio():
    """
    Initialize MinIO by creating the bucket if it doesn't exist.
    """
    client = get_minio_client()
    logger.info(f"Checking if bucket {settings.MINIO_BUCKET_NAME} exists.")
    if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
        logger.info(f"Bucket {settings.MINIO_BUCKET_NAME} does not exist. Creating bucket.")
        client.make_bucket(settings.MINIO_BUCKET_NAME)
    else:
        logger.info(f"Bucket {settings.MINIO_BUCKET_NAME} already exists.")
