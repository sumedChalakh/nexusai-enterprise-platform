"""LangGraph node + graph tests (services mocked, no real Qdrant/LLM)"""
from unittest.mock import patch

from app.services.agents.state import AgentState
from app.services.agents.nodes import retrieve_node, rerank_node, generate_node, format_history
from app.services.agents.graphs import run_rag


def _state(**over) -> AgentState:
    base: AgentState = {
        "question": "what is the refund policy",
        "user_id": "u1",
        "chat_history": [],
        "retrieved": [],
        "reranked": [],
        "answer": None,
        "sources": [],
        "error": None,
    }
    base.update(over)
    return base


@patch("app.services.agents.nodes.hybrid_search")
def test_retrieve_node_calls_hybrid_search_with_user_scope(mock_search):
    mock_search.return_value = [{"text": "refunds within 30 days", "doc_id": "d1", "chunk_id": "c1"}]

    out = retrieve_node(_state())

    mock_search.assert_called_once_with(user_id="u1", query="what is the refund policy", top_n=20)
    assert out["retrieved"] == mock_search.return_value


@patch("app.services.agents.nodes.rerank")
def test_rerank_node_passes_retrieved_chunks_through_reranker(mock_rerank):
    chunks = [{"text": "a"}, {"text": "b"}]
    mock_rerank.return_value = [{"text": "b", "rerank_score": 0.9}]

    out = rerank_node(_state(retrieved=chunks))

    mock_rerank.assert_called_once_with("what is the refund policy", chunks, top_n=6)
    assert out["reranked"] == mock_rerank.return_value


def test_generate_node_short_circuits_on_no_reranked_chunks():
    out = generate_node(_state(reranked=[]))
    assert out["answer"] == "No relevant documents found for this question."
    assert out["sources"] == []


@patch("app.services.agents.nodes.gemini_generate")
def test_generate_node_builds_context_and_extracts_sources(mock_gen):
    mock_gen.return_value = "Refunds are allowed within 30 days [1]."
    reranked = [{"doc_id": "d1", "chunk_id": "c1", "text": "Refund window is 30 days."}]

    out = generate_node(_state(reranked=reranked))

    assert out["answer"] == "Refunds are allowed within 30 days [1]."
    assert out["sources"][0]["doc_id"] == "d1"


def test_format_history_handles_empty_list():
    assert format_history([]) == "(no prior turns)"


def test_format_history_joins_turns():
    h = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    assert format_history(h) == "user: hi\nassistant: hello"


@patch("app.services.agents.nodes.gemini_generate")
@patch("app.services.agents.nodes.rerank")
@patch("app.services.agents.nodes.hybrid_search")
def test_full_graph_runs_all_three_nodes_in_order(mock_search, mock_rerank, mock_gen):
    mock_search.return_value = [{"text": "raw chunk", "doc_id": "d1", "chunk_id": "c1"}]
    mock_rerank.return_value = [{"text": "raw chunk", "doc_id": "d1", "chunk_id": "c1"}]
    mock_gen.return_value = "Here's the answer [1]."

    result = run_rag(user_id="u1", question="anything", chat_history=[])

    mock_search.assert_called_once()
    mock_rerank.assert_called_once()
    mock_gen.assert_called_once()
    assert result["answer"] == "Here's the answer [1]."
    assert result["sources"][0]["doc_id"] == "d1"


@patch("app.services.agents.nodes.hybrid_search")
def test_full_graph_handles_no_results_without_calling_rerank_or_generate(mock_search):
    mock_search.return_value = []

    with patch("app.services.agents.nodes.rerank") as mock_rerank, patch("app.services.agents.nodes.gemini_generate") as mock_gen:
        mock_rerank.return_value = []
        result = run_rag(user_id="u1", question="anything", chat_history=[])

    assert result["answer"] == "No relevant documents found for this question."
    mock_gen.assert_not_called()
