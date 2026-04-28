"""Add applicant_profiles table for #14.

Revision ID: 007
Revises: 006
"""
import sqlalchemy as sa
from alembic import op

revision = "007"
down_revision = "006"


def upgrade() -> None:
    op.create_table(
        "applicant_profiles",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(40), nullable=False),
        sa.Column("source_record_id", sa.String(100), nullable=False),
        sa.Column("source_url", sa.String(1024), nullable=True),
        sa.Column("school", sa.String(120), nullable=True),
        sa.Column("school_tier", sa.String(20), nullable=True),
        sa.Column("major", sa.String(80), nullable=True),
        sa.Column("degree", sa.String(20), nullable=True),
        sa.Column("graduation_year", sa.Integer(), nullable=True),
        sa.Column("years_experience", sa.Integer(), nullable=True),
        sa.Column("company", sa.String(255), nullable=True),
        sa.Column("role_title", sa.String(255), nullable=True),
        sa.Column("role_id", sa.String(50), nullable=True),
        sa.Column("market", sa.String(20), nullable=True),
        sa.Column("offer_status", sa.String(20), nullable=True),
        sa.Column("compensation_disclosed", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("parsed_json", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("posted_date", sa.Date(), nullable=True),
        sa.Column(
            "collected_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "source", "source_record_id", name="uq_applicant_source_record"
        ),
    )
    op.create_index("ix_applicant_profiles_source", "applicant_profiles", ["source"])
    op.create_index("ix_applicant_profiles_school", "applicant_profiles", ["school"])
    op.create_index("ix_applicant_profiles_company", "applicant_profiles", ["company"])
    op.create_index("ix_applicant_profiles_role_id", "applicant_profiles", ["role_id"])
    op.create_index("ix_applicant_profiles_market", "applicant_profiles", ["market"])
    op.create_index(
        "ix_applicant_profiles_offer_status", "applicant_profiles", ["offer_status"]
    )


def downgrade() -> None:
    op.drop_table("applicant_profiles")
