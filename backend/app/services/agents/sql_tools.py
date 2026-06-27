from sqlalchemy import select, func

from app.models.document import Document, DocStatus

VALID_STATUSES = {s.value for s in DocStatus}


def get_val(s) -> str:
    return s.value if hasattr(s, "value") else str(s)


def count_documents(db, user_id: str, **_) -> dict:
    n = db.execute(
        select(func.count()).select_from(Document).where(Document.user_id == user_id)
    ).scalar_one()
    return {"text": f"You have {n} document(s) uploaded.", "rows": [{"count": n}]}


def list_documents(db, user_id: str, status: str | None = None, limit: int = 10, **_) -> dict:
    limit = max(1, min(int(limit), 50))  # clamp

    q = select(Document).where(Document.user_id == user_id)
    if status:
        if status not in VALID_STATUSES:
            return {"text": f"'{status}' isn't a valid status. Valid: {sorted(VALID_STATUSES)}", "rows": []}
        q = q.where(Document.status == status)

    q = q.order_by(Document.created_at.desc()).limit(limit)
    rows = db.execute(q).scalars().all()

    if not rows:
        return {"text": "No matching documents found.", "rows": []}

    lines = [f"- {d.original_name} ({get_val(d.status)})" for d in rows]
    return {
        "text": "Here are your documents:\n" + "\n".join(lines),
        "rows": [{"filename": d.original_name, "status": get_val(d.status)} for d in rows],
    }


def document_stats(db, user_id: str, **_) -> dict:
    rows = db.execute(
        select(Document.status, func.count()).where(Document.user_id == user_id).group_by(Document.status)
    ).all()

    if not rows:
        return {"text": "No documents uploaded yet.", "rows": []}

    lines = [f"- {get_val(status)}: {count}" for status, count in rows]
    return {"text": "Document status breakdown:\n" + "\n".join(lines), "rows": [{"status": get_val(s), "count": c} for s, c in rows]}


TOOLS = {
    "count_documents": count_documents,
    "list_documents": list_documents,
    "document_stats": document_stats,
}
