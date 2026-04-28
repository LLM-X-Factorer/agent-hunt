# Supply-side data — what the *applicant* looks like (#14).
#
# We've only had demand side (JD) data; aijobfit's "diagnosis" can't tell
# users where they sit in the candidate distribution. ApplicantProfile fills
# that gap — each row = one disclosed application story (mostly from
# 牛客 / 一亩三分地 / 应届生网 BBS posts).
import datetime
import uuid

from sqlalchemy import Date, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ApplicantProfile(Base):
    __tablename__ = "applicant_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    source: Mapped[str] = mapped_column(String(40), index=True)
    source_record_id: Mapped[str] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Applicant background.
    school: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    school_tier: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # "985" | "211" | "double-first" | "international" | "other"
    major: Mapped[str | None] = mapped_column(String(80), nullable=True)
    degree: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # "bachelor" | "master" | "phd"
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # The application target.
    company: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    role_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role_id: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )  # mapped to analyze_roles ID for join with JD data
    market: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )  # "domestic" | "international"

    # Outcome.
    offer_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )  # "offered" | "rejected" | "interviewing" | "unknown"

    compensation_disclosed: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # RMB monthly if user self-reported

    # Original payload + LLM extraction for re-parsing.
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    posted_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    collected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint(
            "source", "source_record_id", name="uq_applicant_source_record"
        ),
    )
