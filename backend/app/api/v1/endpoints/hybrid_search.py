from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.services.hybrid_search_service import hybrid_search

router = APIRouter(prefix="/search", tags=["search"])


class HybridSearchRequest(BaseModel):
    query: str
    top_n: int = 8


@router.post("/hybrid")
def search_hybrid(req: HybridSearchRequest, user=Depends(get_current_user)):
    results = hybrid_search(user_id=user.id, query=req.query, top_n=req.top_n)
    return {"query": req.query, "results": results}
