import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.document import Document, DocStatus
from app.models.document_chunk import DocumentChunk
from app.services import s3_service, parser_service, qdrant_service
from app.services.chunking_service import chunk_document
from app.services.embedding_service import embed_texts

log = logging.getLogger(__name__)


def _get_s3_content(s3_key: str) -> bytes:
    import os
    local_path = os.path.join("/app/uploads", s3_key)
    if os.path.exists(local_path):
        log.info("Reading %s from local filesystem fallback", s3_key)
        with open(local_path, "rb") as f:
            return f.read()

    import boto3
    from botocore.config import Config
    from app.core.config import settings

    client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        config=Config(signature_version="s3v4"),
    )
    resp = client.get_object(Bucket=settings.S3_BUCKET, Key=s3_key)
    return resp["Body"].read()


def process_document(doc_id: int) -> None:
    """Stage 1 — Parse: uploaded → processing → ready. Chains to chunking."""
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            log.error("Document %d not found", doc_id)
            return

        doc.status = DocStatus.processing
        db.commit()

        content = _get_s3_content(doc.s3_key)
        extracted = parser_service.parse_document(content, doc.content_type)

        doc.extracted_text = extracted
        doc.word_count = len(extracted.split())
        doc.status = DocStatus.ready
        db.commit()
        log.info("Doc %d parsed — %d words", doc_id, doc.word_count)

    except Exception as e:
        log.error("Parse failed for doc %d: %s", doc_id, e)
        _mark_failed(db, doc_id, str(e))
        db.close()
        return

    db.close()
    chunk_document_task(doc_id)


def chunk_document_task(doc_id: int) -> None:
    """Stage 2 — Chunk: ready → chunking → chunked. Chains to embedding."""
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc or not doc.extracted_text:
            log.error("Cannot chunk doc %d: missing or no text", doc_id)
            return

        doc.status = DocStatus.chunking
        db.commit()

        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).delete()
        db.commit()

        chunks = chunk_document(doc.extracted_text)

        db.bulk_insert_mappings(DocumentChunk, [
            {
                "document_id": doc_id,
                "chunk_index": c.chunk_index,
                "text": c.text,
                "start_char": c.start_char,
                "end_char": c.end_char,
                "page_number": c.page_number,
                "token_estimate": c.token_estimate,
            }
            for c in chunks
        ])

        doc.chunk_count = len(chunks)
        doc.status = DocStatus.chunked
        db.commit()
        log.info("Doc %d chunked into %d chunks", doc_id, len(chunks))

    except Exception as e:
        log.error("Chunk failed for doc %d: %s", doc_id, e)
        _mark_failed(db, doc_id, f"Chunk error: {e}")
        db.close()
        return

    db.close()
    embed_document_task(doc_id)


def embed_document_task(doc_id: int) -> None:
    """Stage 3 — Embed: chunked → embedding → embedded. Writes vectors to Qdrant."""
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            log.error("Document %d not found", doc_id)
            return

        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == doc_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )
        if not chunks:
            log.error("No chunks to embed for doc %d", doc_id)
            return

        doc.status = DocStatus.embedding
        db.commit()

        # Clear any stale vectors for this doc (safe re-run)
        qdrant_service.delete_by_document(doc_id)

        texts = [c.text for c in chunks]
        vectors = embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")

        points = [
            {
                "id": chunks[i].id,
                "vector": vectors[i],
                "payload": {
                    "chunk_id": chunks[i].id,
                    "document_id": doc_id,
                    "user_id": doc.user_id,
                    "chunk_index": chunks[i].chunk_index,
                    "text": chunks[i].text,
                    "page_number": chunks[i].page_number,
                },
            }
            for i in range(len(chunks))
        ]
        qdrant_service.upsert_chunks(points)

        db.query(DocumentChunk).filter(DocumentChunk.document_id == doc_id).update(
            {DocumentChunk.is_embedded: True}
        )
        doc.embedded_count = len(points)
        doc.status = DocStatus.embedded
        db.commit()
        log.info("Doc %d embedded — %d vectors stored", doc_id, len(points))

    except Exception as e:
        log.error("Embedding failed for doc %d: %s", doc_id, e)
        _mark_failed(db, doc_id, f"Embed error: {e}")
    finally:
        db.close()


def _mark_failed(db: Session, doc_id: int, error: str) -> None:
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = DocStatus.failed
            doc.parse_error = error[:500]
            db.commit()
    except Exception:
        pass
