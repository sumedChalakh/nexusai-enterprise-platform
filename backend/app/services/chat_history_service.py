from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession, ChatSessionMessage


def create_session(db: Session, user_id, title: str = "New chat") -> ChatSession:
    session = ChatSession(user_id=str(user_id), title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def add_message(db: Session, session_id, role: str, content: str) -> ChatSessionMessage:
    message = ChatSessionMessage(session_id=str(session_id), role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages(db: Session, session_id, limit: int = 50) -> list[ChatSessionMessage]:
    q = (
        select(ChatSessionMessage)
        .where(ChatSessionMessage.session_id == str(session_id))
        .order_by(ChatSessionMessage.created_at.desc())
        .limit(limit)
    )
    rows = db.execute(q).scalars().all()
    return list(reversed(rows))


def list_sessions(db: Session, user_id) -> list[ChatSession]:
    q = (
        select(ChatSession)
        .where(ChatSession.user_id == str(user_id))
        .order_by(ChatSession.created_at.desc())
    )
    return db.execute(q).scalars().all()


def format_for_llm(msgs: list[ChatSessionMessage]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in msgs]
