from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.constants import FeedbackRating


class MessageFeedbackCreate(BaseModel):
    rating: FeedbackRating
    comment: Optional[str] = Field(default=None, max_length=1000)


class MessageFeedbackResponse(BaseModel):
    id: int
    message_id: int
    chat_id: int
    rating: FeedbackRating
    comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
