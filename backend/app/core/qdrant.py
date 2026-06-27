from app.services.qdrant_service import _get_client


def get_qdrant_client():
    return _get_client()
