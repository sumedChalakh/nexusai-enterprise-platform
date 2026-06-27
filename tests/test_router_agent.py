"""router_agent tests"""
from unittest.mock import patch

from app.services.agents.router_agent import classify_route, pick_route


@patch("app.services.agents.router_agent.gemini_generate")
def test_classify_route_accepts_valid_route(mock_llm):
    mock_llm.return_value = "sql"
    assert classify_route("how many documents do I have", has_doc_id=False) == "sql"


@patch("app.services.agents.router_agent.gemini_generate")
def test_classify_route_falls_back_to_rag_on_garbage(mock_llm):
    mock_llm.return_value = "i'm not sure, maybe something else entirely"
    assert classify_route("anything", has_doc_id=False) == "rag"


@patch("app.services.agents.router_agent.gemini_generate")
def test_classify_route_falls_back_to_rag_when_pdf_picked_without_doc_id(mock_llm):
    mock_llm.return_value = "pdf"
    assert classify_route("summarize this", has_doc_id=False) == "rag"


@patch("app.services.agents.router_agent.gemini_generate")
def test_classify_route_allows_pdf_when_doc_id_present(mock_llm):
    mock_llm.return_value = "pdf"
    assert classify_route("summarize this", has_doc_id=True) == "pdf"


def test_pick_route_reads_state_route_key():
    assert pick_route({"route": "web"}) == "web"
