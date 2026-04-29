#!/usr/bin/env python3
"""Export domestic AI-augmented industry × salary breakdown (P0 论断 2).

Powers the narrative-handbook "反直觉薪资" page: traditional industries
(医疗/制造/金融) pay 30k+ for AI-augmented roles vs internet 25k.

Output schema:
    {
      "by_industry": [
        {"industry": "...", "job_count": N, "salary_p25/p50/p75": int, "sample_size": M},
        ...
      ],
      "comparison": {
        "traditional_median": ..., "internet_median": ..., "delta_pct": ...
      },
      "total_jobs": N
    }

Usage:
    cd backend && .venv/bin/python scripts/export_industry_salary.py
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "industry-augmented-salary.json"
)

# 高薪传统行业对比组：narrative 论断 2 用，median ~30k 段。
PREMIUM_TRADITIONAL = {"healthcare", "manufacturing", "finance"}
# 所有传统行业（非互联网），用于完整对比表
TRADITIONAL_INDUSTRIES = {
    "manufacturing", "automotive", "healthcare", "media",
    "finance", "education", "consulting", "retail",
    "energy", "telecom",
}


def percentiles(values: list[int]) -> dict | None:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    return {
        "p25": s[n // 4],
        "p50": int(median(s)),
        "p75": s[(n * 3) // 4],
        "min": s[0],
        "max": s[-1],
        "sample_size": n,
    }


async def main():
    async with async_session() as db:
        jobs = (await db.execute(
            select(Job).where(
                Job.parse_status == "parsed",
                Job.market == "domestic",
                Job.role_type == "ai_augmented_traditional",
                Job.industry.isnot(None),
            )
        )).scalars().all()
    logger.info("loaded %d domestic ai_augmented_traditional jobs", len(jobs))

    by_industry: dict[str, list[int]] = defaultdict(list)
    counts: dict[str, int] = defaultdict(int)
    for j in jobs:
        counts[j.industry] += 1
        if j.salary_min and j.salary_max:
            by_industry[j.industry].append((j.salary_min + j.salary_max) // 2)

    rows = []
    for industry, salaries in sorted(by_industry.items(), key=lambda kv: -(median(kv[1]) if kv[1] else 0)):
        if len(salaries) < 5:
            continue
        p = percentiles(salaries)
        rows.append({
            "industry": industry,
            "job_count": counts[industry],
            "salary_sample_size": p["sample_size"],
            "p25": p["p25"],
            "p50": p["p50"],
            "p75": p["p75"],
        })

    premium_salaries = [
        s for ind, salaries in by_industry.items() if ind in PREMIUM_TRADITIONAL
        for s in salaries
    ]
    internet_salaries = by_industry.get("internet", [])

    comparison = {
        "premium_traditional_industries": sorted(PREMIUM_TRADITIONAL),
        "premium_traditional_median": int(median(premium_salaries)) if premium_salaries else None,
        "premium_traditional_sample_size": len(premium_salaries),
        "internet_median": int(median(internet_salaries)) if internet_salaries else None,
        "internet_sample_size": len(internet_salaries),
    }
    if comparison["premium_traditional_median"] and comparison["internet_median"]:
        comparison["delta_pct"] = round(
            (comparison["premium_traditional_median"] - comparison["internet_median"])
            / comparison["internet_median"] * 100, 1
        )

    output = {
        "by_industry": rows,
        "comparison": comparison,
        "total_jobs": len(jobs),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
