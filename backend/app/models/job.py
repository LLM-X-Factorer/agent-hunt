# Job (JD) core model — stores raw + parsed job descriptions.
import datetime
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    platform_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("platforms.id"), index=True
    )
    platform_job_id: Mapped[str] = mapped_column(String(255))  # dedup within platform
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    raw_content: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10))  # "zh" | "en" | "mixed"

    # --- Structured fields (populated after LLM parsing) ---
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_size: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # "startup" | "mid" | "large" | "enterprise"
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    market: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )  # "domestic" | "international"
    industry: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    work_mode: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # "onsite" | "remote" | "hybrid"

    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)  # RMB monthly
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(
        String(5), nullable=True
    )  # original currency

    experience_min: Mapped[int | None] = mapped_column(Integer, nullable=True)  # years
    experience_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    education: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # "bachelor" | "master" | "phd" | "any"

    # --- Issue #11: graduate / campus / internship signals ---
    # "fresh" | "0-1y" | "1-3y" | "3-5y" | "5y+"
    experience_requirement: Mapped[str | None] = mapped_column(
        String(10), nullable=True, index=True
    )
    internship_friendly: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_campus: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # --- Issue #10: AI native vs AI augmented traditional ---
    # "ai_native" — algo / LLM eng / AI PM / AI sales etc.
    # "ai_augmented_traditional" — electrical eng + DL, medical imaging, quant, etc.
    role_type: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    # Filled only when role_type == "ai_augmented_traditional".
    # Examples: "电气工程师", "医生", "会计", "金融分析师".
    base_profession: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )

    required_skills: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    preferred_skills: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )
    responsibilities: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )

    # --- Metadata ---
    collected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    parsed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    parse_status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # "pending" | "parsed" | "failed"

    # --- Quality signals (#16) ---
    # first_seen_at = collected_at on first capture; last_seen_at bumps on every re-encounter.
    # seen_count > 1 → posting was re-published (招不到 / 流失大 signal).
    # closed_at populated by the liveness probe when the source URL 404s.
    first_seen_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    seen_count: Mapped[int] = mapped_column(Integer, default=1)
    closed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("platform_id", "platform_job_id", name="uq_job_platform_dedup"),
    )
