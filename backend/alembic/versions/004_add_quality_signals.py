"""Add quality-signal fields to jobs table.

Revision ID: 004
Revises: 003
"""
import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"


def upgrade() -> None:
    op.add_column("jobs", sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("jobs", sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("jobs", sa.Column("seen_count", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("jobs", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))

    # Backfill from collected_at (best signal we have for existing rows).
    op.execute(
        "UPDATE jobs SET first_seen_at = collected_at, last_seen_at = collected_at "
        "WHERE first_seen_at IS NULL"
    )


def downgrade() -> None:
    op.drop_column("jobs", "closed_at")
    op.drop_column("jobs", "seen_count")
    op.drop_column("jobs", "last_seen_at")
    op.drop_column("jobs", "first_seen_at")
