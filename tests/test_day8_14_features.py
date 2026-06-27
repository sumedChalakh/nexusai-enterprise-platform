import uuid
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.chat_session import ChatSession, ChatSessionMessage
from app.services import chat_history_service as history
from app.services import conv_memory_service as memory
from app.services.citation_service import build_context, extract_used_citations
from app.services.hybrid_search_service import HybridSearcher
from app.services.reranker_service import rerank
from app.services.user_isolation_service import (
    assert_owns_s3_key,
    qdrant_user_filter,
    require_session_owner,
    scoped_s3_key,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine, tables=[ChatSession.__table__, ChatSessionMessage.__table__])
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def fake_user_id():
    return uuid.uuid4()


@pytest.fixture()
def fake_redis(monkeypatch):
    fakeredis = pytest.importorskip("fakeredis")
    client = fakeredis.FakeStrictRedis(decode_responses=True)
    monkeypatch.setattr(memory, "r", client)
    return client


def test_rrf_favors_items_ranked_high_in_both_lists():
    dense = [("a", 0.9), ("b", 0.8), ("c", 0.7)]
    bm25 = [("b", 5.0), ("a", 4.0), ("d", 3.0)]

    fused = HybridSearcher._rrf([dense, bm25])

    assert fused["a"] > fused["c"]
    assert fused["b"] > fused["d"]


def test_rrf_handles_disjoint_lists():
    fused = HybridSearcher._rrf([[("a", 0.9)], [("z", 9.0)]])

    assert "a" in fused and "z" in fused
    assert fused["a"] == fused["z"]


def test_rrf_empty_lists_returns_empty():
    assert HybridSearcher._rrf([[], []]) == {}


@patch("app.services.reranker_service.get_reranker")
def test_rerank_reorders_by_score(mock_get_reranker):
    mock_get_reranker.return_value.predict.return_value = [0.1, 0.9, 0.5]
    candidates = [
        {"text": "low relevance chunk"},
        {"text": "high relevance chunk"},
        {"text": "mid relevance chunk"},
    ]

    out = rerank("some query", candidates, top_n=3)

    assert [c["text"] for c in out] == [
        "high relevance chunk",
        "mid relevance chunk",
        "low relevance chunk",
    ]
    assert out[0]["rerank_score"] == 0.9


def test_rerank_empty_candidates_returns_empty():
    assert rerank("q", [], top_n=5) == []


@patch("app.services.reranker_service.get_reranker")
def test_rerank_respects_top_n(mock_get_reranker):
    mock_get_reranker.return_value.predict.return_value = [0.3, 0.6, 0.9, 0.1]
    out = rerank("q", [{"text": f"c{i}"} for i in range(4)], top_n=2)

    assert len(out) == 2


def _chunks():
    return [
        {"doc_id": "d1", "chunk_id": "c1", "text": "Revenue grew 20% in Q3."},
        {"doc_id": "d2", "chunk_id": "c2", "text": "Costs were flat year over year."},
        {"doc_id": "d3", "chunk_id": "c3", "text": "Headcount increased by 10."},
    ]


def test_extract_used_citations_picks_only_referenced_markers():
    sources = extract_used_citations("Revenue grew [1] while costs stayed flat [2].", _chunks())

    assert [s["marker"] for s in sources] == [1, 2]
    assert sources[0]["doc_id"] == "d1"
    assert sources[1]["doc_id"] == "d2"


def test_extract_used_citations_ignores_out_of_range_markers():
    assert extract_used_citations("Some claim [9] with no matching source.", _chunks()) == []


def test_extract_used_citations_dedupes_and_sorts():
    sources = extract_used_citations("Claim a [3] and claim b [1] and again [3].", _chunks())
    assert [s["marker"] for s in sources] == [1, 3]


def test_build_context_numbers_chunks_in_order():
    ctx = build_context(_chunks())
    assert ctx.startswith("[1] Revenue grew 20% in Q3.")
    assert "[3] Headcount increased by 10." in ctx


