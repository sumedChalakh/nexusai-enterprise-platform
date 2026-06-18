"""create document_chunks table

Revision ID: 004_chunks
Revises: 003_parsing
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa

revision = "004_chunks"
down_revision = "003_parsing"
branch_labels = None
depends_on = None


def upgrade():
    # Add chunk_count to documents
    op.add_column("documents", sa.Column("chunk_count", sa.Integer(), server_default="0"))

    # Extend DocStatus enum with new values
    op.execute("ALTER TYPE docstatus ADD VALUE IF NOT EXISTS 'chunking'")
    op.execute("ALTER TYPE docstatus ADD VALUE IF NOT EXISTS 'chunked'")

    # Create document_chunks table
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(),
                  sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("start_char", sa.Integer(), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.Column("page_number", sa.SmallInteger(), nullable=True),
        sa.Column("token_estimate", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("ix_chunks_doc_index", "document_chunks", ["document_id", "chunk_index"], unique=True)


def downgrade():
    op.drop_index("ix_chunks_doc_index", table_name="document_chunks")
    op.drop_index("ix_chunks_document_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_column("documents", "chunk_count")
