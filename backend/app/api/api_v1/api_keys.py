from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app import models, schemas
from app.db.session import get_db
from app.services.api_key import APIKeyService
from app.api.api_v1.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[schemas.APIKey])
def read_api_keys(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Retrieve API keys.
    """
    api_keys = APIKeyService.get_api_keys(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )
    return api_keys

@router.post("/", response_model=schemas.APIKey)
def create_api_key(
    *,
    db: Session = Depends(get_db),
    api_key_in: schemas.APIKeyCreate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Create new API key.
    """
    api_key = APIKeyService.create_api_key(
        db=db, user_id=current_user.id, name=api_key_in.name
    )
    logger.info(f"API key created: {api_key.key} for user {current_user.id}")
    return api_key

@router.put("/{id}", response_model=schemas.APIKey)
def update_api_key(
    *,
    db: Session = Depends(get_db),
    id: int,
    api_key_in: schemas.APIKeyUpdate,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Update API key.
    """
    api_key = APIKeyService.get_api_key(db=db, api_key_id=id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    if api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    api_key = APIKeyService.update_api_key(db=db, api_key=api_key, update_data=api_key_in)
    logger.info(f"API key updated: {api_key.key} for user {current_user.id}")
    return api_key

@router.delete("/{id}", response_model=schemas.APIKey)
def delete_api_key(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: models.User = Depends(get_current_user),
) -> Any:
    """
    Delete API key.
    """
    api_key = APIKeyService.get_api_key(db=db, api_key_id=id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    if api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    APIKeyService.delete_api_key(db=db, api_key=api_key)
    logger.info(f"API key deleted: {api_key.key} for user {current_user.id}")
    return api_key
