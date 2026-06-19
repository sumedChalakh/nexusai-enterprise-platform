import logging
from sqlalchemy.orm import Session
from app.models.chat_message import ChatMessage
from app.services.embedding_service import embed_query
from app.services import qdrant_service
from app.services.generation_service import generate, generate_stream

log = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = """You are NexusAI, an enterprise knowledge assistant. \
Answer the user's question using ONLY the context passages provided below. \
If the context does not contain enough information to answer confidently, say so honestly \
instead of guessing or using outside knowledge. \
When you use information from a passage, cite it inline using its source number, e.g. [Source 2]. \
Keep answers concise and directly relevant to the question."""

NO_CONTEXT_MESSAGE = (
    "I couldn't find any relevant information in your documents to answer this question. "
    "Try rephrasing, or upload a document that covers this topic."
)

RETRIEVAL_LIMIT_DEFAULT = 5
SCORE_THRESHOLD = 0.55   # below this, a chunk is probably not relevant enough to include


def retrieve_context(query: str, user_id: int, document_id: int | None, limit: int) -> list[dict]:
    """Embed the query and fetch the top-k most similar chunks from Qdrant."""
    vector = embed_query(query)
    results = qdrant_service.search(
        query_vector=vector,
        user_id=user_id,
        document_id=document_id,
        limit=limit,
        score_threshold=SCORE_THRESHOLD,
    )
    return results


def build_prompt(question: str, chunks: list[dict]) -> str:
    if not chunks:
        return ""  # signals caller to skip generation entirely

    context_blocks = []
    for i, c in enumerate(chunks, start=1):
        page_info = f" (Page {c['page_number']})" if c.get("page_number") else ""
        context_blocks.append(f"[Source {i}]{page_info}\n{c['text']}")

    context_text = "\n\n".join(context_blocks)

    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"--- CONTEXT ---\n{context_text}\n\n"
        f"--- QUESTION ---\n{question}\n\n"
        f"--- ANSWER ---"
    )


def _save_message(db: Session, user_id: int, document_id: int | None,
                   question: str, answer: str, chunks: list[dict]) -> ChatMessage:
    msg = ChatMessage(
        user_id=user_id,
        document_id=document_id,
        question=question,
        answer=answer,
        source_chunk_ids=[c["chunk_id"] for c in chunks],
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def ask(db: Session, user_id: int, question: str,
        document_id: int | None = None, limit: int = RETRIEVAL_LIMIT_DEFAULT) -> dict:
    """
    Full RAG loop (non-streaming): retrieve → build prompt → generate → persist.
    Returns dict with answer, sources, and the saved ChatMessage id.
    """
    chunks = retrieve_context(question, user_id, document_id, limit)

    if not chunks:
        msg = _save_message(db, user_id, document_id, question, NO_CONTEXT_MESSAGE, [])
        return {"chat_id": msg.id, "answer": NO_CONTEXT_MESSAGE, "sources": []}

    prompt = build_prompt(question, chunks)
    answer = generate(prompt)

    msg = _save_message(db, user_id, document_id, question, answer, chunks)

    return {
        "chat_id": msg.id,
        "answer": answer,
        "sources": [
            {
                "chunk_id": c["chunk_id"],
                "document_id": c["document_id"],
                "chunk_index": c["chunk_index"],
                "page_number": c.get("page_number"),
                "score": c["score"],
                "text_preview": c["text"][:200],
            }
            for c in chunks
        ],
    }


def ask_stream(db: Session, user_id: int, question: str,
                document_id: int | None = None, limit: int = RETRIEVAL_LIMIT_DEFAULT):
    """
    Streaming RAG loop. Yields dicts: {"type": "token"|"sources", "data": ...}
    Persists the full message only after the stream completes.
    The endpoint layer wraps each yield in SSE 'data: ' framing.
    """
    chunks = retrieve_context(question, user_id, document_id, limit)

    if not chunks:
        yield {"type": "token", "data": NO_CONTEXT_MESSAGE}
        yield {"type": "sources", "data": []}
        _save_message(db, user_id, document_id, question, NO_CONTEXT_MESSAGE, [])
        return

    prompt = build_prompt(question, chunks)
    full_answer = []

    for piece in generate_stream(prompt):
        full_answer.append(piece)
        yield {"type": "token", "data": piece}

    source_payload = [
        {
            "chunk_id": c["chunk_id"],
            "document_id": c["document_id"],
            "chunk_index": c["chunk_index"],
            "page_number": c.get("page_number"),
            "score": c["score"],
        }
        for c in chunks
    ]
    yield {"type": "sources", "data": source_payload}

    _save_message(db, user_id, document_id, question, "".join(full_answer), chunks)
