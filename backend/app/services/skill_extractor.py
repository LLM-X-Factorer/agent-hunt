from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.skill import Skill

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


class SkillExtractor:

    def __init__(self) -> None:
        path = DATA_DIR / "skill_aliases.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._aliases: dict[str, str] = {
            k.lower().strip(): v
            for k, v in raw.items()
            if not k.startswith("_")
        }

    def normalize(self, raw_skill: str) -> str | None:
        key = raw_skill.lower().strip()
        if key in self._aliases:
            return self._aliases[key]
        # Try without spaces/hyphens
        compact = key.replace(" ", "").replace("-", "").replace("_", "")
        if compact in self._aliases:
            return self._aliases[compact]
        return None

    def normalize_list(self, raw_skills: list[str]) -> list[str]:
        seen = set()
        result = []
        for raw in raw_skills:
            sid = self.normalize(raw)
            if sid and sid not in seen:
                seen.add(sid)
                result.append(sid)
        return result


extractor = SkillExtractor()


async def normalize_all_jobs(db: AsyncSession) -> dict[str, int]:
    result = await db.execute(
        select(Job).where(Job.parse_status == "parsed")
    )
    jobs = result.scalars().all()

    counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"domestic": 0, "international": 0}
    )
    unmatched: dict[str, int] = defaultdict(int)
    jobs_processed = 0

    for job in jobs:
        all_skills = (job.required_skills or []) + (job.preferred_skills or [])
        if not all_skills:
            continue

        jobs_processed += 1
        market = job.market or "international"
        market_key = "domestic" if market == "domestic" else "international"

        normalized = set()
        for raw in all_skills:
            sid = extractor.normalize(raw)
            if sid:
                normalized.add(sid)
            else:
                unmatched[raw] += 1

        for sid in normalized:
            counts[sid][market_key] += 1

    # Update skill table
    skills_updated = 0
    for sid, mc in counts.items():
        domestic = mc["domestic"]
        international = mc["international"]
        total = domestic + international
        await db.execute(
            update(Skill)
            .where(Skill.id == sid)
            .values(
                domestic_count=domestic,
                international_count=international,
                total_count=total,
            )
        )
        skills_updated += 1

    await db.commit()

    logger.info(
        "Normalized %d jobs, updated %d skills, %d unmatched terms",
        jobs_processed, skills_updated, len(unmatched),
    )

    return {
        "jobs_processed": jobs_processed,
        "skills_updated": skills_updated,
        "unmatched_terms": len(unmatched),
    }


async def get_unmatched_terms(db: AsyncSession) -> list[dict[str, int | str]]:
    result = await db.execute(
        select(Job).where(Job.parse_status == "parsed")
    )
    jobs = result.scalars().all()

    unmatched: dict[str, int] = defaultdict(int)
    for job in jobs:
        for raw in (job.required_skills or []) + (job.preferred_skills or []):
            if extractor.normalize(raw) is None:
                unmatched[raw] += 1

    return sorted(
        [{"term": k, "count": v} for k, v in unmatched.items()],
        key=lambda x: x["count"],
        reverse=True,
    )
