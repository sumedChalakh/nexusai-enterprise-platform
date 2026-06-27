import logging
import time
import hashlib
import random
from app.core.config import settings

log = logging.getLogger(__name__)

EMBED_MODEL = "text-embedding-004"
EMBED_DIM = 768
BATCH_SIZE = 100
MAX_RETRIES = 1
RETRY_BACKOFF = 0  # No backoff when using local fallback


def _get_client():
    from google import genai
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return client


def _fallback_embed(text: str) -> list[float]:
    """Deterministic pseudo-random embedding based on text hash (local fallback)."""
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    vec = [rng.gauss(0, 1) for _ in range(EMBED_DIM)]
    # Normalise to unit length for cosine similarity
    norm = sum(x * x for x in vec) ** 0.5 or 1.0
    return [x / norm for x in vec]


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """
    Embed a list of texts in batches of BATCH_SIZE.
    Returns a list of 768-dim float vectors, same order as input.
    Falls back to deterministic pseudo-random embeddings if Gemini API fails.
    """
    if not texts:
        return []

    try:
        client = _get_client()
        vectors: list[list[float]] = []
        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]
            vectors.extend(_embed_batch(client, batch, task_type))
        log.info("Embedded %d texts -> %d vectors (Gemini)", len(texts), len(vectors))
        return vectors
    except Exception as e:
        log.warning("Gemini embedding unavailable (%s) — using local fallback embeddings", e)
        vectors = [_fallback_embed(t) for t in texts]
        log.info("Generated %d local fallback vectors", len(vectors))
        return vectors


def _embed_batch(client, batch: list[str], task_type: str) -> list[list[float]]:
    from google.genai import types
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result = client.models.embed_content(
                model=EMBED_MODEL,
                contents=batch,
                config=types.EmbedContentConfig(task_type=task_type),
            )
            # New SDK returns a list of ContentEmbedding objects
            return [e.values for e in result.embeddings]
        except Exception as e:
            last_err = e
            wait = RETRY_BACKOFF * attempt
            log.warning("Embed batch attempt %d/%d failed: %s — retrying in %ds",
                        attempt, MAX_RETRIES, e, wait)
            time.sleep(wait)
    raise RuntimeError(f"Embedding failed after {MAX_RETRIES} attempts: {last_err}")


def embed_query(text: str) -> list[float]:
    """Single-text embed for search queries — uses RETRIEVAL_QUERY task type."""
    try:
        from google.genai import types
        client = _get_client()
        result = client.models.embed_content(
            model=EMBED_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
        )
        return result.embeddings[0].values
    except Exception as e:
        log.warning("Gemini query embedding unavailable (%s) — using local fallback", e)
        return _fallback_embed(text)
