from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)

    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_chunk_ids = Column(ARRAY(Integer), default=list)  # which chunks grounded this answer

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chat_messages")
    document = relationship("Document")
