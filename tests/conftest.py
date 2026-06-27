import os
# Force in-memory SQLite and local URLs for tests
os.environ["DB_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["QDRANT_HOST"] = "localhost"

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# SQLite support for Postgres ARRAY type
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import ARRAY

@compiles(ARRAY, "sqlite")
def compile_array_sqlite(element, compiler, **kw):
    return "TEXT"

original_bind_processor = ARRAY.bind_processor
original_result_processor = ARRAY.result_processor

def patched_bind_processor(self, dialect):
    if dialect.name == "sqlite":
        def process(value):
            if value is None:
                return None
            import json
            if isinstance(value, (list, tuple)):
                return json.dumps(value)
            return value
        return process
    return original_bind_processor(self, dialect)

def patched_result_processor(self, dialect, coltype):
    if dialect.name == "sqlite":
        def process(value):
            if value is None:
                return []
            import json
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except Exception:
                    return []
            return value
        return process
    return original_result_processor(self, dialect, coltype)

ARRAY.bind_processor = patched_bind_processor
ARRAY.result_processor = patched_result_processor

# Import all models to register them on Base and prevent mapper config errors during test collection
from app.models.user import User, Session
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.chat_session import ChatSession, ChatSessionMessage
from app.models.chat_message import ChatMessage

from database import Base, get_db
from main import app

@pytest.fixture(name="db")
def db_fixture():
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(name="db_session")
def db_session_fixture(db):
    return db

@pytest.fixture(name="client")
def client_fixture(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
