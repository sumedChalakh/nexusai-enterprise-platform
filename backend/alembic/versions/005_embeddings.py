"""add embedding tracking columns

Revision ID: 005_embeddings
Revises: 004_chunks
Create Date: 2026-06-16
"""
from alembic import op
import sqlalchemy as sa

revision = "005_embeddings"
down_revision = "004_chunks"
branch_labels = None
depends_on = None


def upgrade():
    # Documents: track total embedded count
    op.add_column("documents", sa.Column("embedded_count", sa.Integer(), server_default="0"))

    # Extend DocStatus enum
    op.execute("ALTER TYPE docstatus ADD VALUE IF NOT EXISTS 'embedding'")
    op.execute("ALTER TYPE docstatus ADD VALUE IF NOT EXISTS 'embedded'")

    # Chunks: per-row embedded flag
    op.add_column("document_chunks", sa.Column("is_embedded", sa.Boolean(),
                  server_default="false", nullable=False))


def downgrade():
    op.drop_column("document_chunks", "is_embedded")
    op.drop_column("documents", "embedded_count")
    # Note: Postgres does not support removing enum values directly
