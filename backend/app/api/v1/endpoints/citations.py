from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.services.citation_service import answer_with_citations

router = APIRouter(prefix="/ask", tags=["ask"])


class CitedAskRequest(BaseModel):
    question: str


@router.post("/cited")
def ask_cited(req: CitedAskRequest, user=Depends(get_current_user)):
    return answer_with_citations(user.id, req.question)
