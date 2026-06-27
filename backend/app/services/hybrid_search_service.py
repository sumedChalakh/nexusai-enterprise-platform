import re

from app.services.embedding_service import embed_query
from app.services.qdrant_service import COLLECTION_NAME, _get_client

_tok_re = re.compile(r"[a-z0-9]+")


def tok(s: str) -> list[str]:
    return _tok_re.findall((s or "").lower())


class HybridSearcher:
    """Dense vector search plus BM25 keyword search, fused with RRF."""

    def __init__(self, user_id: int | str, top_k_dense: int = 30):
        self.qc = _get_client()
        self.user_id = user_id
        self.top_k_dense = top_k_dense

    def _user_filter(self):
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        return Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=self.user_id))])

    def _fetch_corpus(self) -> list:
        out, offset = [], None
        while True:
            pts, offset = self.qc.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=self._user_filter(),
                limit=256,
                offset=offset,
                with_payload=True,
            )
            out.extend(pts)
            if offset is None:
                break
        return out

    def _bm25_rank(self, query: str, corpus: list) -> list[tuple[str, float]]:
        if not corpus:
            return []
        from rank_bm25 import BM25Okapi

        texts = [p.payload.get("text", "") for p in corpus]
        bm25 = BM25Okapi([tok(t) for t in texts])
        scores = bm25.get_scores(tok(query))
        ranked = sorted(zip([str(p.id) for p in corpus], scores), key=lambda x: x[1], reverse=True)
        return ranked[:50]

    def _dense_rank(self, query: str) -> list[tuple[str, float]]:
        vec = embed_query(query)
        res = self.qc.search(
            collection_name=COLLECTION_NAME,
            query_vector=vec,
            query_filter=self._user_filter(),
            limit=self.top_k_dense,
        )
        return [(str(r.id), r.score) for r in res]

    @staticmethod
    def _rrf(rank_lists: list[list[tuple[str, float]]], k: int = 60) -> dict[str, float]:
        fused: dict[str, float] = {}
        for lst in rank_lists:
            for rank, (pid, _) in enumerate(lst, start=1):
                fused[pid] = fused.get(pid, 0.0) + 1.0 / (k + rank)
        return fused

    def search(self, query: str, top_n: int = 8) -> list[dict]:
        corpus = self._fetch_corpus()
        bm25_ranked = self._bm25_rank(query, corpus)
        dense_ranked = self._dense_rank(query)
        fused = self._rrf([dense_ranked, bm25_ranked])
        top_ids = sorted(fused, key=fused.get, reverse=True)[:top_n]

        by_id = {str(p.id): p for p in corpus}
        results = []
        for pid in top_ids:
            p = by_id.get(pid)
            if p is None:
                continue
            document_id = p.payload.get("document_id")
            results.append(
                {
                    "chunk_id": p.payload.get("chunk_id"),
                    "document_id": document_id,
                    "doc_id": document_id,
                    "chunk_index": p.payload.get("chunk_index"),
                    "page_number": p.payload.get("page_number"),
                    "text": p.payload.get("text", ""),
                    "fused_score": fused[pid],
                }
            )
        return results


def hybrid_search(user_id: int | str, query: str, top_n: int = 8) -> list[dict]:
    return HybridSearcher(user_id).search(query, top_n)
