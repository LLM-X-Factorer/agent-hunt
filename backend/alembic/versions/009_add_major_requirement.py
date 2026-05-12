"""Add major_requirement field to jobs (#33 / v0.12 A1).

Revision ID: 009
Revises: 008
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "009"
down_revision = "008"


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column(
            "major_requirement",
            postgresql.ARRAY(sa.String()),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_jobs_major_requirement",
        "jobs",
        ["major_requirement"],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_major_requirement", table_name="jobs")
    op.drop_column("jobs", "major_requirement")
