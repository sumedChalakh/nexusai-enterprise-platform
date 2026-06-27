import json

from app.core.llm import gemini_generate
from app.services.agents.sql_tools import TOOLS

INTENT_PROMPT = """Classify this question into exactly one of these intents and extract params.
Reply with ONLY raw JSON, no markdown fences, no extra text.

Intents:
- count_documents: no params
- list_documents: optional "status" (one of: uploaded, processing, ready, chunking, chunked, embedding, embedded, failed), optional "limit" (int, default 10)
- document_stats: no params
- unknown: question isn't about the user's documents at all

Question: {q}

JSON:"""


def classify_intent(question: str) -> dict:
    raw = gemini_generate(INTENT_PROMPT.format(q=question))
    try:
        parsed = json.loads(raw.strip())
    except (json.JSONDecodeError, AttributeError):
        return {"intent": "unknown", "params": {}}

    intent = parsed.get("intent", "unknown")
    if intent not in TOOLS:
        return {"intent": "unknown", "params": {}}

    return {"intent": intent, "params": parsed.get("params", {}) or {}}


def run_sql_agent(db, user_id: str, question: str) -> dict:
    decision = classify_intent(question)
    intent = decision["intent"]

    if intent == "unknown" or intent not in TOOLS:
        return {
            "answer": "That doesn't look like a question about your documents - try asking about counts, status, or recent uploads.",
            "sources": [],
        }

    tool_fn = TOOLS[intent]
    result = tool_fn(db, user_id, **decision["params"])
    return {"answer": result["text"], "sources": [], "sql_result": result.get("rows", [])}


def sql_agent_node(state: dict, db) -> dict:
    out = run_sql_agent(db, state["user_id"], state["question"])
    return {"answer": out["answer"], "sources": out["sources"]}