def test_create_session_sets_owner(db, fake_user_id):
    session = history.create_session(db, fake_user_id, title="Resume help")
    assert session.user_id == str(fake_user_id)
    assert session.title == "Resume help"


def test_add_and_get_messages_in_order(db, fake_user_id):
    session = history.create_session(db, fake_user_id)
    history.add_message(db, session.id, "user", "what is xgboost")
    history.add_message(db, session.id, "assistant", "a gradient boosting library")
    history.add_message(db, session.id, "user", "give an example")

    msgs = history.get_messages(db, session.id)

    assert [m.content for m in msgs] == [
        "what is xgboost",
        "a gradient boosting library",
        "give an example",
    ]


def test_get_messages_respects_limit(db, fake_user_id):
    session = history.create_session(db, fake_user_id)
    for i in range(10):
        history.add_message(db, session.id, "user", f"msg {i}")

    msgs = history.get_messages(db, session.id, limit=3)

    assert len(msgs) == 3
    assert msgs[-1].content == "msg 9"


def test_list_sessions_only_returns_owner_sessions(db, fake_user_id):
    other_user = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    history.create_session(db, fake_user_id, title="mine")
    history.create_session(db, other_user, title="not mine")

    rows = history.list_sessions(db, fake_user_id)

    assert len(rows) == 1
    assert rows[0].title == "mine"


def test_format_for_llm_strips_to_role_content(db, fake_user_id):
    session = history.create_session(db, fake_user_id)
    history.add_message(db, session.id, "user", "hello")

    assert history.format_for_llm(history.get_messages(db, session.id)) == [
        {"role": "user", "content": "hello"}
    ]


def test_push_turn_then_get_window(fake_redis):
    memory.push_turn("sess1", "user", "hi")
    memory.push_turn("sess1", "assistant", "hello")

    assert memory.get_window("sess1", db_fallback=False) == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


def test_window_trims_to_max_size(fake_redis):
    for i in range(memory.WINDOW + 5):
        memory.push_turn("sess2", "user", f"turn {i}")

    window = memory.get_window("sess2", db_fallback=False)

    assert len(window) == memory.WINDOW
    assert window[-1]["content"] == f"turn {memory.WINDOW + 4}"
    assert window[0]["content"] == "turn 5"


def test_clear_session_removes_key(fake_redis):
    memory.push_turn("sess3", "user", "hi")
    memory.clear_session("sess3")

    assert memory.get_window("sess3", db_fallback=False) == []


def test_get_window_cold_cache_no_fallback_returns_empty(fake_redis):
    assert memory.get_window("never-seen-session", db_fallback=False) == []


def test_owner_can_access_own_session(db, fake_user_id):
    session = history.create_session(db, fake_user_id)
    user = SimpleNamespace(id=fake_user_id)

    out = require_session_owner(session_id=str(session.id), user=user, db=db)

    assert out.id == session.id


def test_non_owner_gets_403(db, fake_user_id):
    session = history.create_session(db, fake_user_id)
    other_user = SimpleNamespace(id=uuid.UUID("99999999-9999-9999-9999-999999999999"))

    with pytest.raises(HTTPException) as exc:
        require_session_owner(session_id=str(session.id), user=other_user, db=db)

    assert exc.value.status_code == 403


def test_missing_session_gets_404(db, fake_user_id):
    user = SimpleNamespace(id=fake_user_id)

    with pytest.raises(HTTPException) as exc:
        require_session_owner(session_id="00000000-0000-0000-0000-000000000000", user=user, db=db)

    assert exc.value.status_code == 404


def test_scoped_s3_key_is_namespaced_per_user():
    assert scoped_s3_key("u1", "resume.pdf") == "users/u1/docs/resume.pdf"


def test_assert_owns_s3_key_blocks_cross_user_path():
    with pytest.raises(HTTPException) as exc:
        assert_owns_s3_key("u1", "users/u2/docs/resume.pdf")
    assert exc.value.status_code == 403


def test_qdrant_user_filter_shape():
    assert qdrant_user_filter("u1") == {"must": [{"key": "user_id", "match": {"value": "u1"}}]}
