# Pydantic schemas for Job API requests and responses.
from __future__ import annotations

import datetime
import uuid

from pydantic import BaseModel, Field


# --- Request schemas ---


class JobImportRequest(BaseModel):
    """Single JD submitted via manual import or browser extension."""

    platform_id: str = Field(..., examples=["boss_zhipin"])
    platform_job_id: str = Field(..., examples=["job_abc123"])
    source_url: str | None = None
    raw_content: str = Field(..., min_length=10)
    language: str = Field("zh", pattern=r"^(zh|en|mixed)$")


class JobImportBatchRequest(BaseModel):
    """Batch import multiple JDs at once."""

    jobs: list[JobImportRequest] = Field(..., min_length=1, max_length=100)


class CollectRequest(BaseModel):
    """Request to trigger collection from a platform."""

    platform_id: str = Field(..., examples=["linkedin"])
    keyword: str = Field(..., examples=["AI Agent Engineer"])
    max_pages: int = Field(5, ge=1, le=20)
    auto_parse: bool = Field(True)


# --- Response schemas ---


class JobBrief(BaseModel):
    """Lightweight job listing for list views."""

    id: uuid.UUID
    platform_id: str
    title: str | None
    company_name: str | None
    location: str | None
    market: str | None
    industry: str | None
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    parse_status: str
    collected_at: datetime.datetime

    model_config = {"from_attributes": True}


class JobDetail(BaseModel):
    """Full job detail including parsed fields."""

    id: uuid.UUID
    platform_id: str
    platform_job_id: str
    source_url: str | None
    raw_content: str
    language: str

    title: str | None
    company_name: str | None
    company_size: str | None
    location: str | None
    market: str | None
    industry: str | None
    work_mode: str | None

    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None

    experience_min: int | None
    experience_max: int | None
    education: str | None

    required_skills: list[str] | None
    preferred_skills: list[str] | None
    responsibilities: list[str] | None

    collected_at: datetime.datetime
    parsed_at: datetime.datetime | None
    parse_status: str

    model_config = {"from_attributes": True}


class JobImportResponse(BaseModel):
    """Response after importing jobs."""

    imported: int
    skipped: int  # duplicates
    job_ids: list[uuid.UUID]


class CollectResponse(BaseModel):
    """Response after collecting and optionally parsing jobs."""

    collected: int
    imported: int
    skipped: int
    parsed: int
    failed: int
    job_ids: list[uuid.UUID]


class JobListResponse(BaseModel):
    """Paginated job listing."""

    total: int
    page: int
    page_size: int
    items: list[JobBrief]


# --- Parsed JD structure (output from LLM) ---


class ParsedJD(BaseModel):
    """Structured output from LLM JD parsing."""

    title: str | None = None
    company_name: str | None = None
    company_size: str | None = None
    location: str | None = None
    market: str | None = None
    industry: str | None = None
    work_mode: str | None = None
    salary_min_rmb: int | None = None
    salary_max_rmb: int | None = None
    salary_currency_original: str | None = None
    experience_min_years: int | None = None
    experience_max_years: int | None = None
    education: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    language: str = "zh"

    # --- Issue #11: graduate / campus signals ---
    experience_requirement: str | None = None  # fresh | 0-1y | 1-3y | 3-5y | 5y+
    internship_friendly: bool | None = None
    is_campus: bool | None = None

    # --- Issue #10: AI native vs AI augmented ---
    role_type: str | None = None  # ai_native | ai_augmented_traditional
    base_profession: str | None = None


class QualityLabels(BaseModel):
    """Slimmed-down output used by backfill_quality_labels.py.

    Only the 5 new fields — keeps prompts cheap and avoids re-deriving
    salary / skills / etc. for already-parsed jobs.
    """

    experience_requirement: str | None = None
    internship_friendly: bool | None = None
    is_campus: bool | None = None
    role_type: str | None = None
    base_profession: str | None = None
