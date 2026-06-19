import pytest
from unittest.mock import patch, MagicMock
from app.services.rag_service import build_prompt, NO_CONTEXT_MESSAGE


# ── unit: build_prompt ────────────────────────────────────────────────────

def test_build_prompt_empty_chunks_returns_empty():
    assert build_prompt("What is X?", []) == ""


def test_build_prompt_includes_question():
    chunks = [{"text": "Revenue grew 20%", "page_number": 3}]
    prompt = build_prompt("What was revenue growth?", chunks)
    assert "What was revenue growth?" in prompt
    assert "Revenue grew 20%" in prompt


def test_build_prompt_numbers_sources_sequentially():
    chunks = [
        {"text": "First fact", "page_number": 1},
        {"text": "Second fact", "page_number": 2},
    ]
    prompt = build_prompt("question", chunks)
    assert "[Source 1]" in prompt
    assert "[Source 2]" in prompt


def test_build_prompt_includes_page_number():
    chunks = [{"text": "Some fact", "page_number": 7}]
    prompt = build_prompt("q", chunks)
    assert "(Page 7)" in prompt


def test_build_prompt_omits_page_when_none():
    chunks = [{"text": "Some fact", "page_number": None}]
    prompt = build_prompt("q", chunks)
    assert "(Page" not in prompt


def test_build_prompt_contains_system_instructions():
    chunks = [{"text": "fact", "page_number": None}]
    prompt = build_prompt("q", chunks)
    assert "NexusAI" in prompt
    assert "ONLY the context" in prompt


# ── unit: rag_service.ask (mocked) ──────────────────────────────────────────

@patch("app.services.rag_service.generate")
@patch("app.services.rag_service.qdrant_service")
@patch("app.services.rag_service.embed_query")
def test_ask_no_chunks_returns_fallback(mock_embed, mock_qdrant, mock_generate, db_session):
    mock_embed.return_value = [0.1] * 768
    mock_qdrant.search.return_value = []

    from app.services.rag_service import ask
    result = ask(db_session, user_id=1, question="anything")

    assert result["answer"] == NO_CONTEXT_MESSAGE
    assert result["sources"] == []
    mock_generate.assert_not_called()


@patch("app.services.rag_service.generate")
@patch("app.services.rag_service.qdrant_service")
@patch("app.services.rag_service.embed_query")
def test_ask_with_chunks_calls_generate(mock_embed, mock_qdrant, mock_generate, db_session):
    mock_embed.return_value = [0.1] * 768
    mock_qdrant.search.return_value = [
        {"chunk_id": 1, "document_id": 1, "chunk_index": 0, "text": "fact", "page_number": 1, "score": 0.9}
    ]
    mock_generate.return_value = "The answer is [Source 1]."

    from app.services.rag_service import ask
    result = ask(db_session, user_id=1, question="what happened?")

    assert "Source 1" in result["answer"]
    assert len(result["sources"]) == 1
    mock_generate.assert_called_once()


# ── integration: chat API ───────────────────────────────────────────────────

@pytest.fixture
def auth_header(client):
    client.post("/api/v1/auth/register", json={"email": "chat@nx.ai", "password": "Test1234!"})
    r = client.post("/api/v1/auth/login", data={"username": "chat@nx.ai", "password": "Test1234!"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_ask_empty_question_rejected(client, auth_header):
    res = client.post("/api/v1/chat/ask", json={"question": "   "}, headers=auth_header)
    assert res.status_code == 400


def test_ask_invalid_document_id_404(client, auth_header):
    res = client.post(
        "/api/v1/chat/ask",
        json={"question": "test", "document_id": 9999},
        headers=auth_header,
    )
    assert res.status_code == 404


@patch("app.api.v1.endpoints.chat.rag_service")
def test_ask_success(mock_rag, client, auth_header):
    mock_rag.ask.return_value = {"chat_id": 1, "answer": "42", "sources": []}
    res = client.post("/api/v1/chat/ask", json={"question": "what is the meaning of life?"}, headers=auth_header)
    assert res.status_code == 200
    assert res.json()["answer"] == "42"


def test_chat_history_empty(client, auth_header):
    res = client.get("/api/v1/chat/history", headers=auth_header)
    assert res.status_code == 200
    assert res.json()["total"] >= 0


def test_chat_requires_auth(client):
    res = client.post("/api/v1/chat/ask", json={"question": "test"})
    assert res.status_code == 401


def test_delete_nonexistent_chat_message_404(client, auth_header):
    res = client.delete("/api/v1/chat/history/9999", headers=auth_header)
    assert res.status_code == 404
