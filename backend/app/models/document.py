from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DocStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    chunking = "chunking"
    chunked = "chunked"
    embedding = "embedding"
    embedded = "embedded"
    failed = "failed"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_name = Column(String(255), nullable=False)
    s3_key = Column(String(500), nullable=False, unique=True)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, default=0)
    status = Column(Enum(DocStatus), default=DocStatus.uploaded, nullable=False)

    # Day 4: parsing
    extracted_text = Column(Text, nullable=True)
    word_count = Column(Integer, default=0)
    parse_error = Column(String(500), nullable=True)

    # Day 5: chunking
    chunk_count = Column(Integer, default=0)

    # Day 6: embedding
    embedded_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan",
                          order_by="DocumentChunk.chunk_index")
