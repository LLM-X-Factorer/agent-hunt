#!/usr/bin/env python3
"""Export industry × role 2D slice (#9).

Outputs ``frontend/public/data/roles-by-industry.json`` so aijobfit can
answer "教培行业里数据分析师有多少空缺 / 薪资中位数多少" without
joining JSON files itself.

Cells with sample size < 5 are flagged ``lowSample: true`` per the issue
acceptance criteria.

Usage:
    cd backend && .venv/bin/python scripts/export_roles_by_industry.py
"""
import asyncio
import json
import logging
import sys
from collections import Counter, defaultdict
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

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "data"
LOW_SAMPLE_THRESHOLD = 5
RULES_BY_MARKET = {"domestic": DOMESTIC_ROLES, "international": INTERNATIONAL_ROLES}


def cell_stats(jobs: list[Job]) -> dict:
    salaries = [
        (j.salary_min + j.salary_max) // 2
        for j in jobs
        if j.salary_min and j.salary_max
    ]
    regions = Counter(j.location for j in jobs if j.location)
    out: dict = {
        "vacancyCount": len(jobs),
        "salaryMedian": int(median(salaries)) if salaries else None,
        "salarySampleSize": len(salaries),
        "topRegions": [r for r, _ in regions.most_common(5)],
    }
    if len(jobs) < LOW_SAMPLE_THRESHOLD:
        out["lowSample"] = True
    return out


async def main():
    async with async_session() as db:
        jobs = (await db.execute(
            select(Job).where(Job.parse_status == "parsed", Job.title.isnot(None))
        )).scalars().all()
    logger.info("loaded %d parsed jobs", len(jobs))

    output: dict[str, dict[str, dict[str, dict]]] = {"domestic": {}, "international": {}}
    role_names_by_market: dict[str, dict[str, str]] = {}

    for market, rules in RULES_BY_MARKET.items():
        market_jobs = [j for j in jobs if j.market == market]
        role_names = {rid: name for rid, name, _ in rules}
        role_names_by_market[market] = role_names

        # Bucket by (industry, role_id).
        cells: dict[tuple[str, str], list[Job]] = defaultdict(list)
        for j in market_jobs:
            if not j.industry:
                continue
            rid = classify_job(j.title or "", rules)
            if rid in ("_noise", "other"):
                continue
            cells[(j.industry, rid)].append(j)

        for (industry, rid), bucket in cells.items():
            output[market].setdefault(industry, {})[rid] = {
                "roleName": role_names.get(rid, rid),
                **cell_stats(bucket),
            }

        logger.info(
            "%s — %d industries with role data",
            market, len(output[market]),
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "roles-by-industry.json"
    path.write_text(
        json.dumps(
            {
                "data": output,
                "config": {
                    "lowSampleThreshold": LOW_SAMPLE_THRESHOLD,
                },
                "roleNames": role_names_by_market,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("wrote %s", path.relative_to(OUTPUT_DIR.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
