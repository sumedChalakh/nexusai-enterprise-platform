"""Legacy Day 8-14 database import compatibility."""
from app.core.database import Base, SessionLocal, engine, get_db

__all__ = ["Base", "SessionLocal", "engine", "get_db"]
