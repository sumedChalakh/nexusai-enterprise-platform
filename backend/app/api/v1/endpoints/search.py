from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.search import SearchRequest, SearchResponse, EmbeddingStatsResponse
from app.services.embedding_service import embed_query
from app.services import qdrant_service
from app.services.processing_service import embed_document_task

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/", response_model=SearchResponse)
def semantic_search(
    body: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.document_id is not None:
        doc = db.query(Document).filter(
            Document.id == body.document_id, Document.user_id == current_user.id
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

    try:
        vector = embed_query(body.query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Embedding service error: {e}")

    results = qdrant_service.search(
        query_vector=vector,
        user_id=current_user.id,
        document_id=body.document_id,
        limit=body.limit,
    )

    return {"query": body.query, "results": results, "count": len(results)}


@router.get("/documents/{doc_id}/embedding-status", response_model=EmbeddingStatsResponse)
def embedding_status(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "document_id": doc.id,
        "chunk_count": doc.chunk_count,
        "embedded_count": doc.embedded_count,
        "is_fully_embedded": doc.embedded_count == doc.chunk_count and doc.chunk_count > 0,
    }


@router.post("/documents/{doc_id}/re-embed", response_model=dict)
def re_embed_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == current_user.id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.chunk_count == 0:
        raise HTTPException(status_code=400, detail="Document has no chunks to embed")

    background_tasks.add_task(embed_document_task, doc_id)
    return {"message": "Re-embedding started", "doc_id": doc_id}
