import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from io import BytesIO


@pytest.fixture
def auth_header(client, db):
    # register + login helper
    client.post("/api/v1/auth/register", json={"email": "test@nx.ai", "password": "Test1234!"})
    res = client.post("/api/v1/auth/login", data={"username": "test@nx.ai", "password": "Test1234!"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@patch("app.services.s3_service.s3")
def test_upload_pdf(mock_s3, client, auth_header):
    mock_s3.put_object.return_value = {}
    f = BytesIO(b"%PDF-1.4 test content")
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", f, "application/pdf")},
        headers=auth_header,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["original_name"] == "test.pdf"
    assert data["status"] == "uploaded"


@patch("app.services.s3_service.s3")
def test_upload_invalid_type(mock_s3, client, auth_header):
    f = BytesIO(b"fake exe content")
    res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("malware.exe", f, "application/octet-stream")},
        headers=auth_header,
    )
    assert res.status_code == 400
    assert "Unsupported" in res.json()["detail"]


@patch("app.services.s3_service.s3")
def test_list_documents(mock_s3, client, auth_header):
    mock_s3.put_object.return_value = {}
    f = BytesIO(b"%PDF test")
    client.post(
        "/api/v1/documents/upload",
        files={"file": ("a.pdf", f, "application/pdf")},
        headers=auth_header,
    )
    res = client.get("/api/v1/documents/", headers=auth_header)
    assert res.status_code == 200
    assert res.json()["total"] >= 1


@patch("app.services.s3_service.s3")
def test_delete_document(mock_s3, client, auth_header):
    mock_s3.put_object.return_value = {}
    mock_s3.delete_object.return_value = {}
    f = BytesIO(b"%PDF test")
    upload = client.post(
        "/api/v1/documents/upload",
        files={"file": ("del.pdf", f, "application/pdf")},
        headers=auth_header,
    )
    doc_id = upload.json()["id"]
    res = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_header)
    assert res.status_code == 200
    assert res.json()["deleted_id"] == doc_id


def test_list_unauthorized(client):
    res = client.get("/api/v1/documents/")
    assert res.status_code == 401
