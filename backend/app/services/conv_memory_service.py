import json

from app.core.config import settings
from app.core.database import SessionLocal
from app.services.chat_history_service import format_for_llm, get_messages

try:
    import redis

    r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception:
    r = None

WINDOW = 12
TTL_SECONDS = 60 * 60 * 6


def _key(session_id: str) -> str:
    return f"conv:{session_id}"


def _redis():
    if r is None:
        raise RuntimeError("Redis client is not available")
    return r


def push_turn(session_id: str, role: str, content: str) -> None:
    client = _redis()
    key = _key(session_id)
    client.rpush(key, json.dumps({"role": role, "content": content}))
    client.ltrim(key, -WINDOW, -1)
    client.expire(key, TTL_SECONDS)


def get_window(session_id: str, db_fallback: bool = True) -> list[dict]:
    client = _redis()
    key = _key(session_id)
    raw = client.lrange(key, 0, -1)
    if raw:
        return [json.loads(x) for x in raw]

    if not db_fallback:
        return []

    db = SessionLocal()
    try:
        formatted = format_for_llm(get_messages(db, session_id, limit=WINDOW))
    finally:
        db.close()

    for m in formatted:
        client.rpush(key, json.dumps(m))
    if formatted:
        client.expire(key, TTL_SECONDS)
    return formatted


def clear_session(session_id: str) -> None:
    _redis().delete(_key(session_id))
