"""Add industry column to jobs table.

Revision ID: 002
Revises: 001
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"


def upgrade() -> None:
    op.add_column("jobs", sa.Column("industry", sa.String(50), nullable=True))
    op.create_index("ix_jobs_industry", "jobs", ["industry"])


def downgrade() -> None:
    op.drop_index("ix_jobs_industry", table_name="jobs")
    op.drop_column("jobs", "industry")
