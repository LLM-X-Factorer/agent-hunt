#!/usr/bin/env python3
"""Export graduate-friendliness scores per role (#11).

Combines is_campus / experience_requirement=fresh / internship_friendly
into a single 0-100 score per role, plus a fresh-only salary median
(社招 medians don't translate for an applying student).

Usage:
    cd backend && .venv/bin/python scripts/export_graduate_friendly.py
"""
import asyncio
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.job import Job
from scripts.analyze_roles import (
    DOMESTIC_ROLES,
    INTERNATIONAL_ROLES,
    classify_job,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "roles-graduate-friendly.json"
)
RULES_BY_MARKET = {"domestic": DOMESTIC_ROLES, "international": INTERNATIONAL_ROLES}


def score_role(jobs: list[Job]) -> dict:
    """Composite friendliness score in [0, 100] + the building blocks."""
    total = len(jobs)
    if not total:
        return {"graduateFriendlyScore": 0}

    campus = sum(1 for j in jobs if j.is_campus)
    intern = sum(1 for j in jobs if j.internship_friendly)
    fresh = sum(1 for j in jobs if j.experience_requirement == "fresh")
    fresh_or_under_1y = sum(
        1 for j in jobs if j.experience_requirement in ("fresh", "0-1y")
    )

    # Weighted: campus is the strongest positive signal, fresh second,
    # internship-friendly third. All shares scale to 100 then averaged.
    campus_share = campus / total
    fresh_share = fresh / total
    fresh_or_junior_share = fresh_or_under_1y / total
    intern_share = intern / total

    score = (
        campus_share * 50
        + fresh_share * 30
        + fresh_or_junior_share * 10
        + intern_share * 10
    )
    score = round(min(100, score * 100 / 100), 1)

    fresh_jobs = [j for j in jobs if j.experience_requirement == "fresh"]
    fresh_salaries = [
        (j.salary_min + j.salary_max) // 2
        for j in fresh_jobs
        if j.salary_min and j.salary_max
    ]
    social_jobs = [j for j in jobs if j.experience_requirement not in ("fresh", None)]
    social_salaries = [
        (j.salary_min + j.salary_max) // 2
        for j in social_jobs
        if j.salary_min and j.salary_max
    ]

    return {
        "graduateFriendlyScore": score,
        "totalJobs": total,
        "campusJobCount": campus,
        "internshipJobCount": intern,
        "freshJobCount": fresh,
        "freshSalaryMedian": int(median(fresh_salaries)) if fresh_salaries else None,
        "socialSalaryMedian": int(median(social_salaries)) if social_salaries else None,
    }


async def main():
    async with async_session() as db:
        jobs = (await db.execute(
            select(Job).where(Job.parse_status == "parsed", Job.title.isnot(None))
        )).scalars().all()
    logger.info("loaded %d parsed jobs", len(jobs))

    output: dict[str, list[dict]] = {}
    for market, rules in RULES_BY_MARKET.items():
        market_jobs = [j for j in jobs if j.market == market]
        role_names = {rid: name for rid, name, _ in rules}

        groups: dict[str, list[Job]] = defaultdict(list)
        for j in market_jobs:
            rid = classify_job(j.title or "", rules)
            if rid in ("_noise", "other"):
                continue
            groups[rid].append(j)

        rows = []
        for rid, gjobs in groups.items():
            if len(gjobs) < 3:
                continue
            stats = score_role(gjobs)
            stats["roleId"] = rid
            stats["roleName"] = role_names.get(rid, rid)
            rows.append(stats)
        rows.sort(key=lambda r: -r["graduateFriendlyScore"])
        output[market] = rows
        logger.info("%s — %d roles scored", market, len(rows))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
