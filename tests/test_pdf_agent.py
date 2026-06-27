"""PDF agent tests"""
from unittest.mock import patch

from app.services.agents.nodes import pdf_retrieve_node
from app.services.agents.graphs import run_pdf_agent


def test_pdf_retrieve_node_requires_doc_id():
    out = pdf_retrieve_node({"user_id": "u1", "question": "q", "doc_id": None})
    assert out["retrieved"] == []
    assert "doc_id" in out["error"]


@patch("app.services.agents.nodes.pdf_scoped_search")
def test_pdf_retrieve_node_scopes_to_doc(mock_search):
    mock_search.return_value = [{"text": "chunk", "doc_id": "d1", "chunk_id": "c1", "page": 3}]

    out = pdf_retrieve_node({"user_id": "u1", "question": "summarize section 3", "doc_id": "d1"})

    mock_search.assert_called_once_with(user_id="u1", doc_id="d1", query="summarize section 3")
    assert out["retrieved"][0]["page"] == 3


@patch("app.services.agents.nodes.pdf_scoped_search")
def test_pdf_retrieve_node_no_match_sets_error(mock_search):
    mock_search.return_value = []
    out = pdf_retrieve_node({"user_id": "u1", "question": "q", "doc_id": "d1"})
    assert out["retrieved"] == []
    assert "d1" in out["error"]


@patch("app.services.agents.nodes.gemini_generate")
@patch("app.services.agents.nodes.rerank")
@patch("app.services.agents.nodes.pdf_scoped_search")
def test_run_pdf_agent_full_graph(mock_search, mock_rerank, mock_gen):
    mock_search.return_value = [{"text": "refunds in 30 days", "doc_id": "d1", "chunk_id": "c1", "page": 2}]
    mock_rerank.return_value = mock_search.return_value
    mock_gen.return_value = "Refunds within 30 days [1]."

    result = run_pdf_agent(user_id="u1", doc_id="d1", question="refund window?")

    assert result["answer"] == "Refunds within 30 days [1]."
    assert result["sources"][0]["doc_id"] == "d1"
    assert result["error"] is None
