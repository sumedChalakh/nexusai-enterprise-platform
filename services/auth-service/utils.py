from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status

from backend.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = 15
REFRESH_EXPIRE_DAYS = 7


# ── Password ───────────────────────────────────────────────────────────────────

def hash_pw(plain: str) -> str:
    return pwd_ctx.hash(plain)


def verify_pw(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


# ── JWT ────────────────────────────────────────────────────────────────────────

def make_access_token(user_id: str, role: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MIN)
    payload = {"sub": user_id, "role": role, "type": "access", "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def make_refresh_token(user_id: str) -> str:
    exp = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    payload = {"sub": user_id, "type": "refresh", "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def refresh_token_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
