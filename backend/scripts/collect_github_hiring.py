#!/usr/bin/env python3
"""Pull AI-relevant new-grad / internship postings from GitHub hiring repos (#17).

We target community-maintained repos that publish a structured listings.json
data file (the SimplifyJobs / vanshb03 ecosystem). These are zero-anti-scrape
(plain raw.githubusercontent.com), already-deduped per repo, and updated daily.

Sources (all default branch = dev, file at .github/scripts/listings.json):
  - SimplifyJobs/New-Grad-Positions       → full-time new grad
  - SimplifyJobs/Summer2026-Internships   → summer internships
  - vanshb03/Summer2025-Internships       → alt internship list

Per upstream schema each item has fields like company_name / title / locations /
category / degrees / sponsorship / url / date_posted / id (uuid). We:

  1. Drop inactive / hidden entries (active=False or is_visible=False).
  2. Keep only AI-relevant categories (AI/ML/Data, Software*, Data Science*) —
     OR entries whose title matches AI keywords (LLM / ML / NLP / etc.).
  3. Deduplicate cross-source by normalized URL (same JD often listed in 2 repos).
  4. Synthesize a short JD-like text body — the downstream LLM parser handles
     skill extraction from this metadata.

Each item becomes one Job with source=community_open and
platform_id=community_github_hiring.

Usage:
    cd backend && .venv/bin/python scripts/collect_github_hiring.py
    cd backend && .venv/bin/python scripts/collect_github_hiring.py --limit 30
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

import httpx

from app.collectors.manual_import import import_jobs
from app.database import async_session
from app.schemas.job import JobImportRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PLATFORM_ID = "community_github_hiring"

SOURCES = [
    {
        "label": "SimplifyJobs/New-Grad-Positions",
        "kind": "newgrad",
        "url": "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json",
    },
    {
        "label": "SimplifyJobs/Summer2026-Internships",
        "kind": "internship",
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/.github/scripts/listings.json",
    },
    {
        "label": "vanshb03/Summer2025-Internships",
        "kind": "internship",
        "url": "https://raw.githubusercontent.com/vanshb03/Summer2025-Internships/dev/.github/scripts/listings.json",
    },
]

# Categories whose entries we always keep.
AI_CATEGORIES = {
    "AI/ML/Data",
    "Data Science, AI & Machine Learning",
}
# Categories where we apply the title keyword filter.
SOFTWARE_CATEGORIES = {
    "Software",
    "Software Engineering",
    "Product",
    "Product Management",
}

AI_KEYWORD_RE = re.compile(
    r"\bAI\b|\bML\b|\bLLM\b|\bNLP\b|machine.learning|deep.learning|"
    r"artificial.intelligence|generative|foundation.model|"
    r"transformer|diffusion|GPT|GenAI|RAG|agent|fine.tun|prompt|"
    r"langchain|llamaindex|vector|embedding|RLHF|inference|"
    r"data.scien|data.engineer|research.scien|applied.scien|"
    r"computer.vision|robotic",
    re.I,
)


def keep_listing(item: dict) -> bool:
    if not item.get("active"):
        return False
    if not item.get("is_visible", True):
        return False
    title = item.get("title") or ""
    category = (item.get("category") or "").strip()
    if category in AI_CATEGORIES:
        return True
    if category in SOFTWARE_CATEGORIES:
        return bool(AI_KEYWORD_RE.search(title))
    # Items without category (vanshb03 schema) — always check title.
    if not category:
        return bool(AI_KEYWORD_RE.search(title))
    return False


URL_TRIM_RE = re.compile(r"[?#].*$")


def normalize_url(url: str) -> str:
    if not url:
        return ""
    u = url.strip().lower()
    u = URL_TRIM_RE.sub("", u)
    return u.rstrip("/")


def synthesize_raw_content(item: dict, source_label: str, kind: str) -> str:
    company = item.get("company_name") or "Unknown"
    title = item.get("title") or ""
    locations = item.get("locations") or []
    category = item.get("category") or ""
    sponsorship = item.get("sponsorship") or ""
    degrees = item.get("degrees") or []
    url = item.get("url") or ""

    posted_ts = item.get("date_posted") or 0
    posted_str = ""
    if posted_ts:
        try:
            posted_str = dt.datetime.fromtimestamp(int(posted_ts), tz=dt.timezone.utc).date().isoformat()
        except (ValueError, OSError):
            posted_str = ""

    role_kind = "Full-time new grad" if kind == "newgrad" else "Internship"

    lines = [
        title,
        "",
        f"Company: {company}",
        f"Role type: {role_kind}",
    ]
    if locations:
        lines.append(f"Locations: {', '.join(str(loc) for loc in locations)}")
    if category:
        lines.append(f"Category: {category}")
    if degrees:
        lines.append(f"Degrees: {', '.join(str(d) for d in degrees)}")
    if sponsorship:
        lines.append(f"Sponsorship: {sponsorship}")
    if posted_str:
        lines.append(f"Posted: {posted_str}")
    if url:
        lines.append(f"Apply: {url}")
    lines.append("")
    lines.append(f"[Listed in {source_label} (GitHub community aggregator). Full description on company site.]")
    return "\n".join(lines)


def to_import_request(item: dict, source_label: str, kind: str) -> JobImportRequest | None:
    listing_id = item.get("id")
    url = item.get("url") or ""
    if not listing_id or not url:
        return None
    raw = synthesize_raw_content(item, source_label, kind)
    return JobImportRequest(
        platform_id=PLATFORM_ID,
        platform_job_id=str(listing_id),
        source_url=url,
        raw_content=raw[:60000],
        language="en",
        source="community_open",
    )


async def fetch_listings(client: httpx.AsyncClient, url: str) -> list[dict]:
    resp = await client.get(url, timeout=60)
    resp.raise_for_status()
    return resp.json()


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit", type=int, default=0,
        help="cap total listings to import (0 = no cap, useful for smoke tests)",
    )
    args = parser.parse_args()

    seen_urls: set[str] = set()
    all_requests: list[JobImportRequest] = []

    async with httpx.AsyncClient() as client:
        for src in SOURCES:
            try:
                listings = await fetch_listings(client, src["url"])
            except Exception as e:
                logger.warning("failed to fetch %s: %s", src["label"], e)
                continue

            kept = 0
            cross_dup = 0
            for item in listings:
                if not keep_listing(item):
                    continue
                norm_url = normalize_url(item.get("url") or "")
                if not norm_url:
                    continue
                if norm_url in seen_urls:
                    cross_dup += 1
                    continue
                req = to_import_request(item, src["label"], src["kind"])
                if req is None:
                    continue
                seen_urls.add(norm_url)
                all_requests.append(req)
                kept += 1

            logger.info(
                "  %s — total=%d kept=%d cross_dup=%d",
                src["label"], len(listings), kept, cross_dup,
            )

    if args.limit and args.limit > 0:
        all_requests = all_requests[: args.limit]
        logger.info("limit=%d → trimmed to %d requests", args.limit, len(all_requests))

    if not all_requests:
        logger.warning("nothing to import")
        return

    logger.info("importing %d listings...", len(all_requests))
    imported_total = re_seen_total = 0
    for i in range(0, len(all_requests), 100):
        batch = all_requests[i : i + 100]
        async with async_session() as db:
            res = await import_jobs(db, batch)
        imported_total += res.imported
        re_seen_total += res.skipped
    logger.info(
        "done — imported=%d (new) re-seen=%d (already in DB)",
        imported_total, re_seen_total,
    )


if __name__ == "__main__":
    asyncio.run(main())
