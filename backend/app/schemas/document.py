from pydantic import BaseModel, computed_field
from datetime import datetime
from typing import Optional
from app.models.document import DocStatus


class DocumentOut(BaseModel):
    id: int
    original_name: str
    s3_key: str
    content_type: str
    size_bytes: int
    status: DocStatus
    word_count: int
    parse_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentWithURL(DocumentOut):
    presigned_url: str


class DocumentWithText(DocumentOut):
    extracted_text: Optional[str] = None

    @computed_field
    @property
    def preview(self) -> str:
        if not self.extracted_text:
            return ""
        return self.extracted_text[:500] + ("…" if len(self.extracted_text) > 500 else "")


class DocumentList(BaseModel):
    total: int
    documents: list[DocumentOut]


class DeleteResponse(BaseModel):
    message: str
    deleted_id: int


class ParseStatusResponse(BaseModel):
    doc_id: int
    status: DocStatus
    word_count: int
    parse_error: Optional[str] = None
