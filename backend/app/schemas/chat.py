from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatRequest(BaseModel):
    question: str
    document_id: Optional[int] = None
    limit: int = 5


class SourceOut(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    page_number: Optional[int] = None
    score: float
    text_preview: str


class ChatResponse(BaseModel):
    chat_id: int
    answer: str
    sources: list[SourceOut]


class ChatMessageOut(BaseModel):
    id: int
    document_id: Optional[int] = None
    question: str
    answer: str
    source_chunk_ids: list[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    total: int
    messages: list[ChatMessageOut]
