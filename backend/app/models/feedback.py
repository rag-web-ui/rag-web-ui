from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class MessageFeedback(Base, TimestampMixin):
    """User rating of an assistant message, used to improve later answers."""

    __tablename__ = "message_feedback"
    __table_args__ = (
        UniqueConstraint("message_id", name="uq_message_feedback_message_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(
        Integer,
        ForeignKey("messages.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(String(16), nullable=False)
    question = Column(LONGTEXT, nullable=False)
    answer = Column(LONGTEXT, nullable=False)
    question_fingerprint = Column(String(64), nullable=False, index=True)
    comment = Column(String(1000), nullable=True)

    message = relationship("Message", back_populates="feedback")
    chat = relationship("Chat")
    user = relationship("User", back_populates="message_feedback")
