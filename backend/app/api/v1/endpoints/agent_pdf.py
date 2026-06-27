from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.user_isolation_service import require_session_owner
from app.services.conv_memory_service import get_window, push_turn
from app.services.agents import run_pdf_agent

router = APIRouter(prefix="/agent/pdf", tags=["agent"])


class PdfAskReq(BaseModel):
    doc_id: str
    question: str


@router.post("/sessions/{session_id}/ask")
def ask_pdf(req: PdfAskReq, session=Depends(require_session_owner)):
    history = get_window(str(session.id))
    result = run_pdf_agent(user_id=str(session.user_id), doc_id=req.doc_id, question=req.question, chat_history=history)

    push_turn(str(session.id), "user", req.question)
    push_turn(str(session.id), "assistant", result["answer"] or "")

    return {"answer": result["answer"], "sources": result["sources"], "error": result.get("error")}
