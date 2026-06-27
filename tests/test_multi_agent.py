"""multi-agent tests: branch logic, synthesis, and real parallel fan-out"""
from unittest.mock import patch

from app.services.agents.multi_agent import classify_combo, docs_branch_node, web_branch_node, synthesize_node
from app.services.agents.graphs import pick_branches, run_multi_agent


@patch("app.services.agents.multi_agent.gemini_generate")
def test_classify_combo_valid_response(mock_llm):
    mock_llm.return_value = "both"
    assert classify_combo("does my contract match the law") == "both"


@patch("app.services.agents.multi_agent.gemini_generate")
def test_classify_combo_falls_back_to_docs_on_garbage(mock_llm):
    mock_llm.return_value = "uh, not sure"
    assert classify_combo("anything") == "docs"


def test_pick_branches_both_returns_both_node_names():
    assert sorted(pick_branches({"route": "both"})) == ["docs_branch", "web_branch"]


def test_pick_branches_web_only():
    assert pick_branches({"route": "web"}) == ["web_branch"]


def test_pick_branches_defaults_to_docs():
    assert pick_branches({"route": "docs"}) == ["docs_branch"]


@patch("app.services.agents.multi_agent.rerank_node")
@patch("app.services.agents.multi_agent.retrieve_node")
def test_docs_branch_node_appends_one_candidate(mock_retrieve, mock_rerank):
    mock_retrieve.return_value = {"retrieved": [{"text": "x", "doc_id": "d1", "chunk_id": "c1"}]}
    mock_rerank.return_value = {"reranked": [{"text": "x", "doc_id": "d1", "chunk_id": "c1"}]}

    out = docs_branch_node({"question": "q", "user_id": "u1"})

    assert len(out["answer_candidates"]) == 1
    assert out["answer_candidates"][0]["source"] == "docs"


@patch("app.services.agents.multi_agent.rerank_node")
@patch("app.services.agents.multi_agent.retrieve_node")
def test_docs_branch_node_handles_no_results(mock_retrieve, mock_rerank):
    mock_retrieve.return_value = {"retrieved": []}
    mock_rerank.return_value = {"reranked": []}

    out = docs_branch_node({"question": "q", "user_id": "u1"})

    assert "nothing relevant" in out["answer_candidates"][0]["text"]


@patch("app.services.agents.multi_agent.run_web_agent")
def test_web_branch_node_appends_one_candidate(mock_web):
    mock_web.return_value = {"answer": "from the web", "sources": []}
    out = web_branch_node({"question": "q"})
    assert out["answer_candidates"] == [{"source": "web", "text": "from the web"}]


def test_synthesize_node_skips_llm_call_for_single_candidate():
    with patch("app.services.agents.multi_agent.gemini_generate") as mock_gen:
        out = synthesize_node({"answer_candidates": [{"source": "docs", "text": "the only answer"}]})
        mock_gen.assert_not_called()
    assert out["answer"] == "the only answer"


@patch("app.services.agents.multi_agent.gemini_generate")
def test_synthesize_node_merges_two_candidates(mock_gen):
    mock_gen.return_value = "merged final answer"
    out = synthesize_node({"answer_candidates": [
        {"source": "docs", "text": "doc says X"},
        {"source": "web", "text": "web says Y"},
    ]})
    assert out["answer"] == "merged final answer"
    mock_gen.assert_called_once()


@patch("app.services.agents.multi_agent.gemini_generate")
@patch("app.services.agents.multi_agent.run_web_agent")
@patch("app.services.agents.multi_agent.rerank_node")
@patch("app.services.agents.multi_agent.retrieve_node")
def test_full_graph_both_route_runs_parallel_branches_and_synthesizes(
    mock_retrieve, mock_rerank, mock_web, mock_gen
):
    mock_gen.side_effect = ["both", "merged answer combining both"]
    mock_retrieve.return_value = {"retrieved": [{"text": "doc chunk", "doc_id": "d1", "chunk_id": "c1"}]}
    mock_rerank.return_value = {"reranked": [{"text": "doc chunk", "doc_id": "d1", "chunk_id": "c1"}]}
    mock_web.return_value = {"answer": "web answer", "sources": []}

    result = run_multi_agent(user_id="u1", question="does my contract match the law")

    assert result["route"] == "both"
    assert len(result["answer_candidates"]) == 2
    assert result["answer"] == "merged answer combining both"


@patch("app.services.agents.multi_agent.gemini_generate")
@patch("app.services.agents.multi_agent.rerank_node")
@patch("app.services.agents.multi_agent.retrieve_node")
def test_full_graph_docs_only_route_skips_web_branch(mock_retrieve, mock_rerank, mock_gen):
    mock_gen.return_value = "docs"
    mock_retrieve.return_value = {"retrieved": [{"text": "doc chunk", "doc_id": "d1", "chunk_id": "c1"}]}
    mock_rerank.return_value = {"reranked": [{"text": "doc chunk", "doc_id": "d1", "chunk_id": "c1"}]}

    with patch("app.services.agents.multi_agent.run_web_agent") as mock_web:
        result = run_multi_agent(user_id="u1", question="what does my contract say")
        mock_web.assert_not_called()

    assert result["route"] == "docs"
    assert len(result["answer_candidates"]) == 1
