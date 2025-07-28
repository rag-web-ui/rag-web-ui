import logging
import tempfile
import os
import hashlib
import requests
from urllib.parse import urlparse
from typing import Optional, List
from io import BytesIO
import whisper
from faster_whisper import WhisperModel
from sqlalchemy.orm import Session
import yt_dlp
from app.db.session import get_db
from app.models.knowledge import ProcessingTask, DocumentUpload, Document
from app.core.minio import get_minio_client
from app.core.config import settings
from app.services.document_processor import process_document

logger = logging.getLogger(__name__)

def get_filename_from_url(url: str) -> str:
    """Extract filename from URL, with fallback to generated name"""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)

    # If no filename in URL, generate one
    if not filename or '.' not in filename:
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        filename = f"video_{url_hash}.mp4"

    return filename

def get_video_content_type(filename: str) -> str:
    """Get content type based on file extension"""
    ext = os.path.splitext(filename)[1].lower()
    content_types = {
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.webm': 'video/webm',
        '.mkv': 'video/x-matroska',
        '.flv': 'video/x-flv'
    }
    return content_types.get(ext, 'video/mp4')

def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube URL"""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
    parsed = urlparse(url)
    return any(domain in parsed.netloc.lower() for domain in youtube_domains)

async def download_video_from_url(url: str, kb_id: int, db: Session) -> dict:
    """Download video from URL and create upload record (supports YouTube)"""
    try:
        # Get timeout from environment or use default
        timeout = int(os.getenv('VIDEO_DOWNLOAD_TIMEOUT', 300))
        max_size_mb = int(os.getenv('MAX_VIDEO_SIZE_MB', 500))
        max_size_bytes = max_size_mb * 1024 * 1024

        if is_youtube_url(url):
            # Handle YouTube URLs with yt-dlp
            logger = logging.getLogger(__name__)
            logger.info(f"Detected YouTube URL, using yt-dlp: {url}")

            # Create temporary directory for download
            temp_dir = tempfile.mkdtemp()
            temp_filename = 'video.%(ext)s'
            temp_path = os.path.join(temp_dir, temp_filename)

            ydl_opts = {
                'outtmpl': temp_path,
                'format': 'best[ext=mp4]/best[height<=720]/best',
                'noplaylist': True,
                'extract_flat': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Get video info
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
                    duration = info.get('duration', 0)

                    logger.info(f"YouTube video: {title} (Duration: {duration}s)")

                    # Download the video
                    ydl.download([url])

                    # Find the downloaded file (yt-dlp creates the actual filename)
                    downloaded_files = [f for f in os.listdir(temp_dir) if f.startswith('video.')]
                    if not downloaded_files:
                        raise Exception("No video file was downloaded")

                    actual_file_path = os.path.join(temp_dir, downloaded_files[0])

                    # Read the downloaded file
                    with open(actual_file_path, 'rb') as f:
                        content = f.read()

                    # Clean up temp files
                    import shutil
                    shutil.rmtree(temp_dir)

                    # Generate filename from title
                    safe_title = "".join(c for c in title if c.isalnum() or c in ('-', '_', ' ')).strip()
                    filename = f"{safe_title[:50]}.mp4"  # Limit length
                    content_type = 'video/mp4'

            except Exception as e:
                # Clean up temp directory
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                raise Exception(f"Failed to download YouTube video: {str(e)}")
        else:
            # Handle direct video URLs
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()

            # Get filename and content info
            filename = get_filename_from_url(url)
            content_type = get_video_content_type(filename)

            # Read content
            content = response.content

        # Check content size
        if len(content) > max_size_bytes:
            raise Exception(f"Video file too large: {len(content) / (1024*1024):.1f}MB (max: {max_size_mb}MB)")

        file_hash = hashlib.sha256(content).hexdigest()
        file_size = len(content)

        # Check for duplicates
        existing_upload = db.query(DocumentUpload).filter(
            DocumentUpload.knowledge_base_id == kb_id,
            DocumentUpload.file_hash == file_hash
        ).first()

        if existing_upload:
            return {
                "upload_id": existing_upload.id,
                "file_name": filename,
                "status": "exists",
                "message": "Video already exists",
                "skip_processing": True
            }

        # Upload to MinIO
        temp_path = f"kb_{kb_id}/videos/temp/{filename}"
        minio_client = get_minio_client()

        from io import BytesIO
        minio_client.put_object(
            bucket_name=settings.MINIO_BUCKET_NAME,
            object_name=temp_path,
            data=BytesIO(content),
            length=file_size,
            content_type=content_type
        )

        # Create upload record
        upload = DocumentUpload(
            knowledge_base_id=kb_id,
            file_name=filename,
            file_hash=file_hash,
            file_size=file_size,
            content_type=content_type,
            temp_path=temp_path
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)

        return {
            "upload_id": upload.id,
            "file_name": filename,
            "temp_path": temp_path,
            "status": "pending",
            "skip_processing": False
        }

    except requests.RequestException as e:
        logger.error(f"Failed to download video from URL {url}: {str(e)}")
        raise Exception(f"Failed to download video: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing video URL {url}: {str(e)}")
        raise

async def transcribe_video_background(
    video_path: str,
    file_name: str,
    kb_id: int,
    task_id: int,
    upload_id: int
):
    """Background task to transcribe video and create document"""
    db = next(get_db())
    
    try:
        # Update task status
        task = db.query(ProcessingTask).filter(ProcessingTask.id == task_id).first()
        if task:
            task.status = "processing"
            db.commit()
        
        # Download video from MinIO
        minio_client = get_minio_client()
        
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file_name)[1], delete=False) as temp_video:
            try:
                minio_client.fget_object(
                    settings.MINIO_BUCKET_NAME,
                    video_path,
                    temp_video.name
                )
                
                # Load Faster Whisper model and transcribe
                whisper_model = os.getenv('WHISPER_MODEL', 'base')
                device = "cuda" if os.getenv('WHISPER_USE_GPU', 'false').lower() == 'true' else "cpu"
                compute_type = "float16" if device == "cuda" else "int8"

                logger.info(f"Loading Whisper model: {whisper_model} on {device}")
                model = WhisperModel(whisper_model, device=device, compute_type=compute_type)

                # Transcribe video
                segments, info = model.transcribe(temp_video.name)
                transcript_text = " ".join([segment.text for segment in segments])

                logger.info(f"Transcription completed. Language: {info.language}, Duration: {info.duration:.2f}s")
                
                # Create transcript document (same path structure as regular documents)
                transcript_filename = f"{os.path.splitext(file_name)[0]}_transcript.txt"
                transcript_path = f"kb_{kb_id}/{transcript_filename}"
                
                # Upload transcript to MinIO
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_transcript:
                    temp_transcript.write(transcript_text)
                    temp_transcript.flush()
                    
                    minio_client.fput_object(
                        "documents",  # Same bucket as other documents
                        transcript_path,
                        temp_transcript.name,
                        content_type="text/plain"
                    )
                    
                    # Create document record (same as regular document upload)
                    file_hash = hashlib.sha256(transcript_text.encode('utf-8')).hexdigest()
                    document = Document(
                        knowledge_base_id=kb_id,
                        file_name=transcript_filename,
                        file_path=transcript_path,
                        file_size=len(transcript_text.encode('utf-8')),
                        content_type="text/plain",
                        file_hash=file_hash
                    )
                    db.add(document)
                    db.commit()
                    db.refresh(document)

                    # Link document to task
                    if task:
                        task.document_id = document.id
                        db.commit()
                    
                    # Process the transcript through document processor (same as other documents)
                    # This will chunk the text and add to vector store for RAG
                    try:
                        await process_document(
                            file_path=transcript_path,
                            file_name=transcript_filename,
                            kb_id=kb_id,
                            document_id=document.id,
                            chunk_size=1000,  # Default chunk size
                            chunk_overlap=200  # Default overlap
                        )

                        logger.info(f"Video transcript processed and added to knowledge base: {transcript_filename}")

                    except Exception as e:
                        logger.error(f"Failed to process transcript document: {str(e)}")
                        raise
                    
                    # Clean up temp files
                    os.unlink(temp_transcript.name)
                
            finally:
                # Clean up temp video file
                if os.path.exists(temp_video.name):
                    os.unlink(temp_video.name)
        
        # Update task status to completed
        if task:
            task.status = "completed"
            db.commit()
            
        logger.info(f"Video transcription completed for {file_name}")
        
    except Exception as e:
        logger.error(f"Video transcription failed for {file_name}: {str(e)}")
        
        # Update task status to failed
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
    
    finally:
        db.close()