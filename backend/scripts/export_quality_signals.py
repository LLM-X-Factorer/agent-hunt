#!/usr/bin/env python3
"""Export jobs-quality-signals.json from #16 quality-signal fields.

Computes per-company / per-industry / per-platform metrics:
  - repost_ratio: share of jobs with seen_count >= 3 (招不到 / 流失大 信号)
  - avg_close_days: mean days from first_seen_at to closed_at
  - reposting_top: top companies by repost_ratio (with min sample size)

Usage:
    cd backend && .venv/bin/python scripts/export_quality_signals.py
"""
import asyncio
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.job import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "jobs-quality-signals.json"
)

REPOST_THRESHOLD = 3  # seen_count >= this counts as a "reposted" job
MIN_SAMPLE = 5        # don't compute ratios on companies with fewer than this many jobs


def bucket_stats(jobs: list[Job]) -> dict:
    total = len(jobs)
    reposted = sum(1 for j in jobs if (j.seen_count or 1) >= REPOST_THRESHOLD)
    closed_jobs = [j for j in jobs if j.closed_at and j.first_seen_at]
    close_days = [
        (j.closed_at - j.first_seen_at).days
        for j in closed_jobs
        if (j.closed_at - j.first_seen_at).days >= 0
    ]
    return {
        "total": total,
        "reposted": reposted,
        "repost_ratio": round(reposted / total, 3) if total else 0.0,
        "closed": len(closed_jobs),
        "avg_close_days": round(mean(close_days), 1) if close_days else None,
    }


async def main():
    async with async_session() as db:
        result = await db.execute(select(Job))
        all_jobs = result.scalars().all()

    logger.info("loaded %d jobs", len(all_jobs))

    by_company: dict[str, list[Job]] = defaultdict(list)
    by_industry: dict[str, list[Job]] = defaultdict(list)
    by_platform: dict[str, list[Job]] = defaultdict(list)
    by_market: dict[str, list[Job]] = defaultdict(list)

    for j in all_jobs:
        if j.company_name:
            by_company[j.company_name].append(j)
        if j.industry:
            by_industry[j.industry].append(j)
        if j.platform_id:
            by_platform[j.platform_id].append(j)
        if j.market:
            by_market[j.market].append(j)

    company_rows = []
    for name, jobs in by_company.items():
        if len(jobs) < MIN_SAMPLE:
            continue
        s = bucket_stats(jobs)
        s["company"] = name
        company_rows.append(s)
    company_rows.sort(key=lambda r: -r["repost_ratio"])

    industry_rows = [
        {**bucket_stats(jobs), "industry": ind} for ind, jobs in by_industry.items()
    ]
    industry_rows.sort(key=lambda r: -r["repost_ratio"])

    platform_rows = [
        {**bucket_stats(jobs), "platform": p} for p, jobs in by_platform.items()
    ]
    platform_rows.sort(key=lambda r: -r["repost_ratio"])

    market_rows = [
        {**bucket_stats(jobs), "market": m} for m, jobs in by_market.items()
    ]

    overall = bucket_stats(all_jobs)

    output = {
        "overall": overall,
        "by_market": market_rows,
        "by_platform": platform_rows,
        "by_industry": industry_rows,
        "top_reposting_companies": company_rows[:50],
        "config": {
            "repost_threshold": REPOST_THRESHOLD,
            "min_sample": MIN_SAMPLE,
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
