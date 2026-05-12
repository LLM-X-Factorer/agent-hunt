#!/usr/bin/env python3
"""Pull ByteDance (字节跳动) AI hiring postings from jobs.bytedance.com (#12).

ByteDance frontend hits ``/api/v1/search/job/posts`` with a client-side
generated ``_signature`` query param. We can't replay the signature in
plain httpx, so we let Playwright render the search page (which fires the
signed request) and intercept the JSON response.

The API response is rich — each post includes ``title``, ``description``
(full responsibilities body), ``requirement``, ``city_info``, ``recruit_type``,
which is exactly what we need to skip the LLM JD parser for these jobs.

Usage:
    cd backend && .venv/bin/python scripts/collect_vendor_bytedance.py
    cd backend && .venv/bin/python scripts/collect_vendor_bytedance.py --keyword 大模型
    cd backend && .venv/bin/python scripts/collect_vendor_bytedance.py --max-pages 2

Pagination:
    URL ?current=N&limit=20 — paginate until empty list or safety cap.
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import logging
import re
import sys
import urllib.parse as up
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright
from sqlalchemy import update

from app.collectors.manual_import import import_jobs
from app.database import async_session
from app.models.job import Job
from app.schemas.job import JobImportRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PLATFORM_ID = "vendor_bytedance"
SEARCH_URL = (
    "https://jobs.bytedance.com/experienced/position"
    "?keywords={kw}&category=&location=&project=&type=&job_hot_flag="
    "&current={page}&limit=20"
)
API_PATH = "/api/v1/search/job/posts"

# Keywords to expand recall. ByteDance's search is keyword-literal, so each
# query is independent — we dedup by post id afterwards.
KEYWORDS = [
    "AI",
    "人工智能",
    "算法",
    "大模型",
    "机器学习",
    "深度学习",
    "LLM",
    "推荐",
    "Agent",
    "NLP",
    "CV",
    "多模态",
]


async def fetch_keyword(page, keyword: str, max_pages: int = 30) -> list[dict]:
    """Render search pages for keyword, intercept API responses, accumulate posts."""
    posts: list[dict] = []
    encoded_kw = up.quote(keyword)

    # Hold a future for each pending API response so we don't race with the
    # network. Use a list because each navigation triggers one API hit.
    captured: list[dict] = []

    def on_response(response):
        if API_PATH in response.url:
            try:
                # schedule body parse in event loop
                asyncio.create_task(_capture(response, captured))
            except Exception as e:
                logger.debug("on_response error: %s", e)

    async def _capture(response, sink: list[dict]):
        try:
            data = await response.json()
            if data.get("code") == 0:
                sink.append(data.get("data") or {})
        except Exception as e:
            logger.debug("capture json failed: %s", e)

    page.on("response", on_response)

    for pg in range(1, max_pages + 1):
        url = SEARCH_URL.format(kw=encoded_kw, page=pg)
        captured.clear()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            logger.warning("[%s p%d] goto failed: %s", keyword, pg, str(e)[:80])
            break
        # Let the signed API request fire + response arrive
        await page.wait_for_timeout(2500)
        # Sometimes the API call comes a bit later — wait once more if empty
        if not captured:
            await page.wait_for_timeout(2000)
        if not captured:
            logger.info("[%s p%d] no API response captured — stop", keyword, pg)
            break

        # Each navigation may produce multiple captures if the page re-fires;
        # pick the largest one (the actual list).
        best = max(captured, key=lambda d: len(d.get("job_post_list") or []))
        page_posts = best.get("job_post_list") or []
        total = best.get("count")
        posts.extend(page_posts)
        logger.info(
            "[%s p%d] +%d posts (total now %d, server-count=%s)",
            keyword, pg, len(page_posts), len(posts), total,
        )
        if len(page_posts) < 20:
            break

    page.remove_listener("response", on_response)
    return posts


def detect_market(post: dict) -> str:
    """ByteDance posts have a `city_info` with `name` in Chinese. Most are
    domestic. International offices (Mountain View, Singapore, London, Seoul)
    show up too — split by city name."""
    intl_cities = (
        "Mountain View", "San Jose", "Seattle", "London", "Singapore",
        "Tokyo", "Seoul", "Dublin", "Mumbai", "Sydney",
    )
    city_info = post.get("city_info") or {}
    city_name = city_info.get("name") or ""
    if any(c in city_name for c in intl_cities):
        return "international"
    return "domestic"


def to_import_request(post: dict) -> JobImportRequest | None:
    title = post.get("title") or ""
    description = post.get("description") or ""
    requirement = post.get("requirement") or ""
    if len(description) + len(requirement) < 60:
        return None  # skip postings without real content

    city = (post.get("city_info") or {}).get("name") or ""
    job_category = (post.get("job_category") or {}).get("name") or ""
    recruit_type = (post.get("recruit_type") or {}).get("name") or ""

    raw = (
        f"{title}\n"
        f"分类: {job_category}\n"
        f"位置: {city}\n"
        f"招聘类型: {recruit_type}\n\n"
        f"【工作职责】\n{description}\n\n"
        f"【任职要求】\n{requirement}"
    )

    post_id = str(post.get("id") or "")
    source_url = f"https://jobs.bytedance.com/experienced/position/{post_id}/detail"

    # Cheap CN/EN heuristic from description's first 200 chars
    lang = "zh" if any("一" <= c <= "鿿" for c in (description + title)[:200]) else "en"

    return JobImportRequest(
        platform_id=PLATFORM_ID,
        platform_job_id=post_id,
        source_url=source_url,
        raw_content=raw[:60000],
        language=lang,
        source="vendor_official",
    )


def split_numbered_list(text: str) -> list[str]:
    """Parse ByteDance's numbered Chinese list ("1、... 2、... 3.") into items.
    Each item gets the original Chinese punctuation removed at start, trailing
    semicolon/period kept.
    """
    if not text:
        return []
    # Patterns: '1、', '1.', '1．', '1)', '1）'
    parts = re.split(r"(?:^|\n)\s*\d+\s*[、.．)\)]\s*", text.strip())
    items = [p.strip().rstrip("；;,，").strip() for p in parts if p.strip()]
    # filter out anything < 10 chars (likely empty/garbage)
    return [it for it in items if len(it) >= 10]


async def backfill_structured_fields(posts: list[dict]) -> int:
    """Walk imported posts, parse description/requirement into structured
    fields, mark parse_status='parsed'. Matches the moka / feishu pattern."""
    if not posts:
        return 0
    now = dt.datetime.now(dt.timezone.utc)
    updated = 0
    async with async_session() as db:
        for post in posts:
            post_id = str(post.get("id") or "")
            if not post_id:
                continue
            description = post.get("description") or ""
            requirement = post.get("requirement") or ""
            title = (post.get("title") or "")[:250] or None
            city_info = post.get("city_info") or {}
            location = (city_info.get("name") or "")[:250] or None
            recruit_type = (post.get("recruit_type") or {}).get("name") or ""
            market = detect_market(post)
            is_campus = "校招" in recruit_type
            internship_friendly = "实习" in recruit_type
            # Map ByteDance's recruit_type into our experience_requirement enum.
            # values: fresh | 0-1y | 1-3y | 3-5y | 5y+ — use fresh for campus/intern,
            # leave others NULL since ByteDance doesn't return year ranges.
            exp_req = "fresh" if (is_campus or internship_friendly) else None

            responsibilities = split_numbered_list(description)
            # Requirement also numbered — use first 5 as required_skills hint
            # (it's not skills in our taxonomy sense, but at least non-empty).
            # We leave required_skills NULL since the format isn't a skill list.

            res = await db.execute(
                update(Job)
                .where(Job.platform_id == PLATFORM_ID)
                .where(Job.platform_job_id == post_id)
                .values(
                    title=title,
                    company_name="字节跳动",
                    location=location,
                    market=market,
                    responsibilities=responsibilities,
                    is_campus=is_campus,
                    internship_friendly=internship_friendly,
                    experience_requirement=exp_req,
                    parse_status="parsed",
                    parsed_at=now,
                    language="zh",
                )
            )
            updated += res.rowcount or 0
        await db.commit()
    return updated


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", help="single keyword instead of full sweep")
    parser.add_argument("--max-pages", type=int, default=30,
                        help="cap on pages per keyword (default 30)")
    args = parser.parse_args()

    keywords = [args.keyword] if args.keyword else KEYWORDS

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()

        seen: dict[str, dict] = {}
        for kw in keywords:
            logger.info("--- keyword: %s ---", kw)
            posts = await fetch_keyword(page, kw, max_pages=args.max_pages)
            for post in posts:
                pid = str(post.get("id") or "")
                if pid and pid not in seen:
                    seen[pid] = post

        await browser.close()

    logger.info("total unique posts after dedup: %d", len(seen))
    requests = [r for r in (to_import_request(p) for p in seen.values()) if r]
    logger.info("valid import requests: %d", len(requests))

    if not requests:
        return

    imported = re_seen = 0
    for i in range(0, len(requests), 50):
        batch = requests[i : i + 50]
        async with async_session() as db:
            res = await import_jobs(db, batch)
        imported += res.imported
        re_seen += res.skipped

    logger.info(
        "%s — imported=%d (new) re-seen=%d (already in DB)",
        PLATFORM_ID, imported, re_seen,
    )

    # Backfill structured fields directly — no LLM needed, ByteDance API
    # already returns description / requirement / city / recruit_type.
    bf = await backfill_structured_fields(list(seen.values()))
    logger.info("%s — backfilled %d rows (parse_status='parsed')", PLATFORM_ID, bf)


if __name__ == "__main__":
    asyncio.run(main())
