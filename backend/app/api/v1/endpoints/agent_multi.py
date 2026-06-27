from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.conv_memory_service import get_window, push_turn
from app.services.user_isolation_service import require_session_owner
from app.services.agents import run_multi_agent

router = APIRouter(prefix="/agent/multi", tags=["agent"])


class ComboAskReq(BaseModel):
    question: str


@router.post("/sessions/{session_id}/ask")
def ask_combo(req: ComboAskReq, session=Depends(require_session_owner)):
    history = get_window(str(session.id))
    result = run_multi_agent(user_id=str(session.user_id), question=req.question, chat_history=history)

    push_turn(str(session.id), "user", req.question)
    push_turn(str(session.id), "assistant", result["answer"] or "")

    return {"answer": result["answer"], "route": result["route"]}
