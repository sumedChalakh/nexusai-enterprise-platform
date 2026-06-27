from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import Session, User
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserOut,
)
from app.services.auth_service import (
    decode_token,
    hash_pw,
    make_access_token,
    make_refresh_token,
    refresh_token_expiry,
    verify_pw,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _create_user(body: SignupRequest, db: DBSession) -> User:
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=body.email, hashed_password=hash_pw(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: SignupRequest, db: DBSession = Depends(get_db)):
    return _create_user(body, db)


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: DBSession = Depends(get_db)):
    return _create_user(body, db)


def _issue_tokens(user: User, db: DBSession) -> TokenResponse:
    access = make_access_token(str(user.id), user.role.value)
    refresh = make_refresh_token(str(user.id))
    session = Session(
        user_id=user.id,
        refresh_token=refresh,
        expires_at=refresh_token_expiry(),
    )
    db.add(session)
    db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: DBSession = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
        email = payload.get("email")
        password = payload.get("password")
    else:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    user = db.query(User).filter(User.email == email).first()
    if not user or not password or not verify_pw(str(password), user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    return _issue_tokens(user, db)

@router.post("/login/json", response_model=TokenResponse)
def login_json(body: LoginRequest, db: DBSession = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_pw(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    return _issue_tokens(user, db)


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

    db.delete(session)
    db.commit()
    return _issue_tokens(user, db)


@router.post("/logout", response_model=MessageResponse)
def logout(body: RefreshRequest, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.refresh_token == body.refresh_token).first()
    if session:
        db.delete(session)
        db.commit()
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
