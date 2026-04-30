#!/usr/bin/env python3
"""Rule-based backfill of jobs.work_mode from location + raw_content.

Why we need this: ~6,400 parsed jobs ship with work_mode=NULL because Boss/
Liepin/HN/etc rarely state "onsite/remote/hybrid" explicitly and the LLM
returns null. But location is usually concrete enough to infer:

- "Remote", "Remote in USA", "Anywhere", "Global"            -> remote
- "NYC or Remote", "SF; Remote-Friendly", "Remote, NYC"      -> hybrid
- "深圳", "北京", "San Francisco", "London, UK"              -> onsite
  (unless raw_content shows fully-remote keywords)

Conservative defaults: when location is ambiguous ("Multiple locations",
empty, missing) we leave NULL so a future LLM pass can decide.

Usage:
    cd backend && .venv/bin/python scripts/backfill_work_mode_from_location.py --dry-run
    cd backend && .venv/bin/python scripts/backfill_work_mode_from_location.py --apply
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import or_, select, update

from app.database import async_session
from app.models.job import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Location is a pure remote/anywhere expression — no concrete city.
REMOTE_ONLY_RE = re.compile(
    r"^\s*(remote|anywhere|worldwide|global|distributed|virtual"
    r"|remote\s*[-–]?\s*(only|first|preferred|us|usa|na|emea|apac|global)?"
    r"|remote\s+in\s+[\w &/]+"
    r"|remote\s*\([^)]+\)"
    r"|fully\s+remote)\s*$",
    re.IGNORECASE,
)

# Location lists multiple sites with at least one city + at least one
# remote/remote-friendly token (separator: comma, semicolon, " or ", " / ").
HYBRID_LOCATION_RE = re.compile(
    r"(remote|remote[\s-]friendly|anywhere)",
    re.IGNORECASE,
)
HAS_CITY_TOKEN_RE = re.compile(
    r"[A-Za-z]{2,},\s*[A-Z]{2}\b"  # "San Francisco, CA"
    r"|[一-鿿]{2,}"  # any chinese block (city)
    r"|\b(NYC|SF|LA|DC|UK|US|HQ)\b"
    r"|\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b",  # "London, UK", "Toronto, ON"
)

# Strong remote signal in raw_content: only flips an inferred onsite to remote
# when the JD itself explicitly says fully/100% remote.
RAW_FULLY_REMOTE_RE = re.compile(
    r"(fully\s+remote|100\s*%\s*remote|completely\s+remote"
    r"|全(部|程)?远程|完全远程|远程办公为主)",
    re.IGNORECASE,
)

# Mild remote signal that downgrades onsite -> hybrid (mentions remote option
# but not as the default). We do NOT flip to hybrid on these unless the
# location ALSO hints at it, to avoid false positives from boilerplate
# benefit copy.
RAW_HYBRID_HINT_RE = re.compile(
    r"(hybrid|remote[\s-]friendly|work[\s-]from[\s-]home option"
    r"|混合办公|远程办公(可选|友好)|wfh)",
    re.IGNORECASE,
)

AMBIGUOUS_LOCATION_RE = re.compile(
    r"^\s*(multiple\s+locations?|various|several|tbd|to\s+be\s+determined"
    r"|多地|多城市)\s*$",
    re.IGNORECASE,
)


def infer_work_mode(location: str | None, raw_content: str | None) -> str | None:
    if not location or not location.strip():
        return None
    loc = location.strip()

    if AMBIGUOUS_LOCATION_RE.match(loc):
        return None

    if REMOTE_ONLY_RE.match(loc):
        return "remote"

    has_remote = bool(HYBRID_LOCATION_RE.search(loc))
    has_city = bool(HAS_CITY_TOKEN_RE.search(loc))

    if has_remote and has_city:
        return "hybrid"
    if has_remote and not has_city:
        return "remote"

    raw = raw_content or ""
    if RAW_FULLY_REMOTE_RE.search(raw):
        return "remote"
    if has_city or any(c.isalpha() for c in loc):
        # location is a concrete place; default to onsite. We don't downgrade
        # to hybrid on a soft hint alone — too many JDs have "remote-friendly"
        # in the perks list while the role is still onsite.
        return "onsite"

    return None


async def main(apply: bool) -> None:
    async with async_session() as session:
        rows = (
            await session.execute(
                select(Job.id, Job.location, Job.raw_content, Job.market, Job.work_mode)
                .where(Job.parse_status == "parsed")
                .where(or_(Job.work_mode.is_(None), Job.work_mode == "unknown", Job.work_mode == "null"))
            )
        ).all()

    logger.info("Candidates with NULL/unknown work_mode: %d", len(rows))

    # Inference pass.
    inferred: dict[str, list] = {"onsite": [], "remote": [], "hybrid": []}
    by_market: Counter[tuple[str, str]] = Counter()
    skipped = 0
    for r in rows:
        mode = infer_work_mode(r.location, r.raw_content)
        if mode is None:
            skipped += 1
            continue
        inferred[mode].append(r.id)
        by_market[(r.market or "unknown", mode)] += 1

    logger.info("Inferred -> onsite=%d  remote=%d  hybrid=%d  skipped=%d",
                len(inferred["onsite"]), len(inferred["remote"]),
                len(inferred["hybrid"]), skipped)
    for (market, mode), n in sorted(by_market.items()):
        logger.info("  %s / %s: %d", market, mode, n)

    if not apply:
        logger.info("Dry-run; pass --apply to write.")
        return

    async with async_session() as session:
        for mode, ids in inferred.items():
            if not ids:
                continue
            await session.execute(
                update(Job).where(Job.id.in_(ids)).values(work_mode=mode)
            )
        await session.commit()
    logger.info("Applied.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True)
    g.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(apply=args.apply))
