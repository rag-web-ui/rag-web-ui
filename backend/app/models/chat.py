from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Table
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin

# Association table for many-to-many relationship between Chat and KnowledgeBase
chat_knowledge_bases = Table(
    "chat_knowledge_bases",
    Base.metadata,
    Column("chat_id", Integer, ForeignKey("chats.id"), primary_key=True),
    Column("knowledge_base_id", Integer, ForeignKey("knowledge_bases.id"), primary_key=True),
)

class Chat(Base, TimestampMixin):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    user = relationship("User", back_populates="chats")
    knowledge_bases = relationship(
        "KnowledgeBase",
        secondary=chat_knowledge_bases,
        backref="chats"
    )

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(LONGTEXT, nullable=False)
    role = Column(String(50), nullable=False)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)

    # Relationships
    chat = relationship("Chat", back_populates="messages") 