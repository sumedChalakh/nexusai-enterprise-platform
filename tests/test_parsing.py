import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from app.services.parser_service import parse_txt, parse_csv, parse_document


# ── unit tests: parser_service ───────────────────────────────────────────────

def test_parse_txt_utf8():
    content = b"Hello NexusAI\nLine two"
    result = parse_txt(content)
    assert "Hello NexusAI" in result
    assert "Line two" in result


def test_parse_txt_latin1():
    content = "Café résumé".encode("latin-1")
    result = parse_txt(content)
    assert len(result) > 0


def test_parse_csv():
    content = b"name,score\nAlice,95\nBob,87"
    result = parse_csv(content)
    assert "Alice" in result
    assert "95" in result
    assert "|" in result


def test_parse_unsupported_type():
    with pytest.raises(ValueError, match="No parser"):
        parse_document(b"data", "application/octet-stream")


@patch("app.services.parser_service.fitz")
def test_parse_pdf_mock(mock_fitz):
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "Invoice total: $1,200"
    mock_doc.__iter__ = lambda s: iter([mock_page])
    mock_doc.__len__ = lambda s: 1
    mock_fitz.open.return_value = mock_doc
    from app.services.parser_service import parse_pdf
    result = parse_pdf(b"%PDF-fake")
    assert "Invoice" in result


# ── integration tests: API ───────────────────────────────────────────────────

@pytest.fixture
def auth_header(client):
    client.post("/api/v1/auth/register", json={"email": "p4@nx.ai", "password": "Test1234!"})
    r = client.post("/api/v1/auth/login", data={"username": "p4@nx.ai", "password": "Test1234!"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@patch("app.services.s3_service.s3")
@patch("app.services.processing_service._get_s3_content")
def test_upload_triggers_parse(mock_s3_content, mock_s3, client, auth_header):
    mock_s3.put_object.return_value = {}
    mock_s3_content.return_value = b"plain text content here"

    f = BytesIO(b"plain text content here")
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("note.txt", f, "text/plain")},
        headers=auth_header,
    )
    assert res.status_code == 201
    assert res.json()["status"] in ("uploaded", "processing", "ready")


@patch("app.services.s3_service.s3")
@patch("app.services.processing_service._get_s3_content")
def test_get_text_when_ready(mock_s3_content, mock_s3, client, auth_header):
    mock_s3.put_object.return_value = {}
    mock_s3_content.return_value = b"sample document text"

    f = BytesIO(b"sample document text")
    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("doc.txt", f, "text/plain")},
        headers=auth_header,
    )
    doc_id = upload.json()["id"]

    # Force ready status in DB for test
    import time; time.sleep(0.5)
    status = client.get(f"/api/v1/documents/{doc_id}/status", headers=auth_header)
    assert status.status_code == 200
    assert status.json()["doc_id"] == doc_id


@patch("app.services.s3_service.s3")
@patch("app.services.processing_service._get_s3_content")
def test_reparse_endpoint(mock_s3_content, mock_s3, client, auth_header):
    mock_s3.put_object.return_value = {}
    mock_s3_content.return_value = b"re-parse me"

    f = BytesIO(b"re-parse me")
    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("retry.txt", f, "text/plain")},
        headers=auth_header,
    )
    doc_id = upload.json()["id"]

    res = client.post(f"/api/v1/documents/{doc_id}/reparse", headers=auth_header)
    assert res.status_code == 200
    assert res.json()["doc_id"] == doc_id


def test_list_with_status_filter(client, auth_header):
    res = client.get("/api/v1/documents/?status_filter=ready", headers=auth_header)
    assert res.status_code == 200
    assert "documents" in res.json()
