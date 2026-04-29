#!/usr/bin/env python3
"""Refresh static-mode JSON snapshots that mirror the FastAPI analysis endpoints.

Frontend ``src/lib/api.ts`` falls back to ``/data/<file>.json`` when no live
API URL is configured. Those files used to be curl'd by hand from a running
uvicorn instance — and rotted (cross-market-overview was still showing v0.6
numbers months later). This script calls the same service functions
directly, no HTTP round-trip needed.

Outputs:
  - skills.json
  - cross-market-overview.json
  - cross-market-skills.json
  - skill-gaps.json
  - salary-distribution.json
  - salary-by-skill.json
  - salary-by-experience.json
  - salary-by-platform.json
  - cooccurrence.json
  - industry-overview.json
  - industry-salary.json
  - job-count.json
  - full-stats.json (lightweight totals for nav bar etc.)

Usage:
    cd backend && .venv/bin/python scripts/export_api_snapshots.py
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select

from app.database import async_session
from app.models.job import Job
from app.models.skill import Skill
from app.services.cross_market import (
    industry_overview,
    market_overview,
    skill_gap_analysis,
    top_skills_by_market,
)
from app.services.market_analyzer import (
    salary_by_experience,
    salary_by_industry,
    salary_by_platform,
    salary_by_skill,
    salary_distribution,
)
from app.services.skill_taxonomy import skill_cooccurrence

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "data"


def write(filename: str, payload) -> None:
    path = OUTPUT_DIR / filename
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("wrote %s", filename)


async def export_skills(db) -> None:
    skills = (
        await db.execute(select(Skill).order_by(Skill.total_count.desc()))
    ).scalars().all()
    write("skills.json", [
        {
            "id": s.id,
            "canonical_name": s.canonical_name,
            "category": s.category,
            "subcategory": s.subcategory,
            "domestic_count": s.domestic_count,
            "international_count": s.international_count,
            "total_count": s.total_count,
            "avg_salary_with": s.avg_salary_with,
        }
        for s in skills
    ])


async def export_job_count(db) -> None:
    total = (await db.execute(select(func.count()).select_from(Job))).scalar()
    write("job-count.json", {"total": total, "page": 1, "page_size": 1})


async def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    async with async_session() as db:
        await export_skills(db)
        await export_job_count(db)

        write("cross-market-overview.json", await market_overview(db))
        write("cross-market-skills.json", await top_skills_by_market(db, top_n=20))
        write("skill-gaps.json", await skill_gap_analysis(db))

        write("salary-distribution.json", await salary_distribution(db))
        write("salary-by-skill.json", await salary_by_skill(db, top_n=15))
        write("salary-by-experience.json", await salary_by_experience(db))
        write("salary-by-platform.json", await salary_by_platform(db))

        write("cooccurrence.json", await skill_cooccurrence(db, top_n=10))
        write("industry-overview.json", await industry_overview(db))
        write("industry-salary.json", await salary_by_industry(db))

        # Lightweight summary used by nav / footer.
        total_jobs = (await db.execute(select(func.count()).select_from(Job))).scalar()
        parsed_jobs = (await db.execute(
            select(func.count()).select_from(Job).where(Job.parse_status == "parsed")
        )).scalar()
        skills_total = (await db.execute(select(func.count()).select_from(Skill))).scalar()
        write("full-stats.json", {
            "total_jobs": total_jobs,
            "parsed_jobs": parsed_jobs,
            "total_skills": skills_total,
        })

    logger.info("api-snapshot export complete (%s)", OUTPUT_DIR)


if __name__ == "__main__":
    asyncio.run(main())
