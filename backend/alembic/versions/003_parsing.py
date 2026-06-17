"""add parsing columns to documents

Revision ID: 003_parsing
Revises: 002_documents
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa

revision = "003_parsing"
down_revision = "002_documents"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("documents", sa.Column("extracted_text", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("word_count", sa.Integer(), server_default="0"))
    op.add_column("documents", sa.Column("parse_error", sa.String(500), nullable=True))


def downgrade():
    op.drop_column("documents", "extracted_text")
    op.drop_column("documents", "word_count")
    op.drop_column("documents", "parse_error")
