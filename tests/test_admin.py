"""admin_service + require_admin tests"""
import pytest
from fastapi import HTTPException
from types import SimpleNamespace

from app.models.user import User
from app.models.document import Document, DocStatus
from app.services import admin_service as svc
from dependencies import require_admin


def test_get_all_users_clamps_limit(db):
    for i in range(5):
        db.add(User(email=f"u{i}@x.com", hashed_password="hashed_pwd"))
    db.commit()

    out = svc.get_all_users(db, limit=999999)

    assert len(out) == 5


def test_get_platform_stats_counts_correctly(db):
    u1 = User(email="a@x.com", hashed_password="hashed_pwd")
    db.add(u1)
    db.commit()
    db.add(Document(user_id=u1.id, original_name="a.pdf", s3_key="key/a.pdf", content_type="application/pdf", status=DocStatus.ready))
    db.add(Document(user_id=u1.id, original_name="b.pdf", s3_key="key/b.pdf", content_type="application/pdf", status=DocStatus.failed))
    db.commit()

    stats = svc.get_platform_stats(db)

    assert stats["total_users"] == 1
    assert stats["total_documents"] == 2
    assert stats["documents_by_status"]["ready"] == 1
    assert stats["documents_by_status"]["failed"] == 1


def test_set_user_active_toggles_flag(db):
    u = User(email="a@x.com", hashed_password="hashed_pwd", is_active=True)
    db.add(u)
    db.commit()

    out = svc.set_user_active(db, u.id, False)

    assert out["ok"] is True
    assert out["is_active"] is False


def test_set_user_active_missing_user_returns_error(db):
    out = svc.set_user_active(db, 99999, False)
    assert out["ok"] is False


def test_require_admin_blocks_non_admin():
    fake_user = SimpleNamespace(role=SimpleNamespace(value="user"))
    with pytest.raises(HTTPException) as exc:
        require_admin(current_user=fake_user)
    assert exc.value.status_code == 403


def test_require_admin_allows_admin():
    fake_admin = SimpleNamespace(role=SimpleNamespace(value="admin"))
    assert require_admin(current_user=fake_admin) is fake_admin
