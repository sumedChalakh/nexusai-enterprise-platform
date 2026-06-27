from app.services.agents.state import AgentState
from app.services.hybrid_search_service import hybrid_search
from app.services.reranker_service import rerank
from app.services.citation_service import build_context, extract_used_citations
from app.core.llm import gemini_generate
from app.core.qdrant import get_qdrant_client
from app.core.embeddings import embed_text
from app.core.config import settings

CITE_PROMPT = """Answer using ONLY the numbered sources below. Cite inline with [n].
If the sources don't contain the answer, say so.

Conversation so far:
{history}

Sources:
{ctx}

Question: {q}
Answer:"""

SYNTHESIZE_PROMPT = """Combine these candidate answers into one final answer.
Keep citations from each candidate distinguishable (e.g. mention "from your
documents" vs "from the web"). If they conflict, say so plainly.

{candidates}

Final answer:"""


def format_history(history: list[dict]) -> str:
    if not history:
        return "(no prior turns)"
    return "\n".join(f"{h['role']}: {h['content']}" for h in history)


def retrieve_node(state: AgentState) -> dict:
    chunks = hybrid_search(user_id=state["user_id"], query=state["question"], top_n=20)
    return {"retrieved": chunks}


def rerank_node(state: AgentState) -> dict:
    top = rerank(state["question"], state["retrieved"], top_n=6)
    return {"reranked": top}


def generate_node(state: AgentState) -> dict:
    if not state["reranked"]:
        return {"answer": "No relevant documents found for this question.", "sources": []}

    ctx = build_context(state["reranked"])
    prompt = CITE_PROMPT.format(history=format_history(state["chat_history"]), ctx=ctx, q=state["question"])
    answer = gemini_generate(prompt)
    sources = extract_used_citations(answer, state["reranked"])
    return {"answer": answer, "sources": sources}


def pdf_scoped_search(user_id: str, doc_id: str, query: str, top_n: int = 10) -> list[dict]:
    qc = get_qdrant_client()
    vec = embed_text(query)
    
    # Construct search filter scoped to user_id and doc_id
    from qdrant_client.models import FieldCondition, Filter, MatchValue
    query_filter = Filter(
        must=[
            FieldCondition(key="user_id", match=MatchValue(value=user_id)),
            FieldCondition(key="doc_id", match=MatchValue(value=doc_id))
        ]
    )
    
    res = qc.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=vec,
        query_filter=query_filter,
        limit=top_n,
    )
    return [
        {
            "chunk_id": r.payload.get("chunk_id"),
            "doc_id": r.payload.get("doc_id"),
            "text": r.payload.get("text"),
            "page": r.payload.get("page"),
            "score": r.score,
        }
        for r in res
    ]


def pdf_retrieve_node(state: dict) -> dict:
    doc_id = state.get("doc_id")
    if not doc_id:
        return {"error": "doc_id is required for the PDF agent", "retrieved": []}

    chunks = pdf_scoped_search(user_id=state["user_id"], doc_id=doc_id, query=state["question"])
    if not chunks:
        return {"error": f"no content found for doc_id={doc_id}", "retrieved": []}

    return {"retrieved": chunks}


def docs_branch_node(state: dict) -> dict:
    retrieved = retrieve_node(state)
    merged = {**state, **retrieved}
    reranked = rerank_node(merged)
    chunks = reranked["reranked"]

    if not chunks:
        return {"answer_candidates": [{"source": "docs", "text": "(nothing relevant found in your documents)"}]}

    snippet = build_context(chunks[:3])
    return {"answer_candidates": [{"source": "docs", "text": snippet}]}


def web_branch_node(state: dict) -> dict:
    from app.services.agents.web_agent import run_web_agent
    out = run_web_agent(state["question"])
    return {"answer_candidates": [{"source": "web", "text": out["answer"]}]}


def synthesize_node(state: dict) -> dict:
    candidates = state["answer_candidates"]
    if len(candidates) == 1:
        return {"answer": candidates[0]["text"], "sources": []}

    formatted = "\n\n".join(f"[{c['source']}] {c['text']}" for c in candidates)
    final = gemini_generate(SYNTHESIZE_PROMPT.format(candidates=formatted))
    return {"answer": final, "sources": []}
