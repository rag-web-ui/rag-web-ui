from fastapi import APIRouter
from app.api.api_v1 import auth, knowledge_base, chat, api_keys

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(knowledge_base.router, prefix="/knowledge-base", tags=["knowledge-base"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(api_keys.router, prefix="/agents", tags=["agents"]) 
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"]) 