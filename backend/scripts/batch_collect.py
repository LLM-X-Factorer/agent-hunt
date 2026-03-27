#!/usr/bin/env python3
"""Batch collect jobs using the keyword matrix from data/search_keywords.json.

Usage:
    cd backend && .venv/bin/python scripts/batch_collect.py [--max-pages 1] [--category "AI Agent 核心"]

Calls the /api/v1/jobs/collect endpoint for each keyword × platform combination.
Respects rate limits with delays between requests.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import httpx

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
API_BASE = "http://localhost:8000/api/v1"

PLATFORM_DELAYS = {
    "linkedin": 3,
    "indeed": 3,
    "liepin": 8,
    "boss_zhipin": 12,
    "lagou": 10,
}


def main():
    parser = argparse.ArgumentParser(description="Batch collect jobs from keyword matrix")
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--category", type=str, default=None, help="Only run this category")
    parser.add_argument("--auto-parse", action="store_true", default=False)
    parser.add_argument("--api-url", type=str, default=API_BASE)
    args = parser.parse_args()

    keywords_file = DATA_DIR / "search_keywords.json"
    config = json.loads(keywords_file.read_text(encoding="utf-8"))

    total_collected = 0
    total_imported = 0
    total_skipped = 0

    for cat in config["categories"]:
        if args.category and cat["name"] != args.category:
            continue

        print(f"\n{'='*60}")
        print(f"  Category: {cat['name']}")
        print(f"  Keywords: {len(cat['keywords'])}, Platforms: {cat['platforms']}")
        print(f"{'='*60}")

        for keyword in cat["keywords"]:
            for platform in cat["platforms"]:
                delay = PLATFORM_DELAYS.get(platform, 5)

                try:
                    resp = httpx.post(
                        f"{args.api_url}/jobs/collect",
                        json={
                            "platform_id": platform,
                            "keyword": keyword,
                            "max_pages": args.max_pages,
                            "auto_parse": args.auto_parse,
                        },
                        timeout=300,
                    )
                    data = resp.json()
                    collected = data.get("collected", 0)
                    imported = data.get("imported", 0)
                    skipped = data.get("skipped", 0)

                    total_collected += collected
                    total_imported += imported
                    total_skipped += skipped

                    status = "OK" if resp.status_code == 200 else f"ERR {resp.status_code}"
                    print(
                        f"  [{status}] {platform:14s} | {keyword:20s} | "
                        f"collected={collected:3d} imported={imported:3d} skipped={skipped:3d}"
                    )
                except Exception as e:
                    print(f"  [FAIL] {platform:14s} | {keyword:20s} | {e}")

                time.sleep(delay)

    print(f"\n{'='*60}")
    print(f"  TOTAL: collected={total_collected}, imported={total_imported}, skipped={total_skipped}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
