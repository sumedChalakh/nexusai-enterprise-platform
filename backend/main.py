# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.logging import setup_logging
setup_logging()  # Configure JSON structured logging

from config import settings
from database import engine, Base
from app.api.v1.router import api_router
from app.services.metrics import setup_metrics

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

setup_metrics(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": f"{settings.app_name} API", "version": "0.2.0"}


@app.get("/health")
@app.get("/api/v1/health")
def health():
    from sqlalchemy import text
    from database import SessionLocal
    from app.core.qdrant import get_qdrant_client

    checks = {"db": "ok", "qdrant": "ok"}
    
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        checks["db"] = f"error: {e}"

    try:
        get_qdrant_client().get_collections()
    except Exception as e:
        checks["qdrant"] = f"error: {e}"

    healthy = all(v == "ok" for v in checks.values())
    return {"status": "ok" if healthy else "degraded", "checks": checks}

