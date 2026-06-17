"""create documents table

Revision ID: 002_documents
Revises: 001_users
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa

revision = "002_documents"
down_revision = "001_users"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("s3_key", sa.String(500), nullable=False, unique=True),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), default=0),
        sa.Column(
            "status",
            sa.Enum("uploaded", "processing", "ready", "failed", name="docstatus"),
            nullable=False,
            server_default="uploaded",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    op.create_index("ix_documents_user_id", "documents", ["user_id"])


def downgrade():
    op.drop_index("ix_documents_user_id", table_name="documents")
    op.drop_table("documents")
    op.execute("DROP TYPE IF EXISTS docstatus")
