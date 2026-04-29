#!/usr/bin/env python3
"""Export role × city tier × salary breakdown for aijobfit consumption.

Business reviewer asked: "数据分析师在北上广深 vs 二线工资差多少？"
Existing roles-domestic.json only has nation-wide p25/p50/p75 — this
script slices by city tier (一线 / 新一线 / 其他国内 / 海外 / 远程) so
aijobfit can answer "given your target city, what's the realistic
salary range" instead of citing one global median.

Output schema → ``frontend/public/data/roles-by-city.json``::

    {
      "domestic": {
        "<role_id>": {
          "role_name": "...",
          "by_tier": [
            {
              "tier": "一线",
              "cities_in_tier": ["北京", "上海", ...],
              "job_count": N,
              "salary": {"p25":..., "p50":..., "p75":..., "sample_size": M}
            },
            ...
          ],
          "top_cities": [
            {"city": "上海", "count": N, "median": M, "sample": K},
            ...
          ]
        }
      },
      "international": { ... }
    }

Usage:
    cd backend && .venv/bin/python scripts/export_roles_by_city.py
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
from app.services.cities import (
    REMOTE_TOKENS, TIER_1, TIER_NEW_1, city_tier, split_locations,
)
from app.services.currency import midpoint_cny_monthly
from scripts.analyze_roles import (
    DOMESTIC_ROLES, INTERNATIONAL_ROLES, classify_job,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "roles-by-city.json"
)
RULES_BY_MARKET = {"domestic": DOMESTIC_ROLES, "international": INTERNATIONAL_ROLES}

# Order tiers by relevance for aijobfit's UI (highest-priority first).
DOMESTIC_TIER_ORDER = ["一线", "新一线", "其他国内", "远程"]
INTL_TIER_ORDER = ["海外", "远程"]


def percentiles(values: list[int]) -> dict | None:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    return {
        "p25": s[n // 4],
        "p50": int(median(s)),
        "p75": s[(n * 3) // 4],
        "sample_size": n,
    }


def build_role_city_breakdown(jobs: list[Job], market: str) -> dict | None:
    """Group `jobs` (already filtered to a single role) by city tier."""
    if not jobs:
        return None

    tier_order = DOMESTIC_TIER_ORDER if market == "domestic" else INTL_TIER_ORDER

    # Per-tier and per-city aggregates. A single Job's location can list
    # multiple cities ("北京、上海") — we count it once per city it mentions.
    tier_jobs: dict[str, list[Job]] = defaultdict(list)
    tier_salaries: dict[str, list[int]] = defaultdict(list)
    tier_cities: dict[str, set[str]] = defaultdict(set)

    city_jobs: dict[str, list[Job]] = defaultdict(list)
    city_salaries: dict[str, list[int]] = defaultdict(list)

    for j in jobs:
        cities = split_locations(j.location)
        if not cities:
            continue
        sal = midpoint_cny_monthly(j.salary_min, j.salary_max, j.salary_currency)
        for c in cities:
            t = city_tier(c)
            if t in {"未知"}:
                continue
            # Skip 海外/海外-style cities when we're in the domestic market and
            # vice versa (handles cases where Boss listings include intl. cities).
            if market == "domestic" and t == "海外":
                continue
            if market == "international" and t in {"一线", "新一线", "其他国内"}:
                continue

            tier_jobs[t].append(j)
            tier_cities[t].add(c)
            city_jobs[c].append(j)
            if sal is not None:
                tier_salaries[t].append(int(sal))
                city_salaries[c].append(int(sal))

    by_tier = []
    for t in tier_order:
        if not tier_jobs[t]:
            continue
        by_tier.append({
            "tier": t,
            "cities_in_tier": sorted(tier_cities[t]),
            "job_count": len(tier_jobs[t]),
            "salary": percentiles(tier_salaries[t]),
        })

    top_cities = []
    for city, cjobs in sorted(city_jobs.items(), key=lambda kv: -len(kv[1]))[:8]:
        salaries = city_salaries[city]
        top_cities.append({
            "city": city,
            "count": len(cjobs),
            "median": int(median(salaries)) if salaries else None,
            "sample": len(salaries),
        })

    return {"by_tier": by_tier, "top_cities": top_cities}


async def main():
    async with async_session() as db:
        jobs = (await db.execute(
            select(Job).where(
                Job.parse_status == "parsed",
                Job.title.isnot(None),
            )
        )).scalars().all()
    logger.info("loaded %d parsed jobs", len(jobs))

    output: dict[str, dict[str, dict]] = {"domestic": {}, "international": {}}

    for market, rules in RULES_BY_MARKET.items():
        market_jobs = [j for j in jobs if j.market == market]
        # Group jobs by classified role first.
        by_role: dict[str, list[Job]] = defaultdict(list)
        role_names: dict[str, str] = {}
        # Build role_id → role_name lookup once; rules are tuples (id, name, regex).
        role_names = {rule[0]: rule[1] for rule in rules}
        for j in market_jobs:
            rid = classify_job(j.title, rules)
            if rid in {"_noise", "other", None}:
                continue
            by_role[rid].append(j)

        for rid, role_jobs in by_role.items():
            breakdown = build_role_city_breakdown(role_jobs, market)
            if breakdown:
                output[market][rid] = {
                    "role_name": role_names.get(rid, rid),
                    **breakdown,
                }

        logger.info(
            "%s — %d roles with city breakdown",
            market, len(output[market]),
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
