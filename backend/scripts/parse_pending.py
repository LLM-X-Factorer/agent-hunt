#!/usr/bin/env python3
"""LLM-parse all jobs.parse_status='pending' rows.

Used after a fresh collector run pulls hundreds/thousands of new postings.
Bounded concurrency + asyncio.wait_for so a single hung upstream call
can't stall the whole batch (same recipe as backfill_quality_labels).

Usage:
    cd backend && .venv/bin/python scripts/parse_pending.py
    cd backend && .venv/bin/python scripts/parse_pending.py --limit 500 --concurrency 20
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.job import Job
from app.services.jd_parser import parse_job_by_id

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

PER_JOB_TIMEOUT = 60


async def parse_one(job_id, sem: asyncio.Semaphore) -> bool:
    async with sem:
        try:
            async with async_session() as db:
                await asyncio.wait_for(parse_job_by_id(db, job_id), timeout=PER_JOB_TIMEOUT)
                return True
        except Exception as e:
            logger.debug("parse fail %s: %s", job_id, str(e)[:160])
            return False


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=15)
    args = parser.parse_args()

    async with async_session() as db:
        stmt = select(Job.id).where(Job.parse_status == "pending")
        if args.limit:
            stmt = stmt.limit(args.limit)
        ids = (await db.execute(stmt)).scalars().all()
    logger.info("parsing %d pending jobs (concurrency=%d)", len(ids), args.concurrency)

    sem = asyncio.Semaphore(args.concurrency)
    ok = failed = 0
    for i in range(0, len(ids), 50):
        batch = ids[i : i + 50]
        results = await asyncio.gather(*[parse_one(jid, sem) for jid in batch])
        for r in results:
            if r: ok += 1
            else: failed += 1
        logger.info("progress: %d/%d (ok=%d failed=%d)", min(i + 50, len(ids)), len(ids), ok, failed)
    logger.info("done — ok=%d failed=%d", ok, failed)


if __name__ == "__main__":
    asyncio.run(main())
