from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.chunk import ChunkOut, ChunkList, ChunkStats
from app.services.processing_service import chunk_document_task

router = APIRouter(prefix="/documents/{doc_id}/chunks", tags=["chunks"])


def _owned_doc(doc_id: int, user_id: int, db: Session) -> Document:
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == user_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.get("/", response_model=ChunkList)
def list_chunks(
    doc_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _owned_doc(doc_id, current_user.id, db)
    if doc.status not in ("chunked", "embedding", "embedded"):
        raise HTTPException(
            status_code=425,
            detail=f"Document chunks not ready (status: {doc.status})"
        )
    total = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).count()
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == doc_id)
        .order_by(DocumentChunk.chunk_index)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"document_id": doc_id, "total_chunks": total, "chunks": chunks}


@router.get("/stats", response_model=ChunkStats)
def chunk_stats(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _owned_doc(doc_id, current_user.id, db)
    chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).all()

    if not chunks:
        return ChunkStats(
            document_id=doc_id, chunk_count=0, total_tokens=0,
            avg_tokens=0.0, min_tokens=0, max_tokens=0, pages_covered=0,
        )

    tokens = [c.token_estimate for c in chunks]
    pages = {c.page_number for c in chunks if c.page_number is not None}

    return ChunkStats(
        document_id=doc_id,
        chunk_count=len(chunks),
        total_tokens=sum(tokens),
        avg_tokens=round(sum(tokens) / len(tokens), 1),
        min_tokens=min(tokens),
        max_tokens=max(tokens),
        pages_covered=len(pages),
    )


@router.get("/{chunk_index}", response_model=ChunkOut)
def get_chunk(
    doc_id: int,
    chunk_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _owned_doc(doc_id, current_user.id, db)
    chunk = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == doc_id,
        DocumentChunk.chunk_index == chunk_index,
    ).first()
    if not chunk:
        raise HTTPException(status_code=404, detail=f"Chunk {chunk_index} not found")
    return chunk


@router.post("/rechunk", response_model=dict)
def rechunk_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _owned_doc(doc_id, current_user.id, db)
    if not doc.extracted_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text to chunk")
    background_tasks.add_task(chunk_document_task, doc_id)
    return {"message": "Rechunking started", "doc_id": doc_id}
