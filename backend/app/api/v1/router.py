from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    chat,
    chat_sessions,
    chunks,
    citations,
    documents,
    hybrid_search,
    reranking,
    search,
    agent,
    agent_pdf,
    agent_sql,
    agent_web,
    agent_multi,
    admin,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(chunks.router)
api_router.include_router(search.router)
api_router.include_router(hybrid_search.router)
api_router.include_router(reranking.router)
api_router.include_router(chat.router)
api_router.include_router(chat_sessions.router)
api_router.include_router(citations.router)
api_router.include_router(agent.router)
api_router.include_router(agent_pdf.router)
api_router.include_router(agent_sql.router)
api_router.include_router(agent_web.router)
api_router.include_router(agent_multi.router)
api_router.include_router(admin.router)

