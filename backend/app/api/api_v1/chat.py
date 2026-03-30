from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from app.db.session import get_db
from app.models.user import User
from app.models.chat import Chat, Message
from app.models.knowledge import KnowledgeBase
from app.schemas.chat import (
    ChatCreate,
    ChatResponse,
    ChatUpdate,
    MessageFeedbackRequest,
    MessageCreate,
    MessageResponse,
)
from app.core.security import get_current_user
from app.services.chat_service import generate_response

router = APIRouter()

@router.post("/", response_model=ChatResponse)
def create_chat(
    *,
    db: Session = Depends(get_db),
    chat_in: ChatCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    # Verify knowledge bases exist and belong to user
    knowledge_bases = (
        db.query(KnowledgeBase)
        .filter(
            KnowledgeBase.id.in_(chat_in.knowledge_base_ids),
            KnowledgeBase.user_id == current_user.id
        )
        .all()
    )
    if len(knowledge_bases) != len(chat_in.knowledge_base_ids):
        raise HTTPException(
            status_code=400,
            detail="One or more knowledge bases not found"
        )
    
    chat = Chat(
        title=chat_in.title,
        user_id=current_user.id,
    )
    chat.knowledge_bases = knowledge_bases
    
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

@router.get("/", response_model=List[ChatResponse])
def get_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    chats = (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return chats

@router.get("/{chat_id}", response_model=ChatResponse)
def get_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/{chat_id}/messages")
async def create_message(
    *,
    db: Session = Depends(get_db),
    chat_id: int,
    messages: dict,
    current_user: User = Depends(get_current_user)
) -> StreamingResponse:
    chat = (
        db.query(Chat)
        .options(joinedload(Chat.knowledge_bases))
        .filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Get the last user message
    last_message = messages["messages"][-1]
    if last_message["role"] != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")
    
    # Get knowledge base IDs
    knowledge_base_ids = [kb.id for kb in chat.knowledge_bases]

    async def response_stream():
        async for chunk in generate_response(
            query=last_message["content"],
            messages=messages,
            knowledge_base_ids=knowledge_base_ids,
            chat_id=chat_id,
            db=db,
            user_id=current_user.id,
        ):
            yield chunk

    return StreamingResponse(
        response_stream(),
        media_type="text/event-stream",
        headers={
            "x-vercel-ai-data-stream": "v1"
        }
    )

@router.delete("/{chat_id}")
def delete_chat(
    *,
    db: Session = Depends(get_db),
    chat_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    chat = (
        db.query(Chat)
        .filter(
            Chat.id == chat_id,
            Chat.user_id == current_user.id
        )
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    db.delete(chat)
    db.commit()
    return {"status": "success"}


@router.post("/{chat_id}/messages/{message_id}/feedback")
def message_feedback(
    *,
    db: Session = Depends(get_db),
    chat_id: int,
    message_id: int,
    feedback: MessageFeedbackRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    chat = (
        db.query(Chat)
        .filter(Chat.id == chat_id, Chat.user_id == current_user.id)
        .first()
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    message = (
        db.query(Message)
        .filter(
            Message.id == message_id,
            Message.chat_id == chat_id,
            Message.role == "assistant",
        )
        .first()
    )
    if not message:
        raise HTTPException(status_code=404, detail="Assistant message not found")

    feedback_type = feedback.feedback_type.strip().lower()
    if feedback_type not in {"up", "down"}:
        raise HTTPException(status_code=400, detail="feedback_type must be 'up' or 'down'")

    resolved_answer = None
    if feedback_type == "up":
        resolved_answer = feedback.assistant_response.strip()
    else:
        resolved_answer = (feedback.corrected_answer or "").strip() or (
            feedback.feedback_note or ""
        ).strip()
        if not resolved_answer:
            raise HTTPException(
                status_code=400,
                detail="Please provide corrected_answer or feedback_note for thumbs down",
            )

    message.feedback_type = feedback_type
    message.feedback_note = (feedback.feedback_note or "").strip() or None
    message.corrected_answer = resolved_answer
    message.feedback_query = feedback.user_query.strip()

    db.commit()
    return {"status": "success"}