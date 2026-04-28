# Salary report — independent from Job. Stores reported (爆料) compensation
# data so we can show "JD asking 30k, actual TC 40k+ stock" deltas instead
# of letting users get anchored on inflated JD numbers.
import datetime
import uuid

from sqlalchemy import Date, DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SalaryReport(Base):
    __tablename__ = "salary_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Where it came from (eg "levels_fyi", "kanzhun_baoliao", "maimai_gongzi").
    source: Mapped[str] = mapped_column(String(40), index=True)
    # Stable ID within the source — for levels.fyi this is their per-sample uuid.
    source_record_id: Mapped[str] = mapped_column(String(100))

    company: Mapped[str] = mapped_column(String(255), index=True)
    role_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_family: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    level: Mapped[str | None] = mapped_column(String(80), nullable=True)  # "L4" / "Lead Software Engineer" / etc.
    focus_tag: Mapped[str | None] = mapped_column(String(80), nullable=True)  # "ML", "Full Stack" ...

    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    country: Mapped[str | None] = mapped_column(String(50), nullable=True)
    market: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )  # "domestic" | "international"

    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    years_at_company: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Compensation in original currency (yearly).
    base_salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stock_grant_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bonus_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_compensation: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(5), nullable=True)

    # Normalized to RMB monthly so we can compare with Job.salary_min/max directly.
    total_comp_rmb_monthly: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True
    )

    offer_date: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    collected_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("source", "source_record_id", name="uq_salary_source_record"),
    )
