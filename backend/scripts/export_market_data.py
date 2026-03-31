#!/usr/bin/env python3
"""Export market-specific analysis data (industry + cooccurrence) per market.

Outputs:
  - industry-domestic.json   — industry overview filtered to domestic jobs
  - industry-international.json — industry overview filtered to international jobs
  - cooccurrence-domestic.json  — skill cooccurrence for domestic market
  - cooccurrence-international.json — skill cooccurrence for international market

Usage:
    cd backend && .venv/bin/python scripts/export_market_data.py
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import async_session
from app.services.cross_market import industry_overview
from app.services.skill_taxonomy import skill_cooccurrence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "public" / "data"


def write_json(filename: str, data):
    path = OUTPUT_DIR / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Written %s", filename)


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_session() as db:
        for market in ("domestic", "international"):
            logger.info("Exporting %s data...", market)

            ind_data = await industry_overview(db, market=market)
            write_json(f"industry-{market}.json", ind_data)

            cooc_data = await skill_cooccurrence(db, top_n=30, min_cooccurrence=2, market=market)
            write_json(f"cooccurrence-{market}.json", cooc_data)

    logger.info("Market-specific export complete!")


if __name__ == "__main__":
    asyncio.run(main())
