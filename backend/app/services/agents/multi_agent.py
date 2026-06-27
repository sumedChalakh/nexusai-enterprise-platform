from app.core.llm import gemini_generate
from app.services.agents.nodes import retrieve_node, rerank_node
from app.services.agents.web_agent import run_web_agent

COMBO_PROMPT = """Does answering this question well require BOTH the user's own
documents AND a general web search, or just one of those? Reply with ONLY one
word: both, docs, or web.

Question: {q}
Answer:"""

SYNTHESIZE_PROMPT = """Combine these candidate answers into one final answer.
Keep citations from each candidate distinguishable (e.g. mention "from your
documents" vs "from the web"). If they conflict, say so plainly.

{candidates}

Final answer:"""


def classify_combo(question: str) -> str:
    raw = gemini_generate(COMBO_PROMPT.format(q=question)).strip().lower()
    return raw if raw in {"both", "docs", "web"} else "docs"


def combo_router_node(state: dict) -> dict:
    return {"route": classify_combo(state["question"])}


def pick_combo_route(state: dict) -> str:
    return state["route"]


def docs_branch_node(state: dict) -> dict:
    retrieved = retrieve_node(state)
    merged = {**state, **retrieved}
    reranked = rerank_node(merged)
    chunks = reranked["reranked"]

    if not chunks:
        return {"answer_candidates": [{"source": "docs", "text": "(nothing relevant found in your documents)"}]}

    from app.services.citation_service import build_context
    snippet = build_context(chunks[:3])
    return {"answer_candidates": [{"source": "docs", "text": snippet}]}


def web_branch_node(state: dict) -> dict:
    out = run_web_agent(state["question"])
    return {"answer_candidates": [{"source": "web", "text": out["answer"]}]}


def synthesize_node(state: dict) -> dict:
    candidates = state["answer_candidates"]
    if len(candidates) == 1:
        return {"answer": candidates[0]["text"], "sources": []}

    formatted = "\n\n".join(f"[{c['source']}] {c['text']}" for c in candidates)
    final = gemini_generate(SYNTHESIZE_PROMPT.format(candidates=formatted))
    return {"answer": final, "sources": []}
