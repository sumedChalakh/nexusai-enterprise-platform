from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth import require_admin
from app.services import admin_service as svc

router = APIRouter(prefix="/admin", tags=["admin"])


class SetActiveReq(BaseModel):
    is_active: bool


@router.get("/users")
def list_users(limit: int = 50, offset: int = 0, _admin=Depends(require_admin), db: Session = Depends(get_db)):
    return svc.get_all_users(db, limit, offset)


@router.get("/stats")
def stats(_admin=Depends(require_admin), db: Session = Depends(get_db)):
    return svc.get_platform_stats(db)


@router.post("/users/{user_id}/active")
def set_active(user_id: str, req: SetActiveReq, _admin=Depends(require_admin), db: Session = Depends(get_db)):
    return svc.set_user_active(db, user_id, req.is_active)
