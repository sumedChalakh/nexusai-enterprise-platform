import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.chat_message import ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services import rag_service

router = APIRouter(prefix="/chat", tags=["chat"])


def _validate_document(body: ChatRequest, user_id: int, db: Session) -> None:
    if body.document_id is not None:
        doc = db.query(Document).filter(
            Document.id == body.document_id, Document.user_id == user_id
        ).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")


@router.post("/ask", response_model=ChatResponse)
def ask_question(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    _validate_document(body, current_user.id, db)

    try:
        result = rag_service.ask(
            db=db,
            user_id=current_user.id,
            question=body.question,
            document_id=body.document_id,
            limit=body.limit,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return result


@router.post("/ask/stream")
def ask_question_stream(
    body: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    _validate_document(body, current_user.id, db)

    def event_generator():
        try:
            for event in rag_service.ask_stream(
                db=db,
                user_id=current_user.id,
                question=body.question,
                document_id=body.document_id,
                limit=body.limit,
            ):
                if event["type"] == "token":
                    yield f"data: {json.dumps({'token': event['data']})}\n\n"
                elif event["type"] == "sources":
                    yield f"data: {json.dumps({'sources': event['data']})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/history", response_model=ChatHistoryResponse)
def chat_history(
    skip: int = 0,
    limit: int = 20,
    document_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id)
    if document_id is not None:
        q = q.filter(ChatMessage.document_id == document_id)

    total = q.count()
    messages = (
        q.order_by(ChatMessage.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return {"total": total, "messages": messages}


@router.delete("/history/{chat_id}")
def delete_chat_message(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    msg = db.query(ChatMessage).filter(
        ChatMessage.id == chat_id, ChatMessage.user_id == current_user.id
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return {"message": "Deleted", "chat_id": chat_id}
