"""Add source field to jobs (#12 + #17 attribution).

Revision ID: 008
Revises: 007
"""
import sqlalchemy as sa
from alembic import op

revision = "008"
down_revision = "007"


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column(
            "source",
            sa.String(20),
            nullable=False,
            server_default="platform",
        ),
    )
    op.create_index("ix_jobs_source", "jobs", ["source"])


def downgrade() -> None:
    op.drop_index("ix_jobs_source", table_name="jobs")
    op.drop_column("jobs", "source")
