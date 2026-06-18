from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from backend.database import get_db
from backend.dependencies import get_current_user
from services.auth_service.models import User, Session
from services.auth_service.schemas import (
    SignupRequest, LoginRequest, RefreshRequest,
    TokenResponse, UserOut, MessageResponse
)
from services.auth_service.utils import (
    hash_pw, verify_pw,
    make_access_token, make_refresh_token,
    decode_token, refresh_token_expiry
)

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Signup ─────────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: DBSession = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=body.email, hashed_password=hash_pw(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Login ──────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: DBSession = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_pw(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    uid = str(user.id)
    access = make_access_token(uid, user.role.value)
    refresh = make_refresh_token(uid)

    # store refresh token in sessions table
    session = Session(
        user_id=user.id,
        refresh_token=refresh,
        expires_at=refresh_token_expiry()
    )
    db.add(session)
    db.commit()

    return TokenResponse(access_token=access, refresh_token=refresh)


# ── Refresh ────────────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: DBSession = Depends(get_db)):
    payload = decode_token(body.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    session = db.query(Session).filter(Session.refresh_token == body.refresh_token).first()
    if not session:
        raise HTTPException(status_code=401, detail="Session not found or already revoked")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="User not found or disabled")

    uid = str(user.id)
    new_access = make_access_token(uid, user.role.value)
    new_refresh = make_refresh_token(uid)

    # rotate: delete old session, create new one
    db.delete(session)
    new_session = Session(
        user_id=user.id,
        refresh_token=new_refresh,
        expires_at=refresh_token_expiry()
    )
    db.add(new_session)
    db.commit()

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


# ── Logout ─────────────────────────────────────────────────────────────────────

@router.post("/logout", response_model=MessageResponse)
def logout(body: RefreshRequest, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.refresh_token == body.refresh_token).first()
    if session:
        db.delete(session)
        db.commit()
    return MessageResponse(message="Logged out successfully")


# ── Me (protected) ─────────────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
