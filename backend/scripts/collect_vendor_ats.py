#!/usr/bin/env python3
"""Pull vendor official AI hiring postings via Greenhouse / Ashby APIs (#12).

Both ATSs expose public, no-auth job-board endpoints:
  Greenhouse: https://boards-api.greenhouse.io/v1/boards/<slug>/jobs?content=true
  Ashby:      https://api.ashbyhq.com/posting-api/job-board/<slug>

Coverage as of 2026-04:
  Greenhouse — anthropic (~452) / xai (~230) / deepmind (~82)
  Ashby      — openai (~653) / cohere (~115)

Each posting is normalized into the JD ingestion format (raw_content =
title + location + description) and written via import_jobs() with
``source="vendor_official"``. Subsequent runs are idempotent via
the existing (platform_id, platform_job_id) unique constraint, and #16
seen_count / last_seen_at signals fire automatically.

Usage:
    cd backend && .venv/bin/python scripts/collect_vendor_ats.py
    cd backend && .venv/bin/python scripts/collect_vendor_ats.py --vendor openai
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import re
import sys
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

from app.collectors.manual_import import import_jobs
from app.database import async_session
from app.schemas.job import JobImportRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# (platform_id, ATS, board_slug)
VENDORS = [
    ("vendor_anthropic", "greenhouse", "anthropic"),
    ("vendor_xai", "greenhouse", "xai"),
    ("vendor_deepmind", "greenhouse", "deepmind"),
    ("vendor_openai", "ashby", "openai"),
    ("vendor_cohere", "ashby", "cohere"),
]

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
HTML_TAG_RE = re.compile(r"<[^>]+>")


def html_to_text(html: str | None) -> str:
    if not html:
        return ""
    return HTML_TAG_RE.sub(" ", unescape(html)).strip()


async def fetch_greenhouse(client: httpx.AsyncClient, slug: str) -> list[dict]:
    """Returns list of normalized job dicts: {id, title, location, body}."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    resp = await client.get(url, timeout=60)
    if resp.status_code != 200:
        logger.warning("greenhouse %s — HTTP %d", slug, resp.status_code)
        return []
    data = resp.json()
    out = []
    for j in data.get("jobs", []) or []:
        out.append({
            "id": str(j.get("id")),
            "title": j.get("title") or "",
            "location": (j.get("location") or {}).get("name", ""),
            "body": html_to_text(j.get("content") or ""),
            "absolute_url": j.get("absolute_url"),
        })
    return out


async def fetch_ashby(client: httpx.AsyncClient, slug: str) -> list[dict]:
    """Returns list of normalized job dicts."""
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    # Ashby /openai response is ~10MB; give it space.
    resp = await client.get(url, timeout=180)
    if resp.status_code != 200:
        logger.warning("ashby %s — HTTP %d", slug, resp.status_code)
        return []
    data = resp.json()
    out = []
    for j in data.get("jobs", []) or []:
        location = j.get("location") or ""
        if isinstance(location, dict):
            location = location.get("name", "")
        out.append({
            "id": j.get("id"),
            "title": j.get("title") or "",
            "location": location,
            "body": html_to_text(j.get("descriptionHtml") or "")
                    or (j.get("descriptionPlain") or ""),
            "absolute_url": j.get("jobUrl") or j.get("applyUrl"),
        })
    return out


def to_import_request(platform_id: str, j: dict) -> JobImportRequest | None:
    body = j["body"]
    if len(body) < 30:
        return None  # skip empty descriptions
    raw = f"{j['title']}\n位置: {j['location']}\n\n{body}"
    return JobImportRequest(
        platform_id=platform_id,
        platform_job_id=str(j["id"]),
        source_url=j.get("absolute_url"),
        raw_content=raw[:60000],
        language="en",
        source="vendor_official",
    )


async def collect_one(client: httpx.AsyncClient, platform_id: str, ats: str, slug: str) -> int:
    if ats == "greenhouse":
        jobs = await fetch_greenhouse(client, slug)
    elif ats == "ashby":
        jobs = await fetch_ashby(client, slug)
    else:
        logger.error("unknown ATS %s", ats)
        return 0

    requests = [r for r in (to_import_request(platform_id, j) for j in jobs) if r]
    logger.info("%s (%s/%s) — %d jobs / %d valid imports", platform_id, ats, slug, len(jobs), len(requests))
    if not requests:
        return 0

    # Batch in chunks of 50 to avoid huge transactions.
    imported_total = 0
    re_seen_total = 0
    for i in range(0, len(requests), 50):
        batch = requests[i : i + 50]
        async with async_session() as db:
            res = await import_jobs(db, batch)
        imported_total += res.imported
        re_seen_total += res.skipped
    logger.info(
        "%s — imported=%d (new) re-seen=%d (already in DB)",
        platform_id, imported_total, re_seen_total,
    )
    return imported_total


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vendor",
        default=None,
        help="comma-sep platform_id(s); default = all from VENDORS",
    )
    args = parser.parse_args()

    targets = VENDORS
    if args.vendor:
        wanted = set(args.vendor.split(","))
        targets = [(pid, ats, slug) for pid, ats, slug in VENDORS if pid in wanted]

    async with httpx.AsyncClient(headers={"User-Agent": UA}) as client:
        for pid, ats, slug in targets:
            try:
                await collect_one(client, pid, ats, slug)
            except Exception as e:
                logger.exception("collector failed for %s: %s", pid, str(e)[:200])


if __name__ == "__main__":
    asyncio.run(main())
