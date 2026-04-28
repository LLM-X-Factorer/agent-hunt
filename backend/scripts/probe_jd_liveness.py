#!/usr/bin/env python3
"""Probe whether previously-collected JD source URLs are still live.

Issue #16: when a posting 404s / 410s, mark ``closed_at`` so we can later
compute ``avg_close_days`` per company / industry / role.

Default: only probe jobs older than 7 days that haven't been seen in the
last 7 days, and skip ones already marked closed. Limit + concurrency keep
the request rate gentle so we don't trigger anti-scrape.

Usage:
    cd backend && .venv/bin/python scripts/probe_jd_liveness.py
    cd backend && .venv/bin/python scripts/probe_jd_liveness.py --platform boss-zhipin --limit 200
"""
import argparse
import asyncio
import datetime
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from sqlalchemy import select

from app.database import async_session
from app.models.job import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
CLOSED_STATUSES = {404, 410}


async def probe_one(
    client: httpx.AsyncClient,
    job: Job,
    sem: asyncio.Semaphore,
) -> tuple[Job, int | None]:
    if not job.source_url:
        return job, None
    async with sem:
        try:
            resp = await client.get(job.source_url, follow_redirects=False, timeout=15.0)
            return job, resp.status_code
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.debug("probe failed for %s: %s", job.source_url, e)
            return job, None


async def probe(platform: str | None, limit: int, concurrency: int) -> None:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    now = datetime.datetime.now(datetime.timezone.utc)

    async with async_session() as db:
        stmt = select(Job).where(
            Job.closed_at.is_(None),
            Job.source_url.isnot(None),
            Job.last_seen_at < cutoff,
        )
        if platform:
            stmt = stmt.where(Job.platform_id == platform)
        stmt = stmt.limit(limit)
        jobs = (await db.execute(stmt)).scalars().all()
        logger.info("probing %d jobs (platform=%s)", len(jobs), platform or "all")

        sem = asyncio.Semaphore(concurrency)
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}) as client:
            results = await asyncio.gather(*[probe_one(client, j, sem) for j in jobs])

        closed = 0
        for job, status in results:
            if status in CLOSED_STATUSES:
                job.closed_at = now
                closed += 1
        await db.commit()
        logger.info("marked %d jobs closed", closed)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", default=None, help="restrict to one platform_id")
    parser.add_argument("--limit", type=int, default=300, help="max URLs to probe per run")
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()
    await probe(args.platform, args.limit, args.concurrency)


if __name__ == "__main__":
    asyncio.run(main())
