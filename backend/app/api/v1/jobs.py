# Job API endpoints — import, list, detail, parse, and collect.
from __future__ import annotations

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.manual_import import import_jobs
from app.collectors.registry import get_collector
from app.database import get_db
from app.models.job import Job
from app.schemas.job import (
    CollectRequest,
    CollectResponse,
    JobBrief,
    JobDetail,
    JobImportBatchRequest,
    JobImportRequest,
    JobImportResponse,
    JobListResponse,
)
from app.services.jd_parser import parse_job_by_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/import", response_model=JobImportResponse)
async def import_single(req: JobImportRequest, db: AsyncSession = Depends(get_db)):
    """Import a single raw JD."""
    return await import_jobs(db, [req])


@router.post("/import/batch", response_model=JobImportResponse)
async def import_batch(req: JobImportBatchRequest, db: AsyncSession = Depends(get_db)):
    """Import multiple raw JDs at once (max 100)."""
    return await import_jobs(db, req.jobs)


@router.post("/collect", response_model=CollectResponse)
async def collect_jobs(req: CollectRequest, db: AsyncSession = Depends(get_db)):
    """Collect jobs from a platform, import to DB, and optionally auto-parse."""
    try:
        collector = get_collector(req.platform_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    collected_jobs = await collector.collect(req.keyword, req.max_pages)
    if not collected_jobs:
        return CollectResponse(
            collected=0, imported=0, skipped=0, parsed=0, failed=0, job_ids=[]
        )

    import_result = await import_jobs(db, collected_jobs)

    parsed = 0
    failed = 0
    if req.auto_parse and import_result.job_ids:
        for job_id in import_result.job_ids:
            try:
                job = await parse_job_by_id(db, job_id)
                if job.parse_status == "parsed":
                    parsed += 1
                else:
                    failed += 1
            except Exception:
                logger.exception("Parse failed for job %s", job_id)
                failed += 1
            await asyncio.sleep(1)  # Gemini API rate limit

    return CollectResponse(
        collected=len(collected_jobs),
        imported=import_result.imported,
        skipped=import_result.skipped,
        parsed=parsed,
        failed=failed,
        job_ids=import_result.job_ids,
    )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform_id: str | None = None,
    market: str | None = None,
    parse_status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List jobs with optional filtering and pagination."""
    query = select(Job)
    count_query = select(func.count(Job.id))

    if platform_id:
        query = query.where(Job.platform_id == platform_id)
        count_query = count_query.where(Job.platform_id == platform_id)
    if market:
        query = query.where(Job.market == market)
        count_query = count_query.where(Job.market == market)
    if parse_status:
        query = query.where(Job.parse_status == parse_status)
        count_query = count_query.where(Job.parse_status == parse_status)

    total = (await db.execute(count_query)).scalar_one()

    query = query.order_by(Job.collected_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    jobs = result.scalars().all()

    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[JobBrief.model_validate(j) for j in jobs],
    )


@router.get("/{job_id}", response_model=JobDetail)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get full job detail by ID."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetail.model_validate(job)


@router.post("/parse/batch")
async def batch_parse(
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Parse all pending jobs in batch. Returns progress counts."""
    result = await db.execute(
        select(Job.id).where(Job.parse_status == "pending").limit(limit)
    )
    pending_ids = [row[0] for row in result.all()]

    if not pending_ids:
        return {"total_pending": 0, "parsed": 0, "failed": 0}

    parsed = 0
    failed = 0
    for job_id in pending_ids:
        try:
            job = await parse_job_by_id(db, job_id)
            if job.parse_status == "parsed":
                parsed += 1
            else:
                failed += 1
        except Exception:
            logger.exception("Batch parse failed for %s", job_id)
            failed += 1
        await asyncio.sleep(1.5)

    return {
        "total_pending": len(pending_ids),
        "parsed": parsed,
        "failed": failed,
    }


@router.post("/{job_id}/parse", response_model=JobDetail)
async def trigger_parse(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Trigger LLM parsing for a specific job."""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job = await parse_job_by_id(db, job_id)
    return JobDetail.model_validate(job)
