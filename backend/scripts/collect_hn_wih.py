#!/usr/bin/env python3
"""Pull AI-relevant postings from HN 'Who is Hiring' threads (#17).

HN Algolia API is fully open and zero-anti-scrape. We:
  1. Search for the most-recent N "Ask HN: Who is hiring? (<month> <year>)"
     stories authored by user `whoishiring`.
  2. Fetch each thread's full comment tree via /api/v1/items/<id>.
  3. Title-keyword filter relevant comments (AI / ML / LLM / etc.) — most
     of HN WIH is generic SDE noise.
  4. Each comment becomes one Job entry with source=community_open and
     platform_id=community_hn_wih.

Skips LLM parsing — Job pipeline handles that downstream via the existing
``/jobs/parse/batch`` flow once jobs are imported.

Usage:
    cd backend && .venv/bin/python scripts/collect_hn_wih.py
    cd backend && .venv/bin/python scripts/collect_hn_wih.py --months 12
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

ALGOLIA_BASE = "https://hn.algolia.com/api/v1"
PLATFORM_ID = "community_hn_wih"

HTML_TAG_RE = re.compile(r"<[^>]+>")

AI_KEYWORD_RE = re.compile(
    r"\bAI\b|\bML\b|\bLLM\b|\bNLP\b|machine.learning|deep.learning|"
    r"artificial.intelligence|generative|foundation.model|"
    r"transformer|diffusion|GPT|GenAI|RAG|agent|fine.tun|prompt|"
    r"langchain|llamaindex|vector.database|embedding|RLHF|"
    r"compiler|inference|kubernetes.+(GPU|AI)|cuda|tensor",
    re.I,
)


def html_to_text(html: str | None) -> str:
    if not html:
        return ""
    return HTML_TAG_RE.sub(" ", unescape(html)).strip()


async def fetch_recent_wih_threads(
    client: httpx.AsyncClient, months: int
) -> list[dict]:
    """Get the latest N WIH stories authored by user 'whoishiring'."""
    url = (
        f"{ALGOLIA_BASE}/search_by_date"
        f"?tags=story,author_whoishiring&query=hiring&hitsPerPage={months + 5}"
    )
    resp = await client.get(url, timeout=30)
    resp.raise_for_status()
    hits = resp.json().get("hits", [])
    threads: list[dict] = []
    for h in hits:
        title = h.get("title") or ""
        if title.lower().startswith("ask hn: who is hiring"):
            threads.append({"id": h["objectID"], "title": title, "created": h["created_at"]})
        if len(threads) >= months:
            break
    return threads


async def fetch_thread_comments(client: httpx.AsyncClient, story_id: str) -> list[dict]:
    """Returns flat list of top-level comment dicts."""
    url = f"{ALGOLIA_BASE}/items/{story_id}"
    resp = await client.get(url, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data.get("children") or []


def comment_relevant(text: str) -> bool:
    return bool(AI_KEYWORD_RE.search(text))


def to_import_request(thread: dict, comment: dict) -> JobImportRequest | None:
    text_html = comment.get("text") or ""
    if not text_html:
        return None
    text = html_to_text(text_html)
    if len(text) < 80:
        return None
    if not comment_relevant(text):
        return None
    cid = str(comment.get("id"))
    if not cid:
        return None
    # Use the first line as a synthetic title — HN convention is
    # "Company (Location) — Role — stack..." on line 1.
    first_line = text.split("\n")[0].strip()[:240] or thread["title"]
    raw = f"{first_line}\n\n[Posted in: {thread['title']}]\n\n{text}"
    source_url = f"https://news.ycombinator.com/item?id={cid}"
    return JobImportRequest(
        platform_id=PLATFORM_ID,
        platform_job_id=cid,
        source_url=source_url,
        raw_content=raw[:60000],
        language="en",
        source="community_open",
    )


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--months", type=int, default=6,
        help="how many recent WIH threads to harvest",
    )
    args = parser.parse_args()

    async with httpx.AsyncClient() as client:
        threads = await fetch_recent_wih_threads(client, args.months)
        logger.info("found %d recent WIH threads", len(threads))
        for t in threads:
            logger.info("  %s — %s", t["id"], t["title"])

        all_requests: list[JobImportRequest] = []
        for t in threads:
            comments = await fetch_thread_comments(client, t["id"])
            requests = [
                r for r in (to_import_request(t, c) for c in comments) if r
            ]
            logger.info(
                "  %s — %d total comments / %d AI-relevant",
                t["id"], len(comments), len(requests),
            )
            all_requests.extend(requests)

    if not all_requests:
        logger.warning("nothing to import")
        return

    imported_total = re_seen_total = 0
    for i in range(0, len(all_requests), 50):
        batch = all_requests[i : i + 50]
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
