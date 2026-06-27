from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.services.reranker_service import search_and_rerank

router = APIRouter(prefix="/search", tags=["search"])


class RerankRequest(BaseModel):
    query: str
    fetch_n: int = 20
    top_n: int = 5


@router.post("/rerank")
def search_reranked(req: RerankRequest, user=Depends(get_current_user)):
    results = search_and_rerank(user.id, req.query, req.fetch_n, req.top_n)
    return {"query": req.query, "results": results}
