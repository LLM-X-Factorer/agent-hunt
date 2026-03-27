from __future__ import annotations

from collections import defaultdict
from statistics import median

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.skill import Skill
from app.services.skill_extractor import extractor

SALARY_BUCKETS = [
    ("<10k", 0, 10000),
    ("10-20k", 10000, 20000),
    ("20-30k", 20000, 30000),
    ("30-50k", 30000, 50000),
    ("50-80k", 50000, 80000),
    ("80k+", 80000, float("inf")),
]

EXPERIENCE_BRACKETS = [
    ("0-1", 0, 1),
    ("1-3", 1, 3),
    ("3-5", 3, 5),
    ("5-10", 5, 10),
    ("10+", 10, 100),
]


async def _fetch_parsed_jobs(db: AsyncSession, market=None, platform_id=None, industry=None):
    query = select(Job).where(Job.parse_status == "parsed")
    if market:
        query = query.where(Job.market == market)
    if platform_id:
        query = query.where(Job.platform_id == platform_id)
    if industry:
        query = query.where(Job.industry == industry)
    result = await db.execute(query)
    return result.scalars().all()


async def salary_distribution(
    db: AsyncSession, market: str | None = None, platform_id: str | None = None,
    industry: str | None = None,
) -> dict:
    jobs = await _fetch_parsed_jobs(db, market, platform_id, industry)
    salaries = [
        (j.salary_min + j.salary_max) // 2
        for j in jobs
        if j.salary_min is not None and j.salary_max is not None
    ]

    if not salaries:
        return {"market": market, "total_jobs_with_salary": 0, "buckets": []}

    total = len(salaries)
    buckets = []
    for label, lo, hi in SALARY_BUCKETS:
        count = sum(1 for s in salaries if lo <= s < hi)
        buckets.append({
            "range_label": label,
            "count": count,
            "percentage": round(count / total * 100, 1),
        })

    return {"market": market, "total_jobs_with_salary": total, "buckets": buckets}


async def salary_by_skill(
    db: AsyncSession, top_n: int = 20, market: str | None = None,
    industry: str | None = None,
) -> list[dict]:
    jobs = await _fetch_parsed_jobs(db, market, industry=industry)

    skill_salaries: dict[str, list[int]] = defaultdict(list)
    for job in jobs:
        if job.salary_min is None or job.salary_max is None:
            continue
        avg_sal = (job.salary_min + job.salary_max) // 2
        all_skills = (job.required_skills or []) + (job.preferred_skills or [])
        for raw in all_skills:
            sid = extractor.normalize(raw)
            if sid:
                skill_salaries[sid].append(avg_sal)

    # Get canonical names
    result = await db.execute(select(Skill))
    skill_map = {s.id: s.canonical_name for s in result.scalars().all()}

    ranked = []
    for sid, sals in skill_salaries.items():
        if len(sals) < 2:
            continue
        ranked.append({
            "skill_id": sid,
            "canonical_name": skill_map.get(sid, sid),
            "job_count": len(sals),
            "avg_salary": int(sum(sals) / len(sals)),
            "min_salary": min(sals),
            "max_salary": max(sals),
        })

    ranked.sort(key=lambda x: x["avg_salary"], reverse=True)
    return ranked[:top_n]


async def salary_by_experience(
    db: AsyncSession, market: str | None = None
) -> list[dict]:
    jobs = await _fetch_parsed_jobs(db, market)

    brackets: dict[str, list[int]] = defaultdict(list)
    for job in jobs:
        if job.salary_min is None or job.salary_max is None:
            continue
        if job.experience_min is None:
            continue

        avg_sal = (job.salary_min + job.salary_max) // 2
        exp = job.experience_min
        for label, lo, hi in EXPERIENCE_BRACKETS:
            if lo <= exp <= hi:
                brackets[label].append(avg_sal)
                break

    result = []
    for label, _, _ in EXPERIENCE_BRACKETS:
        sals = brackets.get(label, [])
        if sals:
            result.append({
                "bracket": label,
                "job_count": len(sals),
                "avg_salary": int(sum(sals) / len(sals)),
            })

    return result


async def salary_by_platform(db: AsyncSession) -> list[dict]:
    jobs = await _fetch_parsed_jobs(db)

    platform_sals: dict[str, list[int]] = defaultdict(list)
    for job in jobs:
        if job.salary_min is None or job.salary_max is None:
            continue
        avg_sal = (job.salary_min + job.salary_max) // 2
        platform_sals[job.platform_id].append(avg_sal)

    result = []
    for pid, sals in platform_sals.items():
        result.append({
            "platform_id": pid,
            "job_count": len(sals),
            "avg_salary": int(sum(sals) / len(sals)),
        })

    result.sort(key=lambda x: x["avg_salary"], reverse=True)
    return result


async def salary_by_industry(db: AsyncSession) -> list[dict]:
    jobs = await _fetch_parsed_jobs(db)

    industry_sals: dict[str, list[int]] = defaultdict(list)
    for job in jobs:
        if job.salary_min is None or job.salary_max is None or not job.industry:
            continue
        avg_sal = (job.salary_min + job.salary_max) // 2
        industry_sals[job.industry].append(avg_sal)

    result = []
    for ind, sals in industry_sals.items():
        result.append({
            "industry": ind,
            "job_count": len(sals),
            "avg_salary": int(sum(sals) / len(sals)),
        })

    result.sort(key=lambda x: x["job_count"], reverse=True)
    return result
