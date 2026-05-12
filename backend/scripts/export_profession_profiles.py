#!/usr/bin/env python3
"""Aggregate ai_augmented_traditional jobs by traditional profession + merge hand-written
descriptions → frontend/public/data/profession-profiles.json (#37 B2).

Reads:
  - backend/data/profession_descriptions.json (8 hand-written entries with aliases)
  - DB: jobs WHERE role_type='ai_augmented_traditional' AND base_profession IN aliases

For each profession:
  - Aggregate JD-level fields (salary / education / majors / responsibilities / skills /
    companies / sample_titles) via build_role_profile() from analyze_roles.
  - Classify each job by title using DOMESTIC_ROLES / INTERNATIONAL_ROLES rules to
    derive "AI pivot targets" — the AI role clusters this profession is showing up in.
  - Pivot targets link to /roles/[market]/[role_id] on the frontend.

Usage:
    cd backend && .venv/bin/python scripts/export_profession_profiles.py
"""
import asyncio
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import or_, select

from app.database import async_session
from app.models.job import Job
from scripts.analyze_roles import (
    DOMESTIC_ROLES,
    INTERNATIONAL_ROLES,
    build_role_profile,
    classify_job,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DESCRIPTIONS_FILE = REPO_ROOT / "backend" / "data" / "profession_descriptions.json"
OUTPUT_FILE = REPO_ROOT / "frontend" / "public" / "data" / "profession-profiles.json"


def role_name_lookup() -> dict[tuple[str, str], str]:
    """(market, role_id) → role display name from the classification rules."""
    out: dict[tuple[str, str], str] = {}
    for rid, name, _ in DOMESTIC_ROLES:
        out[("domestic", rid)] = name
    for rid, name, _ in INTERNATIONAL_ROLES:
        out[("international", rid)] = name
    out[("domestic", "other")] = "其他"
    out[("international", "other")] = "Other"
    return out


async def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    descriptions = json.loads(DESCRIPTIONS_FILE.read_text(encoding="utf-8"))
    role_names = role_name_lookup()

    profession_profiles = []

    async with async_session() as db:
        for desc in descriptions:
            aliases = desc["aliases"]
            result = await db.execute(
                select(Job).where(
                    Job.role_type == "ai_augmented_traditional",
                    or_(*[Job.base_profession == a for a in aliases]),
                )
            )
            jobs = list(result.scalars().all())
            sample_size = len(jobs)
            logger.info(
                "%s: %d jobs (aliases=%s)", desc["profession_id"], sample_size, aliases
            )

            entry = {**desc, "sample_size": sample_size}

            if sample_size > 0:
                aggregate = build_role_profile(jobs)
                # Keep relevant aggregate fields only
                for k in (
                    "salary",
                    "experience",
                    "education",
                    "work_mode",
                    "top_companies",
                    "top_industries",
                    "top_majors",
                    "majors_sample_size",
                    "top_responsibilities",
                    "responsibilities_sample_size",
                    "sample_titles",
                    "required_skills",
                    "preferred_skills",
                ):
                    entry[k] = aggregate.get(k)

                # AI pivot targets — classify each job by title against its market's rules
                pivot_counter: Counter = Counter()
                # store role name lookup per (market, role_id) so we don't re-eval
                for j in jobs:
                    if not j.title:
                        continue
                    market = j.market or "domestic"
                    rules = DOMESTIC_ROLES if market == "domestic" else INTERNATIONAL_ROLES
                    rid = classify_job(j.title, rules)
                    if rid in ("_noise", "other"):
                        continue
                    pivot_counter[(market, rid)] += 1

                entry["ai_pivot_targets"] = [
                    {
                        "market": market,
                        "role_id": rid,
                        "role_name": role_names.get((market, rid), rid),
                        "count": cnt,
                    }
                    for (market, rid), cnt in pivot_counter.most_common(8)
                ]
            else:
                entry["sample_titles"] = []
                entry["ai_pivot_targets"] = []

            profession_profiles.append(entry)

    OUTPUT_FILE.write_text(
        json.dumps(profession_profiles, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "Written %s (%d professions)", OUTPUT_FILE.relative_to(REPO_ROOT), len(profession_profiles)
    )


if __name__ == "__main__":
    asyncio.run(main())
