from __future__ import annotations

from pydantic import BaseModel, Field


# --- Skill normalization ---


class NormalizationResult(BaseModel):
    jobs_processed: int
    skills_updated: int
    unmatched_terms: int


class UnmatchedTerm(BaseModel):
    term: str
    count: int


class SkillResponse(BaseModel):
    id: str
    canonical_name: str
    category: str
    subcategory: str | None
    domestic_count: int
    international_count: int
    total_count: int
    avg_salary_with: int | None

    model_config = {"from_attributes": True}


# --- Salary analysis ---


class SalaryBucket(BaseModel):
    range_label: str
    count: int
    percentage: float


class SalaryDistribution(BaseModel):
    market: str | None
    total_jobs_with_salary: int
    buckets: list[SalaryBucket]


class SkillSalary(BaseModel):
    skill_id: str
    canonical_name: str
    job_count: int
    avg_salary: int
    min_salary: int
    max_salary: int


class ExperienceSalary(BaseModel):
    bracket: str
    job_count: int
    avg_salary: int


class PlatformSalary(BaseModel):
    platform_id: str
    job_count: int
    avg_salary: int


# --- Cross-market ---


class MarketSkillRank(BaseModel):
    skill_id: str
    canonical_name: str
    count: int
    percentage: float


class SkillGap(BaseModel):
    skill_id: str
    canonical_name: str
    domestic_count: int
    international_count: int
    domestic_pct: float
    international_pct: float
    gap: float
    dominant_market: str


class CrossMarketSkills(BaseModel):
    domestic_top: list[MarketSkillRank]
    international_top: list[MarketSkillRank]
    skill_gaps: list[SkillGap]


class WorkModeDistribution(BaseModel):
    onsite: int = 0
    remote: int = 0
    hybrid: int = 0
    unknown: int = 0


class EducationDistribution(BaseModel):
    bachelor: int = 0
    master: int = 0
    phd: int = 0
    any_or_unspecified: int = 0


class MarketSummary(BaseModel):
    market: str
    total_jobs: int
    avg_salary: int | None
    median_salary: int | None
    work_mode: WorkModeDistribution
    education: EducationDistribution
    experience_distribution: list[ExperienceSalary]


class MarketOverview(BaseModel):
    domestic: MarketSummary
    international: MarketSummary


# --- Co-occurrence ---


class SkillPair(BaseModel):
    skill_a: str
    skill_b: str
    skill_a_name: str
    skill_b_name: str
    cooccurrence_count: int
    jaccard_index: float


class CooccurrenceResult(BaseModel):
    top_pairs: list[SkillPair]
    total_jobs_analyzed: int


# --- Industry ---


class IndustrySkillCount(BaseModel):
    skill_id: str
    count: int


class IndustrySummary(BaseModel):
    industry: str
    job_count: int
    domestic_count: int
    international_count: int
    avg_salary: int | None
    top_skills: list[IndustrySkillCount]


class IndustrySalary(BaseModel):
    industry: str
    job_count: int
    avg_salary: int
