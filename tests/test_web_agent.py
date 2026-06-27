"""web agent tests (provider always mocked, never calls a real API)"""
from unittest.mock import patch

from app.services.agents.web_agent import run_web_agent, build_web_context


def fake_provider(query):
    return [
        {"title": "AWS Free Tier docs", "url": "https://aws.amazon.com/free", "snippet": "credits valid 6 months"},
        {"title": "Some blog", "url": "https://example.com", "snippet": "unrelated content"},
    ]


def test_build_web_context_numbers_results():
    ctx = build_web_context(fake_provider("q"))
    assert ctx.startswith("[1] AWS Free Tier docs")
    assert "[2] Some blog" in ctx


@patch("app.services.agents.web_agent.gemini_generate")
def test_run_web_agent_maps_only_cited_sources(mock_gen):
    mock_gen.return_value = "AWS gives credits valid for 6 months [1]."

    out = run_web_agent("how long is aws free tier", provider=fake_provider)

    assert len(out["sources"]) == 1
    assert out["sources"][0]["url"] == "https://aws.amazon.com/free"


def test_run_web_agent_no_results_short_circuits():
    out = run_web_agent("q", provider=lambda q: [])
    assert out["answer"] == "No web results found for that."
    assert out["sources"] == []


@patch("app.services.agents.web_agent.gemini_generate")
def test_run_web_agent_ignores_out_of_range_marker(mock_gen):
    mock_gen.return_value = "Some claim [9] that doesn't map to a real result."
    out = run_web_agent("q", provider=fake_provider)
    assert out["sources"] == []
