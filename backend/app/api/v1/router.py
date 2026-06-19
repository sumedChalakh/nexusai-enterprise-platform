from fastapi import APIRouter
from app.api.v1.endpoints import auth, documents, chunks, search, chat

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(chunks.router)
api_router.include_router(search.router)
api_router.include_router(chat.router)
