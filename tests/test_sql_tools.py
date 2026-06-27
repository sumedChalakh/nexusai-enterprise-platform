"""sql_tools tests against real sqlite (no mocking the DB layer)"""
from app.models.document import Document, DocStatus
from app.services.agents.sql_tools import count_documents, list_documents, document_stats


def _mk_doc(db, user_id, filename, status):
    # Map parsed string to ready enum
    if status == "parsed":
        status_enum = DocStatus.ready
    elif status == "failed":
        status_enum = DocStatus.failed
    elif status == "uploaded":
        status_enum = DocStatus.uploaded
    else:
        status_enum = DocStatus(status)

    d = Document(
        user_id=user_id,
        original_name=filename,
        s3_key=f"keys/{user_id}/{filename}",
        content_type="application/pdf",
        status=status_enum
    )
    db.add(d)
    db.commit()
    return d


def test_count_documents_scoped_to_user(db):
    u1, u2 = 1, 2
    _mk_doc(db, u1, "a.pdf", "parsed")
    _mk_doc(db, u1, "b.pdf", "uploaded")
    _mk_doc(db, u2, "c.pdf", "parsed")  # different user, must not be counted

    out = count_documents(db, u1)

    assert out["rows"][0]["count"] == 2
    assert "2 document" in out["text"]


def test_list_documents_filters_by_valid_status(db):
    u1 = 1
    _mk_doc(db, u1, "a.pdf", "parsed")
    _mk_doc(db, u1, "b.pdf", "failed")

    # The filter matches the active schema status, which is 'ready' (parsed maps to ready)
    out = list_documents(db, u1, status="ready")

    assert len(out["rows"]) == 1
    assert out["rows"][0]["filename"] == "a.pdf"


def test_list_documents_rejects_invalid_status_without_querying():
    out = list_documents(db=None, user_id=1, status="dropped_table_please")
    assert out["rows"] == []
    assert "valid status" in out["text"]


def test_list_documents_clamps_limit(db):
    u1 = 1
    for i in range(5):
        _mk_doc(db, u1, f"doc{i}.pdf", "uploaded")

    out = list_documents(db, u1, limit=999999)  # try to ask for way more than allowed

    assert len(out["rows"]) <= 50  # clamp enforced even though only 5 exist here


def test_document_stats_groups_by_status(db):
    u1 = 1
    _mk_doc(db, u1, "a.pdf", "parsed")
    _mk_doc(db, u1, "b.pdf", "parsed")
    _mk_doc(db, u1, "c.pdf", "failed")

    out = document_stats(db, u1)

    by_status = {r["status"]: r["count"] for r in out["rows"]}
    assert by_status["ready"] == 2
    assert by_status["failed"] == 1
