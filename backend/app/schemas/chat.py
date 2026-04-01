from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MessageBase(BaseModel):
    content: str
    role: str

class MessageCreate(MessageBase):
    chat_id: int

class MessageResponse(MessageBase):
    id: int
    chat_id: int
    feedback_type: Optional[str] = None
    feedback_note: Optional[str] = None
    corrected_answer: Optional[str] = None
    feedback_query: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatBase(BaseModel):
    title: str

class ChatCreate(ChatBase):
    knowledge_base_ids: List[int]

class ChatUpdate(ChatBase):
    knowledge_base_ids: Optional[List[int]] = None

class ChatResponse(ChatBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    knowledge_base_ids: List[int] = []

    class Config:
        from_attributes = True 


class MessageFeedbackRequest(BaseModel):
    feedback_type: str
    user_query: str
    assistant_response: str
    corrected_answer: Optional[str] = None
    feedback_note: Optional[str] = None