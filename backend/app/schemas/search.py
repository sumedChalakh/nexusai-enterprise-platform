from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):
    query: str
    document_id: Optional[int] = None
    limit: int = 5


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    chunk_index: int
    text: str
    page_number: Optional[int] = None
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    count: int


class EmbeddingStatsResponse(BaseModel):
    document_id: int
    chunk_count: int
    embedded_count: int
    is_fully_embedded: bool
