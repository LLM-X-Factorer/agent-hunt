#!/usr/bin/env python3
"""Retry backfill for ByteDance JDs whose structured fields crashed mid-run.

The full collect_vendor_bytedance.py crashed during structured backfill
when Supabase dropped a long-running session. The raw_content was already
saved correctly; this script parses title / location / market / responsibilities
out of the stored raw_content text and writes the structured fields in
small batches with fresh sessions to dodge cross-region connection drops.

Usage:
    cd backend && .venv/bin/python scripts/backfill_bytedance_from_raw.py
    cd backend && .venv/bin/python scripts/backfill_bytedance_from_raw.py --limit 50
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
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


# Same parser as collect_vendor_bytedance.py
def split_numbered_list(text: str) -> list[str]:
    if not text:
        return []
    parts = re.split(r"(?:^|\n)\s*\d+\s*[、.．)\)]\s*", text.strip())
    items = [p.strip().rstrip("；;,，").strip() for p in parts if p.strip()]
    return [it for it in items if len(it) >= 10]


def parse_raw_content(raw: str) -> dict:
    """ByteDance raw_content format (set by collect_vendor_bytedance.py):

        {title}
        分类: {category}
        位置: {city}
        招聘类型: {recruit_type}

        【工作职责】
        {description}

        【任职要求】
        {requirement}
    """
    lines = (raw or "").split("\n")
    title = lines[0].strip() if lines else ""

    def _find_line(prefix: str) -> str:
        for line in lines[:8]:
            if line.startswith(prefix):
                return line[len(prefix):].strip()
        return ""

    location = _find_line("位置:") or _find_line("位置：")
    recruit_type = _find_line("招聘类型:") or _find_line("招聘类型：")

    # Extract 工作职责 section
    desc_match = re.search(
        r"【工作职责】\s*\n(.*?)(?:\n【任职要求】|\Z)", raw, re.S
    )
    description = desc_match.group(1).strip() if desc_match else ""

    return {
        "title": title,
        "location": location,
        "recruit_type": recruit_type,
        "description": description,
    }


INTL_CITIES = (
    "Mountain View", "San Jose", "Seattle", "London", "Singapore",
    "Tokyo", "Seoul", "Dublin", "Mumbai", "Sydney", "New York",
    "Los Angeles", "Boston", "Austin", "Washington",
)


def detect_market(location: str) -> str:
    if not location:
        return "domestic"
    if any(c in location for c in INTL_CITIES):
        return "international"
    return "domestic"


async def _process_one_batch(BATCH: int) -> int:
    """Process one batch of pending jobs in a fresh session. Returns number updated.
    Raises on session-level failures so caller can decide to retry / continue.
    """
    async with async_session() as db:
        stmt = (
            select(Job)
            .where(Job.platform_id == "vendor_bytedance")
            .where(Job.parse_status == "pending")
            .order_by(Job.id)
            .limit(BATCH)
        )
        jobs = (await db.execute(stmt)).scalars().all()
        if not jobs:
            return 0

        now = dt.datetime.now(dt.timezone.utc)
        for j in jobs:
            parsed = parse_raw_content(j.raw_content or "")
            market = detect_market(parsed["location"])
            is_campus = "校招" in parsed["recruit_type"]
            internship = "实习" in parsed["recruit_type"]
            exp_req = "fresh" if (is_campus or internship) else None
            responsibilities = split_numbered_list(parsed["description"])

            await db.execute(
                update(Job)
                .where(Job.id == j.id)
                .values(
                    title=parsed["title"][:250] or None,
                    company_name="字节跳动",
                    location=parsed["location"][:250] or None,
                    market=market,
                    responsibilities=responsibilities,
                    is_campus=is_campus,
                    internship_friendly=internship,
                    experience_requirement=exp_req,
                    parse_status="parsed",
                    parsed_at=now,
                    language="zh",
                )
            )

        await db.commit()
        return len(jobs)


async def backfill(limit: int | None):
    """Pull pending ByteDance jobs in small batches with retry on disconnect.
    Supabase ap-southeast-2 sometimes drops connections mid-script; instead of
    failing the whole run, log the disconnect and retry that batch.
    """
    BATCH = 25
    total_updated = 0
    consecutive_failures = 0
    MAX_CONSECUTIVE = 5  # bail if 5 batches in a row all fail

    while True:
        try:
            n = await _process_one_batch(BATCH)
            if n == 0:
                break  # no more pending
            total_updated += n
            consecutive_failures = 0
            logger.info("batch — running total updated=%d", total_updated)
        except Exception as e:
            consecutive_failures += 1
            logger.warning(
                "batch failed (consecutive=%d/%d): %s",
                consecutive_failures, MAX_CONSECUTIVE, str(e)[:160],
            )
            if consecutive_failures >= MAX_CONSECUTIVE:
                logger.error("too many consecutive failures, bailing")
                break
            # back off briefly to let the pool recover
            await asyncio.sleep(2)
            continue

        if limit and total_updated >= limit:
            break

    logger.info("DONE — updated=%d (consecutive_failures_at_end=%d)",
                total_updated, consecutive_failures)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    await backfill(args.limit)


if __name__ == "__main__":
    asyncio.run(main())
