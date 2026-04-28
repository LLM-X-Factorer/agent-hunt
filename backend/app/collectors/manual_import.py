# Manual import service — accepts raw JD data and saves to database.
from __future__ import annotations

import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.schemas.job import JobImportRequest, JobImportResponse


async def import_jobs(
    db: AsyncSession,
    requests: list[JobImportRequest],
) -> JobImportResponse:
    """Import one or more raw JDs.

    On dedup hit (same platform_id + platform_job_id) we **don't skip** —
    we bump last_seen_at + seen_count so #16 can later compute repost_ratio
    (signals like "this listing has been re-published 6 times in 3 months").
    """
    imported_ids: list[uuid.UUID] = []
    re_seen = 0
    now = datetime.datetime.now(datetime.timezone.utc)

    for req in requests:
        existing = await db.execute(
            select(Job).where(
                Job.platform_id == req.platform_id,
                Job.platform_job_id == req.platform_job_id,
            )
        )
        existing_job = existing.scalar_one_or_none()

        if existing_job is not None:
            existing_job.last_seen_at = now
            existing_job.seen_count = (existing_job.seen_count or 1) + 1
            # If a posting reappears after being marked closed, reopen it.
            if existing_job.closed_at is not None:
                existing_job.closed_at = None
            re_seen += 1
            continue

        job = Job(
            platform_id=req.platform_id,
            platform_job_id=req.platform_job_id,
            source_url=req.source_url,
            raw_content=req.raw_content,
            language=req.language,
            parse_status="pending",
            first_seen_at=now,
            last_seen_at=now,
            seen_count=1,
        )
        db.add(job)
        await db.flush()  # populate job.id
        imported_ids.append(job.id)

    await db.commit()

    return JobImportResponse(
        imported=len(imported_ids),
        skipped=re_seen,
        job_ids=imported_ids,
    )
