#!/usr/bin/env python3
"""Backfill structured fields for Tencent vendor jobs without LLM.

The Tencent collector populates raw_content in a known format:
    {title}
    事业群: {BG} / {Category}[ / {Product}]
    位置: {LocationName}
    经验: {RequireWorkYearsName}

    {Responsibility body}

Since the format is deterministic (we generated it ourselves), we can
parse those structured fields directly without burning OpenRouter
tokens. Sets parse_status='parsed' so the entries flow into all the
narrative aggregations.

Fields populated:
  - title, company_name, location, market, industry, experience_min/max
  - parse_status='parsed', parsed_at=NOW()

Fields LEFT NULL (would need LLM):
  - salary_min/max, required_skills, preferred_skills, responsibilities,
    education, role_type
  (role_type gets filled by the subsequent backfill_role_type_rules.py run.)

Usage:
    cd backend && .venv/bin/python scripts/backfill_tencent_metadata.py
"""
from __future__ import annotations

import asyncio
import datetime
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, update

from app.database import async_session
from app.models.job import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

LOC_RE = re.compile(r"位置:\s*(.+?)\s*\n")
EXP_RE = re.compile(r"经验:\s*(.+?)\s*\n")
BG_RE = re.compile(r"事业群:\s*(.+?)\s*\n")

# Domestic city / country tokens — anything matching means CN/HK/TW/SG market.
# Tencent ranks these as "domestic" because their HQ + biggest BG ops are CN.
CN_LOCATION_RE = re.compile(
    r"中国|China|深圳|北京|上海|广州|杭州|成都|武汉|南京|西安|苏州|"
    r"重庆|天津|长沙|青岛|郑州|宁波|东莞|沈阳|合肥|香港|台北|新加坡",
    re.IGNORECASE,
)


def parse_experience(exp: str | None) -> tuple[int | None, int | None]:
    """『5年以上』 → (5, None); 『1-3年』 → (1, 3); 『不限』 → (None, None)."""
    if not exp or "不限" in exp:
        return None, None
    m = re.search(r"(\d+)\s*年?\s*-\s*(\d+)\s*年?", exp)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d+)\s*年?\s*以上", exp)
    if m:
        return int(m.group(1)), None
    m = re.search(r"(\d+)\s*年", exp)
    if m:
        n = int(m.group(1))
        return n, n
    return None, None


def detect_market(location: str | None) -> str | None:
    if not location:
        return None
    return "domestic" if CN_LOCATION_RE.search(location) else "international"


async def main():
    async with async_session() as db:
        rows = (await db.execute(
            select(Job).where(
                Job.platform_id == "vendor_tencent",
                Job.parse_status == "pending",
            )
        )).scalars().all()
    logger.info("loaded %d pending Tencent jobs", len(rows))

    if not rows:
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    updated = 0
    market_counter = {"domestic": 0, "international": 0, "unknown": 0}

    async with async_session() as db:
        for j in rows:
            raw = j.raw_content or ""
            # First non-empty line is the title.
            title = raw.split("\n", 1)[0].strip() if raw else None

            loc_m = LOC_RE.search(raw)
            location = loc_m.group(1).strip() if loc_m else None

            exp_m = EXP_RE.search(raw)
            exp_min, exp_max = parse_experience(exp_m.group(1) if exp_m else None)

            market = detect_market(location)
            market_counter[market or "unknown"] += 1

            await db.execute(
                update(Job).where(Job.id == j.id).values(
                    title=title,
                    company_name="腾讯",
                    location=location,
                    market=market,
                    industry="internet",  # Tencent is a tech/internet conglomerate
                    experience_min=exp_min,
                    experience_max=exp_max,
                    parse_status="parsed",
                    parsed_at=now,
                )
            )
            updated += 1
        await db.commit()

    logger.info("backfilled %d rows", updated)
    logger.info("market split: %s", market_counter)


if __name__ == "__main__":
    asyncio.run(main())
