#!/usr/bin/env python3
"""Export monthly snapshot tables to static JSON for the frontend.

Issue #13: emits ``frontend/public/data/trends/`` so aijobfit can render
"is X declining" type charts. Run after ``snapshot_monthly.py``.

Outputs:
  trends/skills-monthly.json     — { domestic: [{skill_id, series:[{month,job_count,salary_median}]}], international: [...] }
  trends/roles-monthly.json
  trends/industries-monthly.json

Usage:
    cd backend && .venv/bin/python scripts/export_trends.py
"""
import asyncio
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.snapshot import (
    IndustryMonthlySnapshot,
    RoleMonthlySnapshot,
    SkillMonthlySnapshot,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "data" / "trends"
)


def write_json(name: str, data) -> None:
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("wrote %s", path.relative_to(OUTPUT_DIR.parent.parent))


async def export_skills():
    async with async_session() as db:
        rows = (await db.execute(select(SkillMonthlySnapshot))).scalars().all()

    by_market: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_market[r.market][r.skill_id].append({
            "month": r.month.isoformat(),
            "job_count": r.job_count,
            "salary_median": r.salary_median,
            "salary_avg": r.salary_avg,
        })

    out: dict[str, list[dict]] = {}
    for market, skill_map in by_market.items():
        series = []
        for sid, points in skill_map.items():
            points.sort(key=lambda p: p["month"])
            series.append({"skill_id": sid, "series": points})
        series.sort(key=lambda s: -sum(p["job_count"] for p in s["series"]))
        out[market] = series
    write_json("skills-monthly.json", out)


async def export_roles():
    async with async_session() as db:
        rows = (await db.execute(select(RoleMonthlySnapshot))).scalars().all()

    by_market: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_market[r.market][r.role_id].append({
            "month": r.month.isoformat(),
            "job_count": r.job_count,
            "salary_median": r.salary_median,
            "salary_avg": r.salary_avg,
            "top_skills": r.top_skills or [],
        })

    out: dict[str, list[dict]] = {}
    for market, role_map in by_market.items():
        series = []
        for rid, points in role_map.items():
            points.sort(key=lambda p: p["month"])
            series.append({"role_id": rid, "series": points})
        series.sort(key=lambda s: -sum(p["job_count"] for p in s["series"]))
        out[market] = series
    write_json("roles-monthly.json", out)


async def export_industries():
    async with async_session() as db:
        rows = (await db.execute(select(IndustryMonthlySnapshot))).scalars().all()

    by_market: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_market[r.market][r.industry].append({
            "month": r.month.isoformat(),
            "job_count": r.job_count,
            "salary_median": r.salary_median,
            "salary_avg": r.salary_avg,
        })

    out: dict[str, list[dict]] = {}
    for market, ind_map in by_market.items():
        series = []
        for ind, points in ind_map.items():
            points.sort(key=lambda p: p["month"])
            series.append({"industry": ind, "series": points})
        series.sort(key=lambda s: -sum(p["job_count"] for p in s["series"]))
        out[market] = series
    write_json("industries-monthly.json", out)


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    await export_skills()
    await export_roles()
    await export_industries()


if __name__ == "__main__":
    asyncio.run(main())
