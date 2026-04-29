#!/usr/bin/env python3
"""Export vendor_official title breakdown — Forward Deployed/Solutions/etc (P0 论断 3).

Powers the narrative-handbook "客户端工程师" page: ~20% of OpenAI/Anthropic
engineering hires are FDE / Applied / Solutions / Implementation roles.

Categories (case-insensitive, regex on title):
  - fde:        forward deployed
  - solutions:  solutions engineer | solution architect
  - applied:    applied engineer | applied (excluding "applied research")
  - deploy:     deployment | implementation | onboard
  - customer:   success | customer
Anything else → "core" (research/eng/PM/etc).

Output schema:
    {
      "by_vendor": {
        "vendor_openai": {
          "total": 652,
          "categories": {"fde": 40, "solutions": 18, ...},
          "client_facing_total": 136,
          "client_facing_pct": 20.9,
          "samples": {"fde": ["title1", "title2", ...]}
        },
        ...
      },
      "summary": {
        "total_vendors": N,
        "total_jobs": N,
        "total_client_facing": N,
        "client_facing_pct": ...
      }
    }

Usage:
    cd backend && .venv/bin/python scripts/export_vendor_title_breakdown.py
"""
import asyncio
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.job import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "vendor-title-breakdown.json"
)

# Order matters: first match wins, so put more specific patterns first.
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("fde", re.compile(r"\bforward deployed\b", re.IGNORECASE)),
    ("solutions", re.compile(r"\b(solutions engineer|solution architect|solutions architect)\b", re.IGNORECASE)),
    ("deploy", re.compile(r"\b(deployment|implementation|onboarding)\b", re.IGNORECASE)),
    ("applied", re.compile(r"\bapplied (engineer|engineering|ai)\b", re.IGNORECASE)),
    ("customer", re.compile(r"\b(customer success|customer engineer|technical success)\b", re.IGNORECASE)),
]
CLIENT_FACING_CATS = {"fde", "solutions", "deploy", "applied", "customer"}


def categorize(title: str) -> str:
    for cat, pattern in PATTERNS:
        if pattern.search(title):
            return cat
    return "core"


async def main():
    async with async_session() as db:
        jobs = (await db.execute(
            select(Job).where(
                Job.platform_id.like("vendor_%"),
                Job.title.isnot(None),
            )
        )).scalars().all()
    logger.info("loaded %d vendor_* jobs", len(jobs))

    by_vendor: dict[str, list[Job]] = defaultdict(list)
    for j in jobs:
        by_vendor[j.platform_id].append(j)

    output: dict[str, dict] = {}
    grand_total = 0
    grand_client = 0

    for vendor, vjobs in sorted(by_vendor.items(), key=lambda kv: -len(kv[1])):
        cat_counts: dict[str, int] = defaultdict(int)
        cat_samples: dict[str, list[str]] = defaultdict(list)
        for j in vjobs:
            cat = categorize(j.title)
            cat_counts[cat] += 1
            if len(cat_samples[cat]) < 6 and j.title not in cat_samples[cat]:
                cat_samples[cat].append(j.title)

        client_total = sum(cat_counts[c] for c in CLIENT_FACING_CATS)
        total = len(vjobs)
        output[vendor] = {
            "total": total,
            "categories": dict(cat_counts),
            "client_facing_total": client_total,
            "client_facing_pct": round(client_total / total * 100, 1) if total else 0,
            "samples": {c: cat_samples[c] for c in CLIENT_FACING_CATS if cat_samples[c]},
        }
        grand_total += total
        grand_client += client_total

    summary = {
        "total_vendors": len(output),
        "total_jobs": grand_total,
        "total_client_facing": grand_client,
        "client_facing_pct": round(grand_client / grand_total * 100, 1) if grand_total else 0,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps({"by_vendor": output, "summary": summary}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s — %d client-facing / %d total (%.1f%%)",
                OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent),
                grand_client, grand_total, summary["client_facing_pct"])


if __name__ == "__main__":
    asyncio.run(main())
