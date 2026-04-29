#!/usr/bin/env python3
"""Pull Tencent (腾讯) AI hiring postings from careers.tencent.com (#12 国内大厂).

careers.tencent.com exposes a public no-auth JSON API used by their own
SPA frontend — the same endpoint we hit. Each entry comes with a full
Chinese-language Responsibility section, BG (business group) tag,
location, and a stable PostId. ~589 AI-keyword matches as of 2026-04.

Usage:
    cd backend && .venv/bin/python scripts/collect_vendor_tencent.py
    cd backend && .venv/bin/python scripts/collect_vendor_tencent.py --keyword 算法

Pagination:
    pageSize 50 × pageIndex 1..N until empty
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

from app.collectors.manual_import import import_jobs
from app.database import async_session
from app.schemas.job import JobImportRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Tencent API endpoint — public, returns JSON, no auth required.
TENCENT_API = "https://careers.tencent.com/tencentcareer/api/post/Query"
PLATFORM_ID = "vendor_tencent"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# Keywords to expand recall — Tencent's search isn't synonym-aware, so we
# query a few common AI/ML terms separately and dedup by PostId.
KEYWORDS = [
    "AI",          # broad
    "人工智能",
    "算法",
    "大模型",
    "机器学习",
    "深度学习",
    "LLM",
    "推荐",         # recommender / 推荐算法
]


async def fetch_page(client: httpx.AsyncClient, keyword: str, page: int, page_size: int = 50) -> list[dict]:
    params = {"keyword": keyword, "pageIndex": page, "pageSize": page_size}
    resp = await client.get(TENCENT_API, params=params, timeout=30)
    if resp.status_code != 200:
        logger.warning("tencent %s page %d — HTTP %d", keyword, page, resp.status_code)
        return []
    data = resp.json()
    return data.get("Data", {}).get("Posts", []) or []


async def fetch_keyword(client: httpx.AsyncClient, keyword: str) -> list[dict]:
    """Fetch every page for one keyword until empty."""
    out = []
    for page in range(1, 50):  # cap at 50 pages × 50 = 2500, well above realistic
        posts = await fetch_page(client, keyword, page)
        if not posts:
            break
        out.extend(posts)
        if len(posts) < 50:
            break
    logger.info("keyword %s — %d posts", keyword, len(out))
    return out


def detect_market(country_name: str | None, location_name: str | None) -> str:
    cn_tokens = ("中国", "China", "深圳", "北京", "上海", "广州", "杭州", "成都", "武汉")
    if country_name and any(t in country_name for t in cn_tokens):
        return "domestic"
    if location_name and any(t in location_name for t in cn_tokens):
        return "domestic"
    return "international"


def to_import_request(post: dict) -> JobImportRequest | None:
    title = post.get("RecruitPostName") or ""
    body = post.get("Responsibility") or ""
    if len(body) < 30:
        return None  # skip stub postings without a description

    location = post.get("LocationName") or post.get("CountryName") or ""
    bg = post.get("BGName") or ""
    category = post.get("CategoryName") or ""
    product = post.get("ProductName") or ""

    raw = (
        f"{title}\n"
        f"事业群: {bg} / {category}"
        + (f" / {product}" if product else "")
        + f"\n位置: {location}\n经验: {post.get('RequireWorkYearsName') or '不限'}\n\n"
        f"{body}"
    )

    return JobImportRequest(
        platform_id=PLATFORM_ID,
        platform_job_id=str(post.get("PostId")),
        source_url=post.get("PostURL"),
        raw_content=raw[:60000],
        language="zh" if any("一" <= c <= "鿿" for c in body[:200]) else "en",
        source="vendor_official",
    )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", help="search single keyword instead of full list")
    args = parser.parse_args()

    keywords = [args.keyword] if args.keyword else KEYWORDS

    seen: dict[str, dict] = {}  # PostId → post (dedup across keyword queries)
    async with httpx.AsyncClient(headers={"User-Agent": UA}) as client:
        for kw in keywords:
            posts = await fetch_keyword(client, kw)
            for p in posts:
                pid = str(p.get("PostId") or "")
                if pid and pid not in seen:
                    seen[pid] = p

    logger.info("total unique posts after dedup: %d", len(seen))

    requests = [r for r in (to_import_request(p) for p in seen.values()) if r]
    logger.info("valid import requests: %d", len(requests))

    if not requests:
        logger.info("nothing to import.")
        return

    imported = re_seen = 0
    for i in range(0, len(requests), 50):
        batch = requests[i : i + 50]
        async with async_session() as db:
            res = await import_jobs(db, batch)
        imported += res.imported
        re_seen += res.skipped

    logger.info("%s — imported=%d (new) re-seen=%d (already in DB)",
                PLATFORM_ID, imported, re_seen)


if __name__ == "__main__":
    asyncio.run(main())
