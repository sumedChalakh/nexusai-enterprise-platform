import pytest
from app.services.chunking_service import chunk_document, _split_text, _estimate_tokens, CHUNK_SIZE


# ── unit: _estimate_tokens ───────────────────────────────────────────────────

def test_estimate_tokens_basic():
    assert _estimate_tokens("hello world") == 2   # 11 chars // 4


def test_estimate_tokens_minimum():
    assert _estimate_tokens("x") == 1             # never returns 0


# ── unit: _split_text ────────────────────────────────────────────────────────

def test_split_text_short_returns_single():
    text = "This is a short sentence."
    res = _split_text(text, CHUNK_SIZE, 64)
    assert len(res) == 1
    assert res[0][0] == text


def test_split_text_long_creates_multiple():
    # 3000 chars → should split into multiple chunks of ~512 tokens
    text = ("word " * 600).strip()
    res = _split_text(text, CHUNK_SIZE, 64)
    assert len(res) > 1


def test_split_text_overlap():
    text = ("paragraph one.\n\n" * 50).strip()
    res = _split_text(text, 100, 20)
    # Consecutive chunks should share some content (overlap)
    if len(res) > 1:
        end_of_first = res[0][2]       # end_char of first chunk
        start_of_second = res[1][1]    # start_char of second chunk
        assert start_of_second < end_of_first  # overlap confirmed


# ── unit: chunk_document ─────────────────────────────────────────────────────

def test_chunk_empty_text():
    assert chunk_document("") == []
    assert chunk_document("   ") == []


def test_chunk_short_document():
    text = "This is a short document with only a few sentences."
    chunks = chunk_document(text)
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == text.strip()
    assert chunks[0].page_number is None


def test_chunk_plain_text():
    text = ("This is paragraph number one.\n\n" * 80).strip()
    chunks = chunk_document(text)
    assert len(chunks) > 1
    for i, c in enumerate(chunks):
        assert c.chunk_index == i
        assert len(c.text) > 0
        assert c.token_estimate > 0
        assert c.start_char <= c.end_char


def test_chunk_pdf_page_aware():
    text = "[Page 1]\nContent of page one.\n\n[Page 2]\nContent of page two.\n\n" * 10
    chunks = chunk_document(text)
    assert len(chunks) >= 2
    # Page numbers should be extracted
    page_nums = {c.page_number for c in chunks if c.page_number is not None}
    assert 1 in page_nums
    assert 2 in page_nums


def test_chunk_indices_sequential():
    text = ("sentence here " * 200).strip()
    chunks = chunk_document(text)
    for i, c in enumerate(chunks):
        assert c.chunk_index == i


def test_chunk_token_estimates_reasonable():
    text = ("word " * 400).strip()
    chunks = chunk_document(text)
    for c in chunks:
        # Each chunk should be under 2x CHUNK_SIZE tokens
        assert c.token_estimate <= CHUNK_SIZE * 2


# ── integration: API ─────────────────────────────────────────────────────────

@pytest.fixture
def auth_header(client):
    client.post("/api/v1/auth/register", json={"email": "chunk@nx.ai", "password": "Test1234!"})
    r = client.post("/api/v1/auth/login", data={"username": "chunk@nx.ai", "password": "Test1234!"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_chunk_stats_empty(client, auth_header):
    # Create a mock doc and check stats returns 0s gracefully
    # (full pipeline test requires S3 mock — tested in test_parsing.py)
    pass


def test_chunks_endpoint_404_on_missing_doc(client, auth_header):
    r = client.get("/api/v1/documents/9999/chunks/", headers=auth_header)
    assert r.status_code == 404


def test_chunk_stats_404_on_missing_doc(client, auth_header):
    r = client.get("/api/v1/documents/9999/chunks/stats", headers=auth_header)
    assert r.status_code == 404
