"""Add role_type, base_profession and graduate-friendly fields (#10 + #11).

Revision ID: 005
Revises: 004
"""
import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"


def upgrade() -> None:
    # #10 — distinguish ai_native vs ai_augmented_traditional roles.
    op.add_column("jobs", sa.Column("role_type", sa.String(30), nullable=True))
    op.add_column("jobs", sa.Column("base_profession", sa.String(50), nullable=True))
    op.create_index("ix_jobs_role_type", "jobs", ["role_type"])
    op.create_index("ix_jobs_base_profession", "jobs", ["base_profession"])

    # #11 — graduate / campus / internship signals.
    op.add_column(
        "jobs",
        sa.Column("experience_requirement", sa.String(10), nullable=True),
    )
    op.add_column("jobs", sa.Column("internship_friendly", sa.Boolean(), nullable=True))
    op.add_column("jobs", sa.Column("is_campus", sa.Boolean(), nullable=True))
    op.create_index(
        "ix_jobs_experience_requirement", "jobs", ["experience_requirement"]
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_experience_requirement", table_name="jobs")
    op.drop_column("jobs", "is_campus")
    op.drop_column("jobs", "internship_friendly")
    op.drop_column("jobs", "experience_requirement")
    op.drop_index("ix_jobs_base_profession", table_name="jobs")
    op.drop_index("ix_jobs_role_type", table_name="jobs")
    op.drop_column("jobs", "base_profession")
    op.drop_column("jobs", "role_type")
