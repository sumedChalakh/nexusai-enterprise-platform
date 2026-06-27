from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.db import get_db
from app.services.agents.sql_agent import run_sql_agent

router = APIRouter(prefix="/agent/sql", tags=["agent"])


class SqlAskReq(BaseModel):
    question: str


@router.post("/ask")
def ask_sql(req: SqlAskReq, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return run_sql_agent(db, user.id, req.question)
