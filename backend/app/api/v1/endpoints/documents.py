from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import (
    DocumentOut, DocumentWithURL, DocumentWithText,
    DocumentList, DeleteResponse, ParseStatusResponse,
)
from app.services import s3_service
from app.services.processing_service import process_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = await s3_service.upload_file(file, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    doc = Document(
        user_id=current_user.id,
        original_name=result["original_name"],
        s3_key=result["s3_key"],
        content_type=result["content_type"],
        size_bytes=result["size_bytes"],
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Kick off background parsing immediately after upload
    background_tasks.add_task(process_document, doc.id)

    return doc


@router.get("/", response_model=DocumentList)
def list_documents(
    skip: int = 0,
    limit: int = 20,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Document).filter(Document.user_id == current_user.id)
    if status_filter:
        q = q.filter(Document.status == status_filter)
    total = q.count()
    docs = q.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "documents": docs}


@router.get("/{doc_id}", response_model=DocumentWithURL)
def get_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_owned_doc(doc_id, current_user.id, db)
    url = s3_service.get_presigned_url(doc.s3_key)
    return {**doc.__dict__, "presigned_url": url}


@router.get("/{doc_id}/text", response_model=DocumentWithText)
def get_document_text(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_owned_doc(doc_id, current_user.id, db)
    if doc.status != "ready":
        raise HTTPException(
            status_code=425,
            detail=f"Document is not ready yet (status: {doc.status})",
        )
    return doc


@router.get("/{doc_id}/status", response_model=ParseStatusResponse)
def get_parse_status(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_owned_doc(doc_id, current_user.id, db)
    return {
        "doc_id": doc.id,
        "status": doc.status,
        "word_count": doc.word_count,
        "parse_error": doc.parse_error,
    }


@router.post("/{doc_id}/reparse", response_model=ParseStatusResponse)
def reparse_document(
    doc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_owned_doc(doc_id, current_user.id, db)
    doc.status = "uploaded"
    doc.extracted_text = None
    doc.parse_error = None
    doc.word_count = 0
    db.commit()
    background_tasks.add_task(process_document, doc.id)
    return {"doc_id": doc.id, "status": doc.status, "word_count": 0, "parse_error": None}


@router.delete("/{doc_id}", response_model=DeleteResponse)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = _get_owned_doc(doc_id, current_user.id, db)
    s3_service.delete_file(doc.s3_key)
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted", "deleted_id": doc_id}


# ── helpers ─────────────────────────────────────────────────────────────────

def _get_owned_doc(doc_id: int, user_id: int, db: Session) -> Document:
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == user_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
