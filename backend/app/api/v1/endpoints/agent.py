from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.conv_memory_service import get_window, push_turn
from app.services.user_isolation_service import require_session_owner
from app.services.agents import run_master

router = APIRouter(prefix="/agent", tags=["agent"])


class MasterAskReq(BaseModel):
    question: str
    doc_id: str | None = None


@router.post("/sessions/{session_id}/ask")
def ask(req: MasterAskReq, session=Depends(require_session_owner)):
    history = get_window(str(session.id))

    result = run_master(user_id=str(session.user_id), question=req.question, doc_id=req.doc_id, chat_history=history)

    push_turn(str(session.id), "user", req.question)
    push_turn(str(session.id), "assistant", result["answer"] or "")

    return {"answer": result["answer"], "sources": result["sources"], "route": result["route"]}
