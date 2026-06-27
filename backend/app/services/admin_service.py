from sqlalchemy import select, func

from app.models.user import User
from app.models.document import Document


def get_val(s) -> str:
    return s.value if hasattr(s, "value") else str(s)


def get_all_users(db, limit: int = 50, offset: int = 0) -> list[dict]:
    limit = max(1, min(int(limit), 200))  # clamp
    rows = db.execute(select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)).scalars().all()
    return [{"id": str(u.id), "email": u.email, "is_active": u.is_active, "created_at": u.created_at} for u in rows]


def get_platform_stats(db) -> dict:
    total_users = db.execute(select(func.count()).select_from(User)).scalar_one()
    total_docs = db.execute(select(func.count()).select_from(Document)).scalar_one()

    by_status = db.execute(select(Document.status, func.count()).group_by(Document.status)).all()

    return {
        "total_users": total_users,
        "total_documents": total_docs,
        "documents_by_status": {get_val(status): count for status, count in by_status},
    }


def set_user_active(db, user_id, active: bool) -> dict:
    user = db.get(User, user_id)
    if user is None:
        return {"ok": False, "error": "user not found"}

    user.is_active = active
    db.commit()
    return {"ok": True, "user_id": str(user.id), "is_active": user.is_active}
