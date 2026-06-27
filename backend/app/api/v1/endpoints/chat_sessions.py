from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.chat_session import ChatSession
from app.services import chat_history_service as history
from app.services.conv_memory_service import get_window, push_turn
from app.services.generation_service import generate
from app.services.user_isolation_service import require_session_owner

router = APIRouter(prefix="/chat", tags=["chat"])


class NewSessionRequest(BaseModel):
    title: str = "New chat"


class SessionMessageRequest(BaseModel):
    role: str
    content: str


class TurnRequest(BaseModel):
    message: str


@router.post("/sessions")
def new_session(
    req: NewSessionRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = history.create_session(db, user.id, req.title)
    return {"session_id": str(session.id), "title": session.title}


@router.get("/sessions")
def sessions(user=Depends(get_current_user), db: Session = Depends(get_db)):
    rows = history.list_sessions(db, user.id)
    return [
        {"session_id": str(s.id), "title": s.title, "created_at": s.created_at}
        for s in rows
    ]


@router.get("/sessions/{session_id}/messages")
def get_history(
    session: ChatSession = Depends(require_session_owner),
    db: Session = Depends(get_db),
):
    return history.format_for_llm(history.get_messages(db, session.id))


@router.post("/sessions/{session_id}/messages")
def post_message(
    req: SessionMessageRequest,
    session: ChatSession = Depends(require_session_owner),
    db: Session = Depends(get_db),
):
    message = history.add_message(db, session.id, req.role, req.content)
    return {"message_id": str(message.id)}


@router.post("/sessions/{session_id}/turn")
def chat_turn(
    req: TurnRequest,
    session: ChatSession = Depends(require_session_owner),
    db: Session = Depends(get_db),
):
    window = get_window(str(session.id))
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in window)
    reply = generate(f"{convo}\nuser: {req.message}\nassistant:")

    history.add_message(db, session.id, "user", req.message)
    history.add_message(db, session.id, "assistant", reply)
    push_turn(str(session.id), "user", req.message)
    push_turn(str(session.id), "assistant", reply)

    return {"reply": reply}
