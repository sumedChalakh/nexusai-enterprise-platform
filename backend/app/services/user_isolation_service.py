from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.chat_session import ChatSession


def require_session_owner(
    session_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatSession:
    session = db.get(ChatSession, str(session_id))
    if session is None:
        raise HTTPException(404, "session not found")
    if str(session.user_id) != str(user.id):
        raise HTTPException(403, "not your session")
    return session


def scoped_s3_key(user_id: int | str, filename: str) -> str:
    return f"users/{user_id}/docs/{filename}"


def assert_owns_s3_key(user_id: int | str, key: str) -> None:
    if not key.startswith(f"users/{user_id}/"):
        raise HTTPException(403, "not your document")


def qdrant_user_filter(user_id: int | str) -> dict:
    return {"must": [{"key": "user_id", "match": {"value": user_id}}]}


def assert_owns_doc(db: Session, user_id: int | str, doc_id: int | str) -> None:
    from app.models.document import Document

    doc = db.get(Document, int(doc_id))
    if doc is None or str(doc.user_id) != str(user_id):
        raise HTTPException(403, "not your document")
