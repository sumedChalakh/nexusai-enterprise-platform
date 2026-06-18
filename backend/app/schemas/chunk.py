from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChunkOut(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    text: str
    start_char: int
    end_char: int
    page_number: Optional[int] = None
    token_estimate: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChunkList(BaseModel):
    document_id: int
    total_chunks: int
    chunks: list[ChunkOut]


class ChunkStats(BaseModel):
    document_id: int
    chunk_count: int
    total_tokens: int
    avg_tokens: float
    min_tokens: int
    max_tokens: int
    pages_covered: int
