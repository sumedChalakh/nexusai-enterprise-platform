from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.services.agents.web_agent import run_web_agent

router = APIRouter(prefix="/agent/web", tags=["agent"])


class WebAskReq(BaseModel):
    question: str


@router.post("/ask")
def ask_web(req: WebAskReq, user=Depends(get_current_user)):
    return run_web_agent(req.question)
