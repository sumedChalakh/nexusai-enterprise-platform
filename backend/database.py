from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from sqlalchemy.pool import StaticPool
from config import settings

engine_kwargs = {
    "pool_pre_ping": True,
}
if not settings.db_url.startswith("sqlite"):
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
else:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(
    settings.db_url,
    **engine_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# dependency — yields a DB session per request, closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


