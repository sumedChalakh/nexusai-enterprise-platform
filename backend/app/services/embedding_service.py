import logging
import time
from app.core.config import settings

log = logging.getLogger(__name__)

EMBED_MODEL = "models/text-embedding-004"
EMBED_DIM = 768
BATCH_SIZE = 100
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubles each retry


def _get_client():
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """
    Embed a list of texts in batches of BATCH_SIZE.
    Returns a list of 768-dim float vectors, same order as input.
    Retries each batch up to MAX_RETRIES times on transient failure.
    """
    if not texts:
        return []

    genai = _get_client()
    vectors: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        vectors.extend(_embed_batch(genai, batch, task_type))

    log.info("Embedded %d texts -> %d vectors", len(texts), len(vectors))
    return vectors


def _embed_batch(genai, batch: list[str], task_type: str) -> list[list[float]]:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = genai.embed_content(
                model=EMBED_MODEL,
                content=batch,
                task_type=task_type,
            )
            embeddings = result["embedding"]
            # API returns a single vector for single string, list of vectors for list input
            if isinstance(embeddings[0], float):
                embeddings = [embeddings]
            return embeddings
        except Exception as e:
            last_err = e
            wait = RETRY_BACKOFF * attempt
            log.warning("Embed batch attempt %d/%d failed: %s — retrying in %ds",
                        attempt, MAX_RETRIES, e, wait)
            time.sleep(wait)
    raise RuntimeError(f"Embedding failed after {MAX_RETRIES} attempts: {last_err}")


def embed_query(text: str) -> list[float]:
    """Single-text embed for search queries — uses RETRIEVAL_QUERY task type."""
    genai = _get_client()
    result = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type="RETRIEVAL_QUERY",
    )
    return result["embedding"]
