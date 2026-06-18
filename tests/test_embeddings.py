import pytest
from unittest.mock import patch, MagicMock
from app.services.embedding_service import embed_texts, embed_query, EMBED_DIM, BATCH_SIZE


# ── unit: embedding_service ──────────────────────────────────────────────────

@patch("app.services.embedding_service._get_client")
def test_embed_texts_empty(mock_client):
    assert embed_texts([]) == []
    mock_client.assert_not_called()


@patch("app.services.embedding_service._get_client")
def test_embed_texts_single_batch(mock_client):
    mock_genai = MagicMock()
    mock_genai.embed_content.return_value = {"embedding": [[0.1] * EMBED_DIM, [0.2] * EMBED_DIM]}
    mock_client.return_value = mock_genai

    result = embed_texts(["hello", "world"])
    assert len(result) == 2
    assert len(result[0]) == EMBED_DIM
    mock_genai.embed_content.assert_called_once()


@patch("app.services.embedding_service._get_client")
def test_embed_texts_multiple_batches(mock_client):
    mock_genai = MagicMock()
    # Simulate BATCH_SIZE-sized responses
    mock_genai.embed_content.return_value = {"embedding": [[0.1] * EMBED_DIM] * BATCH_SIZE}
    mock_client.return_value = mock_genai

    texts = ["chunk"] * (BATCH_SIZE + 50)  # forces 2 batches
    result = embed_texts(texts)
    assert mock_genai.embed_content.call_count == 2
    assert len(result) == BATCH_SIZE * 2  # mocked response size per call


@patch("app.services.embedding_service._get_client")
@patch("app.services.embedding_service.time.sleep")  # skip real backoff delay
def test_embed_texts_retries_on_failure(mock_sleep, mock_client):
    mock_genai = MagicMock()
    mock_genai.embed_content.side_effect = [
        Exception("transient error"),
        {"embedding": [[0.1] * EMBED_DIM]},
    ]
    mock_client.return_value = mock_genai

    result = embed_texts(["one text"])
    assert len(result) == 1
    assert mock_genai.embed_content.call_count == 2


@patch("app.services.embedding_service._get_client")
@patch("app.services.embedding_service.time.sleep")
def test_embed_texts_raises_after_max_retries(mock_sleep, mock_client):
    mock_genai = MagicMock()
    mock_genai.embed_content.side_effect = Exception("permanent error")
    mock_client.return_value = mock_genai

    with pytest.raises(RuntimeError, match="Embedding failed"):
        embed_texts(["fails forever"])


@patch("app.services.embedding_service._get_client")
def test_embed_query_uses_retrieval_query_type(mock_client):
    mock_genai = MagicMock()
    mock_genai.embed_content.return_value = {"embedding": [0.5] * EMBED_DIM}
    mock_client.return_value = mock_genai

    vec = embed_query("what is the revenue?")
    assert len(vec) == EMBED_DIM
    _, kwargs = mock_genai.embed_content.call_args
    assert kwargs["task_type"] == "RETRIEVAL_QUERY"


# ── integration: search API ──────────────────────────────────────────────────

@pytest.fixture
def auth_header(client):
    client.post("/api/v1/auth/register", json={"email": "search@nx.ai", "password": "Test1234!"})
    r = client.post("/api/v1/auth/login", data={"username": "search@nx.ai", "password": "Test1234!"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@patch("app.api.v1.endpoints.search.qdrant_service")
@patch("app.api.v1.endpoints.search.embed_query")
def test_search_endpoint_success(mock_embed, mock_qdrant, client, auth_header):
    mock_embed.return_value = [0.1] * 768
    mock_qdrant.search.return_value = [
        {"chunk_id": 1, "document_id": 1, "chunk_index": 0, "text": "revenue grew 20%", "page_number": 2, "score": 0.91}
    ]

    res = client.post("/api/v1/search/", json={"query": "revenue growth"}, headers=auth_header)
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 1
    assert data["results"][0]["score"] == 0.91


@patch("app.api.v1.endpoints.search.embed_query")
def test_search_endpoint_embedding_failure(mock_embed, client, auth_header):
    mock_embed.side_effect = Exception("API down")
    res = client.post("/api/v1/search/", json={"query": "test"}, headers=auth_header)
    assert res.status_code == 502


def test_search_with_invalid_document_id(client, auth_header):
    res = client.post("/api/v1/search/", json={"query": "test", "document_id": 9999}, headers=auth_header)
    assert res.status_code == 404


def test_embedding_status_404(client, auth_header):
    res = client.get("/api/v1/search/documents/9999/embedding-status", headers=auth_header)
    assert res.status_code == 404


def test_search_requires_auth(client):
    res = client.post("/api/v1/search/", json={"query": "test"})
    assert res.status_code == 401
