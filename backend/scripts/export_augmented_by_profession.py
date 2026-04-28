#!/usr/bin/env python3
"""Export AI-augmented traditional roles grouped by base profession (#10).

Reads jobs where role_type = 'ai_augmented_traditional' + base_profession,
emits a per-profession listing so aijobfit can pull a "电气 + AI" roster
for users with electrical-engineering background instead of pushing them
toward AI sales.

Usage:
    cd backend && .venv/bin/python scripts/export_augmented_by_profession.py
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
from app.services.skill_extractor import extractor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "roles-augmented-by-profession.json"
)


def profession_stats(jobs: list[Job]) -> dict:
    salaries = [
        (j.salary_min + j.salary_max) // 2
        for j in jobs
        if j.salary_min and j.salary_max
    ]
    augment_skills: Counter = Counter()
    for j in jobs:
        for raw in (j.required_skills or []) + (j.preferred_skills or []):
            sid = extractor.normalize(raw)
            if sid:
                augment_skills[sid] += 1
    industries = Counter(j.industry for j in jobs if j.industry)
    sample_titles: list[str] = []
    seen: set[str] = set()
    for j in jobs:
        if j.title and j.title not in seen:
            seen.add(j.title)
            sample_titles.append(j.title)
            if len(sample_titles) >= 8:
                break
    return {
        "vacancyCount": len(jobs),
        "salaryMedian": int(median(salaries)) if salaries else None,
        "salarySampleSize": len(salaries),
        "augmentSkills": [
            {"skillId": s, "count": c} for s, c in augment_skills.most_common(15)
        ],
        "topIndustries": [
            {"industry": ind, "count": cnt} for ind, cnt in industries.most_common(5)
        ],
        "sampleTitles": sample_titles,
    }


async def main():
    async with async_session() as db:
        jobs = (await db.execute(
            select(Job).where(
                Job.parse_status == "parsed",
                Job.role_type == "ai_augmented_traditional",
                Job.base_profession.isnot(None),
            )
        )).scalars().all()
    logger.info("loaded %d ai_augmented_traditional jobs", len(jobs))

    output: dict[str, dict[str, dict]] = {"domestic": {}, "international": {}}
    for market in ("domestic", "international"):
        groups: dict[str, list[Job]] = defaultdict(list)
        for j in jobs:
            if j.market != market:
                continue
            groups[j.base_profession].append(j)
        for prof, prof_jobs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            output[market][prof] = profession_stats(prof_jobs)
        logger.info("%s — %d professions", market, len(output[market]))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
