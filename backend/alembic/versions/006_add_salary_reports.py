"""Add salary_reports table for #15.

Revision ID: 006
Revises: 005
"""
import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"


def upgrade() -> None:
    op.create_table(
        "salary_reports",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("source_record_id", sa.String(100), nullable=False),
        sa.Column("company", sa.String(255), nullable=False),
        sa.Column("role_title", sa.String(255), nullable=True),
        sa.Column("job_family", sa.String(100), nullable=True),
        sa.Column("level", sa.String(80), nullable=True),
        sa.Column("focus_tag", sa.String(80), nullable=True),
        sa.Column("location", sa.String(150), nullable=True),
        sa.Column("country", sa.String(50), nullable=True),
        sa.Column("market", sa.String(20), nullable=True),
        sa.Column("years_experience", sa.Integer(), nullable=True),
        sa.Column("years_at_company", sa.Integer(), nullable=True),
        sa.Column("base_salary", sa.Integer(), nullable=True),
        sa.Column("stock_grant_value", sa.Integer(), nullable=True),
        sa.Column("bonus_value", sa.Integer(), nullable=True),
        sa.Column("total_compensation", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(5), nullable=True),
        sa.Column("total_comp_rmb_monthly", sa.Integer(), nullable=True),
        sa.Column("offer_date", sa.Date(), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("source", "source_record_id", name="uq_salary_source_record"),
    )
    op.create_index("ix_salary_reports_source", "salary_reports", ["source"])
    op.create_index("ix_salary_reports_company", "salary_reports", ["company"])
    op.create_index("ix_salary_reports_job_family", "salary_reports", ["job_family"])
    op.create_index("ix_salary_reports_market", "salary_reports", ["market"])
    op.create_index(
        "ix_salary_reports_total_comp_rmb_monthly",
        "salary_reports",
        ["total_comp_rmb_monthly"],
    )


def downgrade() -> None:
    op.drop_table("salary_reports")
