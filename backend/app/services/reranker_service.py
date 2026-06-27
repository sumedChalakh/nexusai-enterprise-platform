from app.services.hybrid_search_service import hybrid_search

_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
_model = None


def get_reranker():
    global _model
    if _model is None:
        from sentence_transformers import CrossEncoder

        _model = CrossEncoder(_MODEL_NAME, max_length=512)
    return _model


def rerank(query: str, candidates: list[dict], top_n: int = 5) -> list[dict]:
    if not candidates:
        return []
    ce = get_reranker()
    pairs = [(query, c.get("text", "")) for c in candidates]
    scores = ce.predict(pairs)

    for c, s in zip(candidates, scores):
        c["rerank_score"] = float(s)

    return sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)[:top_n]


def search_and_rerank(user_id: int | str, query: str, fetch_n: int = 20, top_n: int = 5) -> list[dict]:
    candidates = hybrid_search(user_id=user_id, query=query, top_n=fetch_n)
    return rerank(query, candidates, top_n=top_n)
