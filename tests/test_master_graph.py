"""master graph tests: verify each route actually reaches the right node and nothing else runs."""
from unittest.mock import patch

from app.services.agents.graphs import run_master


@patch("app.services.agents.nodes.gemini_generate")
@patch("app.services.agents.nodes.rerank")
@patch("app.services.agents.nodes.hybrid_search")
@patch("app.services.agents.router_agent.gemini_generate")
def test_rag_route_runs_retrieve_rerank_generate(mock_route_llm, mock_search, mock_rerank, mock_gen):
    mock_route_llm.return_value = "rag"
    mock_search.return_value = [{"text": "x", "doc_id": "d1", "chunk_id": "c1"}]
    mock_rerank.return_value = mock_search.return_value
    mock_gen.return_value = "answer [1]"

    result = run_master(user_id="u1", question="general question")

    assert result["route"] == "rag"
    mock_search.assert_called_once()
    assert result["answer"] == "answer [1]"


@patch("app.services.agents.nodes.gemini_generate")
@patch("app.services.agents.nodes.rerank")
@patch("app.services.agents.nodes.pdf_scoped_search")
@patch("app.services.agents.router_agent.gemini_generate")
def test_pdf_route_runs_pdf_retrieve_rerank_generate(mock_route_llm, mock_pdf_search, mock_rerank, mock_gen):
    mock_route_llm.return_value = "pdf"
    mock_pdf_search.return_value = [{"text": "x", "doc_id": "d1", "chunk_id": "c1", "page": 1}]
    mock_rerank.return_value = mock_pdf_search.return_value
    mock_gen.return_value = "pdf answer [1]"

    result = run_master(user_id="u1", question="summarize", doc_id="d1")

    assert result["route"] == "pdf"
    mock_pdf_search.assert_called_once()
    assert result["answer"] == "pdf answer [1]"


@patch("app.services.agents.graphs.run_sql_agent")
@patch("app.services.agents.router_agent.gemini_generate")
def test_sql_route_skips_retrieval_and_rerank_entirely(mock_route_llm, mock_sql):
    mock_route_llm.return_value = "sql"
    mock_sql.return_value = {"answer": "you have 3 documents", "sources": []}

    with patch("app.services.agents.nodes.hybrid_search") as mock_search:
        result = run_master(user_id="u1", question="how many docs do I have")
        mock_search.assert_not_called()

    assert result["route"] == "sql"
    assert result["answer"] == "you have 3 documents"


@patch("app.services.agents.graphs.run_web_agent")
@patch("app.services.agents.router_agent.gemini_generate")
def test_web_route_skips_retrieval_and_rerank_entirely(mock_route_llm, mock_web):
    mock_route_llm.return_value = "web"
    mock_web.return_value = {"answer": "it's sunny today", "sources": [{"marker": 1, "url": "https://x.com"}]}

    with patch("app.services.agents.nodes.hybrid_search") as mock_search:
        result = run_master(user_id="u1", question="what's the weather")
        mock_search.assert_not_called()

    assert result["route"] == "web"
    assert result["sources"][0]["url"] == "https://x.com"
