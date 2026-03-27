from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.analysis import (
    CooccurrenceResult,
    CrossMarketSkills,
    ExperienceSalary,
    MarketOverview,
    PlatformSalary,
    SalaryDistribution,
    SkillGap,
    SkillSalary,
)
from app.services.cross_market import market_overview, skill_gap_analysis, top_skills_by_market
from app.services.market_analyzer import (
    salary_by_experience,
    salary_by_platform,
    salary_by_skill,
    salary_distribution,
)
from app.services.skill_taxonomy import skill_cooccurrence

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/salary/distribution", response_model=SalaryDistribution)
async def salary_distribution_endpoint(
    market: str | None = None,
    platform_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await salary_distribution(db, market, platform_id)


@router.get("/salary/by-skill", response_model=list[SkillSalary])
async def salary_by_skill_endpoint(
    top_n: int = Query(20, ge=5, le=50),
    market: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await salary_by_skill(db, top_n, market)


@router.get("/salary/by-experience", response_model=list[ExperienceSalary])
async def salary_by_experience_endpoint(
    market: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await salary_by_experience(db, market)


@router.get("/salary/by-platform", response_model=list[PlatformSalary])
async def salary_by_platform_endpoint(db: AsyncSession = Depends(get_db)):
    return await salary_by_platform(db)


@router.get("/cross-market/overview", response_model=MarketOverview)
async def cross_market_overview(db: AsyncSession = Depends(get_db)):
    return await market_overview(db)


@router.get("/cross-market/skills", response_model=CrossMarketSkills)
async def cross_market_skills(
    top_n: int = Query(20, ge=5, le=50),
    db: AsyncSession = Depends(get_db),
):
    return await top_skills_by_market(db, top_n)


@router.get("/cross-market/skill-gaps", response_model=list[SkillGap])
async def skill_gaps(
    min_count: int = Query(3, ge=1),
    db: AsyncSession = Depends(get_db),
):
    return await skill_gap_analysis(db, min_count)


@router.get("/cooccurrence", response_model=CooccurrenceResult)
async def cooccurrence(
    top_n: int = Query(30, ge=5, le=50),
    min_cooccurrence: int = Query(3, ge=1),
    market: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await skill_cooccurrence(db, top_n, min_cooccurrence, market)
