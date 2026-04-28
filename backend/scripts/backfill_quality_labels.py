#!/usr/bin/env python3
"""Backfill the 5 new fields on already-parsed jobs (#10 + #11).

Cheap to re-run: a job is only re-asked if any of the new fields are still
NULL. Keeps prompt small (only the 5 new fields, no salary / skills / etc.)
so we don't risk regressing existing fields by re-parsing them.

Usage:
    cd backend && .venv/bin/python scripts/backfill_quality_labels.py
    cd backend && .venv/bin/python scripts/backfill_quality_labels.py --limit 100 --concurrency 10
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import or_, select

from app.database import async_session
from app.models.job import Job
from app.schemas.job import QualityLabels
from app.services.llm import llm_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

QUALITY_PROMPT = """\
你是 JD 标签补打引擎。读完原始 JD 文本，只输出以下 5 个字段的 JSON。

字段定义：

1. experience_requirement — 经验要求分桶，必须从以下选择：
   "fresh"(应届/在校/0 经验), "0-1y", "1-3y", "3-5y", "5y+", null
2. internship_friendly — 是否接受实习生 / 在校生（true/false/null）
3. is_campus — 是否明确标注"校招/校园招聘/应届生招聘"（true/false/null）
4. role_type — 岗位类型：
   - "ai_native": 算法/ML/LLM 工程师、AI 产品、AI Agent、AI 销售等以 AI 为主的岗
   - "ai_augmented_traditional": 主体是传统专业（电气/医疗/金融/制造/会计/法律/教育...）但要求 AI 技能
5. base_profession — 仅当 role_type = "ai_augmented_traditional" 时填，
   传统岗位名，例如"电气工程师"、"医生"、"会计"、"金融分析师"、"机械工程师"、"教师"
   ai_native 时填 null

严格输出以下 JSON，不要添加任何额外文字：
{
  "experience_requirement": "fresh | 0-1y | 1-3y | 3-5y | 5y+ | null",
  "internship_friendly": "bool | null",
  "is_campus": "bool | null",
  "role_type": "ai_native | ai_augmented_traditional | null",
  "base_profession": "string | null"
}"""


async def label_one(
    job: Job,
    sem: asyncio.Semaphore,
) -> tuple[Job, QualityLabels | None, str | None]:
    async with sem:
        try:
            data = await llm_json(
                job.raw_content,
                system=QUALITY_PROMPT,
                temperature=0.1,
            )
            return job, QualityLabels(**data), None
        except Exception as e:
            return job, None, str(e)[:200]


async def backfill(limit: int | None, concurrency: int) -> None:
    async with async_session() as db:
        stmt = select(Job).where(
            Job.parse_status == "parsed",
            or_(
                Job.role_type.is_(None),
                Job.experience_requirement.is_(None),
            ),
        )
        if limit:
            stmt = stmt.limit(limit)
        jobs = (await db.execute(stmt)).scalars().all()
        logger.info("backfilling %d jobs (concurrency=%d)", len(jobs), concurrency)

        sem = asyncio.Semaphore(concurrency)
        ok = failed = 0
        batch_size = 50
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]
            results = await asyncio.gather(*[label_one(j, sem) for j in batch])
            for job, labels, err in results:
                if labels is None:
                    failed += 1
                    logger.warning("failed %s: %s", job.id, err)
                    continue
                job.experience_requirement = labels.experience_requirement
                job.internship_friendly = labels.internship_friendly
                job.is_campus = labels.is_campus
                job.role_type = labels.role_type
                job.base_profession = labels.base_profession
                ok += 1
            await db.commit()
            logger.info("progress: %d / %d (ok=%d failed=%d)", min(i + batch_size, len(jobs)), len(jobs), ok, failed)

        logger.info("done — ok=%d failed=%d", ok, failed)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()
    await backfill(args.limit, args.concurrency)


if __name__ == "__main__":
    asyncio.run(main())
