"""sql_agent tests: classification safety + dispatch correctness"""
import uuid
from unittest.mock import patch

from app.services.agents.sql_agent import classify_intent, run_sql_agent
from app.models.document import Document, DocStatus


@patch("app.services.agents.sql_agent.gemini_generate")
def test_classify_intent_parses_valid_json(mock_llm):
    mock_llm.return_value = '{"intent": "count_documents", "params": {}}'
    out = classify_intent("how many documents do I have")
    assert out["intent"] == "count_documents"


@patch("app.services.agents.sql_agent.gemini_generate")
def test_classify_intent_falls_back_on_garbage_response(mock_llm):
    mock_llm.return_value = "sure! here's some markdown ```json{not valid}```"
    out = classify_intent("anything")
    assert out["intent"] == "unknown"


@patch("app.services.agents.sql_agent.gemini_generate")
def test_classify_intent_rejects_intent_not_on_allowlist(mock_llm):
    mock_llm.return_value = '{"intent": "delete_all_documents", "params": {}}'
    out = classify_intent("delete everything")
    assert out["intent"] == "unknown"


@patch("app.services.agents.sql_agent.classify_intent")
def test_run_sql_agent_unknown_intent_never_touches_db(mock_classify, db):
    mock_classify.return_value = {"intent": "unknown", "params": {}}
    out = run_sql_agent(db, "u1", "what's the weather today")
    assert "documents" in out["answer"]
    assert out["sources"] == []


@patch("app.services.agents.sql_agent.classify_intent")
def test_run_sql_agent_dispatches_to_correct_tool(mock_classify, db):
    u1 = 1
    db.add(Document(
        user_id=u1,
        original_name="a.pdf",
        s3_key=f"keys/{u1}/a.pdf",
        content_type="application/pdf",
        status=DocStatus.ready
    ))
    db.commit()

    mock_classify.return_value = {"intent": "count_documents", "params": {}}
    out = run_sql_agent(db, u1, "how many docs")

    assert "1 document" in out["answer"]
