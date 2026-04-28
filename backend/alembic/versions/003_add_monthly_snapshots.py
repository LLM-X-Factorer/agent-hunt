"""Add monthly snapshot tables for time-series trends.

Revision ID: 003
Revises: 002
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"


def upgrade() -> None:
    op.create_table(
        "skill_monthly_snapshot",
        sa.Column("skill_id", sa.String(100), nullable=False),
        sa.Column("market", sa.String(20), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("job_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("salary_median", sa.Integer(), nullable=True),
        sa.Column("salary_avg", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("skill_id", "market", "month", name="pk_skill_monthly"),
    )

    op.create_table(
        "role_monthly_snapshot",
        sa.Column("role_id", sa.String(50), nullable=False),
        sa.Column("market", sa.String(20), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("job_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("salary_median", sa.Integer(), nullable=True),
        sa.Column("salary_avg", sa.Integer(), nullable=True),
        sa.Column("top_skills", postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint("role_id", "market", "month", name="pk_role_monthly"),
    )

    op.create_table(
        "industry_monthly_snapshot",
        sa.Column("industry", sa.String(50), nullable=False),
        sa.Column("market", sa.String(20), nullable=False),
        sa.Column("month", sa.Date(), nullable=False),
        sa.Column("job_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("salary_median", sa.Integer(), nullable=True),
        sa.Column("salary_avg", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("industry", "market", "month", name="pk_industry_monthly"),
    )


def downgrade() -> None:
    op.drop_table("industry_monthly_snapshot")
    op.drop_table("role_monthly_snapshot")
    op.drop_table("skill_monthly_snapshot")
