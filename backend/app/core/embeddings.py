from app.services.embedding_service import embed_query


def embed_text(text: str) -> list[float]:
    return embed_query(text)
