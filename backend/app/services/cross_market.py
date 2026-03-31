from __future__ import annotations

from collections import defaultdict
from statistics import median

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.skill import Skill
from app.services.market_analyzer import EXPERIENCE_BRACKETS


async def market_overview(db: AsyncSession) -> dict:
    result = await db.execute(
        select(Job).where(Job.parse_status == "parsed")
    )
    jobs = result.scalars().all()

    domestic = [j for j in jobs if j.market == "domestic"]
    international = [j for j in jobs if j.market == "international"]

    return {
        "domestic": _summarize_market("domestic", domestic),
        "international": _summarize_market("international", international),
    }


def _summarize_market(market: str, jobs: list) -> dict:
    salaries = [
        (j.salary_min + j.salary_max) // 2
        for j in jobs
        if j.salary_min is not None and j.salary_max is not None
    ]

    work_mode = {"onsite": 0, "remote": 0, "hybrid": 0, "unknown": 0}
    for j in jobs:
        wm = j.work_mode or "unknown"
        work_mode[wm] = work_mode.get(wm, 0) + 1

    education = {"bachelor": 0, "master": 0, "phd": 0, "any_or_unspecified": 0}
    for j in jobs:
        edu = j.education
        if edu in ("bachelor", "master", "phd"):
            education[edu] += 1
        else:
            education["any_or_unspecified"] += 1

    exp_dist = defaultdict(list)
    for j in jobs:
        if j.salary_min is None or j.salary_max is None or j.experience_min is None:
            continue
        avg_sal = (j.salary_min + j.salary_max) // 2
        for label, lo, hi in EXPERIENCE_BRACKETS:
            if lo <= j.experience_min <= hi:
                exp_dist[label].append(avg_sal)
                break

    experience_distribution = []
    for label, _, _ in EXPERIENCE_BRACKETS:
        sals = exp_dist.get(label, [])
        if sals:
            experience_distribution.append({
                "bracket": label,
                "job_count": len(sals),
                "avg_salary": int(sum(sals) / len(sals)),
            })

    return {
        "market": market,
        "total_jobs": len(jobs),
        "avg_salary": int(sum(salaries) / len(salaries)) if salaries else None,
        "median_salary": int(median(salaries)) if salaries else None,
        "work_mode": work_mode,
        "education": education,
        "experience_distribution": experience_distribution,
    }


async def top_skills_by_market(db: AsyncSession, top_n: int = 20) -> dict:
    result = await db.execute(
        select(Skill).where(Skill.total_count > 0).order_by(Skill.total_count.desc())
    )
    skills = result.scalars().all()

    # Count total jobs per market for percentage calculation
    job_result = await db.execute(
        select(Job).where(Job.parse_status == "parsed")
    )
    all_jobs = job_result.scalars().all()
    domestic_total = sum(1 for j in all_jobs if j.market == "domestic")
    international_total = sum(1 for j in all_jobs if j.market == "international")

    domestic_top = sorted(skills, key=lambda s: s.domestic_count, reverse=True)[:top_n]
    international_top = sorted(
        skills, key=lambda s: s.international_count, reverse=True
    )[:top_n]

    def _rank(skill, count, total):
        return {
            "skill_id": skill.id,
            "canonical_name": skill.canonical_name,
            "count": count,
            "percentage": round(count / total * 100, 1) if total else 0,
        }

    # Skill gaps
    gaps = []
    for s in skills:
        if s.total_count < 3:
            continue
        d_pct = (
            round(s.domestic_count / domestic_total * 100, 1) if domestic_total else 0
        )
        i_pct = (
            round(s.international_count / international_total * 100, 1)
            if international_total
            else 0
        )
        gap = abs(d_pct - i_pct)
        gaps.append({
            "skill_id": s.id,
            "canonical_name": s.canonical_name,
            "domestic_count": s.domestic_count,
            "international_count": s.international_count,
            "domestic_pct": d_pct,
            "international_pct": i_pct,
            "gap": round(gap, 1),
            "dominant_market": "domestic" if d_pct > i_pct else "international",
        })

    gaps.sort(key=lambda x: x["gap"], reverse=True)

    return {
        "domestic_top": [
            _rank(s, s.domestic_count, domestic_total) for s in domestic_top
        ],
        "international_top": [
            _rank(s, s.international_count, international_total)
            for s in international_top
        ],
        "skill_gaps": gaps[:top_n],
    }


async def skill_gap_analysis(
    db: AsyncSession, min_count: int = 3
) -> list[dict]:
    data = await top_skills_by_market(db)
    return [g for g in data["skill_gaps"] if g["domestic_count"] + g["international_count"] >= min_count]


async def industry_overview(
    db: AsyncSession, market: str | None = None,
) -> list[dict]:
    query = select(Job).where(Job.parse_status == "parsed", Job.industry.isnot(None))
    if market:
        query = query.where(Job.market == market)
    result = await db.execute(query)
    jobs = result.scalars().all()

    by_industry: dict[str, list] = defaultdict(list)
    for j in jobs:
        by_industry[j.industry].append(j)

    summaries = []
    for ind, ind_jobs in by_industry.items():
        salaries = [
            (j.salary_min + j.salary_max) // 2
            for j in ind_jobs
            if j.salary_min and j.salary_max
        ]
        domestic = sum(1 for j in ind_jobs if j.market == "domestic")
        international = len(ind_jobs) - domestic

        # Top skills in this industry
        from app.services.skill_extractor import extractor
        skill_counts: dict[str, int] = defaultdict(int)
        for j in ind_jobs:
            for raw in (j.required_skills or []) + (j.preferred_skills or []):
                sid = extractor.normalize(raw)
                if sid:
                    skill_counts[sid] += 1
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        summaries.append({
            "industry": ind,
            "job_count": len(ind_jobs),
            "domestic_count": domestic,
            "international_count": international,
            "avg_salary": int(sum(salaries) / len(salaries)) if salaries else None,
            "top_skills": [{"skill_id": s, "count": c} for s, c in top_skills],
        })

    summaries.sort(key=lambda x: x["job_count"], reverse=True)
    return summaries
