# Monthly snapshot tables for time-series trends.
# Issue #13: capture skill / role / industry stats by month so we can
# answer "is X declining" type questions instead of always working from a
# fresh-overwritten snapshot.
import datetime

from sqlalchemy import Date, Integer, PrimaryKeyConstraint, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SkillMonthlySnapshot(Base):
    __tablename__ = "skill_monthly_snapshot"

    skill_id: Mapped[str] = mapped_column(String(100))
    market: Mapped[str] = mapped_column(String(20))  # "domestic" | "international"
    month: Mapped[datetime.date] = mapped_column(Date)  # first day of month

    job_count: Mapped[int] = mapped_column(Integer, default=0)
    salary_median: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("skill_id", "market", "month", name="pk_skill_monthly"),
    )


class RoleMonthlySnapshot(Base):
    __tablename__ = "role_monthly_snapshot"

    role_id: Mapped[str] = mapped_column(String(50))
    market: Mapped[str] = mapped_column(String(20))
    month: Mapped[datetime.date] = mapped_column(Date)

    job_count: Mapped[int] = mapped_column(Integer, default=0)
    salary_median: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top_skills: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("role_id", "market", "month", name="pk_role_monthly"),
    )


class IndustryMonthlySnapshot(Base):
    __tablename__ = "industry_monthly_snapshot"

    industry: Mapped[str] = mapped_column(String(50))
    market: Mapped[str] = mapped_column(String(20))
    month: Mapped[datetime.date] = mapped_column(Date)

    job_count: Mapped[int] = mapped_column(Integer, default=0)
    salary_median: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint("industry", "market", "month", name="pk_industry_monthly"),
    )
