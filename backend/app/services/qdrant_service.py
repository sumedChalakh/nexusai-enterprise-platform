import logging
from app.core.config import settings
from app.services.embedding_service import EMBED_DIM

log = logging.getLogger(__name__)

COLLECTION_NAME = "nexusai_chunks"


def _get_client():
    from qdrant_client import QdrantClient
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


def ensure_collection() -> None:
    """Idempotent — creates the collection only if it doesn't already exist."""
    from qdrant_client.models import Distance, VectorParams

    client = _get_client()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in existing:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
    )
    log.info("Created Qdrant collection: %s", COLLECTION_NAME)


def upsert_chunks(points: list[dict]) -> None:
    """
    points: [{ id, vector, payload: {document_id, user_id, chunk_id, chunk_index, text, page_number} }]
    Point id must be a positive int or UUID string — we use the chunk's DB id.
    """
    from qdrant_client.models import PointStruct

    if not points:
        return

    client = _get_client()
    ensure_collection()

    structs = [
        PointStruct(id=pt["id"], vector=pt["vector"], payload=pt["payload"])
        for pt in points
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=structs)
    log.info("Upserted %d points into Qdrant", len(structs))


def search(
    query_vector: list[float],
    user_id: int,
    document_id: int | None = None,
    limit: int = 5,
    score_threshold: float = 0.0,
) -> list[dict]:
    """
    Vector similarity search, always filtered by user_id for isolation.
    Optionally filter to a single document.
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = _get_client()
    ensure_collection()

    must = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
    if document_id is not None:
        must.append(FieldCondition(key="document_id", match=MatchValue(value=document_id)))

    try:
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=Filter(must=must),
            limit=limit,
            score_threshold=score_threshold or None,
        )
    except Exception as e:
        log.warning("Qdrant search failed: %s", e)
        return []

    return [
        {
            "chunk_id": r.payload.get("chunk_id"),
            "document_id": r.payload.get("document_id"),
            "chunk_index": r.payload.get("chunk_index"),
            "text": r.payload.get("text"),
            "page_number": r.payload.get("page_number"),
            "score": round(r.score, 4),
        }
        for r in results
    ]


def delete_by_document(document_id: int) -> None:
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    client = _get_client()
    ensure_collection()
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
            ),
        )
        log.info("Deleted Qdrant points for document %d", document_id)
    except Exception as e:
        log.warning("Failed to delete Qdrant points for document %d: %s", document_id, e)


def collection_stats() -> dict:
    client = _get_client()
    info = client.get_collection(COLLECTION_NAME)
    return {
        "points_count": info.points_count,
        "vectors_count": info.vectors_count,
        "status": info.status,
    }
