from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.database import engine, Base
from services.auth_service.router import router as auth_router

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("NexusAI starting — creating tables if not exist...")
    Base.metadata.create_all(bind=engine)   # dev only; production uses Alembic
    log.info("Startup complete.")
    yield
    log.info("NexusAI shutting down.")


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Enterprise Knowledge Platform API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(auth_router)


@app.get("/")
def root():
    return {"message": f"{settings.app_name} API", "version": "0.2.0"}


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}
