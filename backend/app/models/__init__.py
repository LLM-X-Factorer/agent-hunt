# Re-export all models so Alembic can discover them.
from app.models.job import Job
from app.models.platform import Platform
from app.models.skill import Skill
from app.models.applicant_profile import ApplicantProfile
from app.models.salary_report import SalaryReport
from app.models.snapshot import (
    IndustryMonthlySnapshot,
    RoleMonthlySnapshot,
    SkillMonthlySnapshot,
)

__all__ = [
    "Platform",
    "Job",
    "Skill",
    "SalaryReport",
    "ApplicantProfile",
    "SkillMonthlySnapshot",
    "RoleMonthlySnapshot",
    "IndustryMonthlySnapshot",
]
