import re

from app.services.generation_service import generate
from app.services.reranker_service import search_and_rerank

CITE_RE = re.compile(r"\[(\d+)\]")

PROMPT = """Answer the question using ONLY the numbered sources below.
Cite sources inline using [n] right after the claim they support.
If the sources don't contain the answer, say so plainly.

Sources:
{ctx}

Question: {q}
Answer:"""


def build_context(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{i}] {c.get('text', '')}" for i, c in enumerate(chunks, start=1))


def extract_used_citations(answer: str, chunks: list[dict]) -> list[dict]:
    used_idx = sorted({int(n) for n in CITE_RE.findall(answer)})
    sources = []
    for n in used_idx:
        if 1 <= n <= len(chunks):
            c = chunks[n - 1]
            sources.append(
                {
                    "marker": n,
                    "document_id": c.get("document_id") or c.get("doc_id"),
                    "doc_id": c.get("document_id") or c.get("doc_id"),
                    "chunk_id": c.get("chunk_id"),
                    "snippet": c.get("text", "")[:200],
                }
            )
    return sources


def answer_with_citations(user_id: int | str, question: str) -> dict:
    chunks = search_and_rerank(user_id, question, fetch_n=20, top_n=6)
    if not chunks:
        return {"answer": "No relevant documents found.", "sources": []}

    answer = generate(PROMPT.format(ctx=build_context(chunks), q=question))
    return {"answer": answer, "sources": extract_used_citations(answer, chunks)}
