from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.skill import Skill
from app.schemas.analysis import NormalizationResult, SkillResponse, UnmatchedTerm
from app.services.skill_extractor import get_unmatched_terms, normalize_all_jobs

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("", response_model=list[SkillResponse])
async def list_skills(
    category: str | None = None,
    sort_by: str = Query("total_count", pattern=r"^(total_count|canonical_name)$"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Skill)
    if category:
        query = query.where(Skill.category == category)

    if sort_by == "total_count":
        query = query.order_by(Skill.total_count.desc())
    else:
        query = query.order_by(Skill.canonical_name)

    result = await db.execute(query)
    return [SkillResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/normalize", response_model=NormalizationResult)
async def trigger_normalization(db: AsyncSession = Depends(get_db)):
    result = await normalize_all_jobs(db)
    return NormalizationResult(**result)


@router.get("/unmatched", response_model=list[UnmatchedTerm])
async def list_unmatched(db: AsyncSession = Depends(get_db)):
    terms = await get_unmatched_terms(db)
    return [UnmatchedTerm(**t) for t in terms]
