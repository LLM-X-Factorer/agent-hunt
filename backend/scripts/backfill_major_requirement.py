#!/usr/bin/env python3
"""Backfill major_requirement on already-parsed jobs (#33 / v0.12 A1).

Narrow prompt — only extracts the majors array, doesn't re-derive
salary / skills / role_type / etc. Keeps cost low (~$1-2 for 8k jobs)
and avoids regressing curated fields.

Usage:
    cd backend && .venv/bin/python scripts/backfill_major_requirement.py
    cd backend && .venv/bin/python scripts/backfill_major_requirement.py --limit 5
    cd backend && .venv/bin/python scripts/backfill_major_requirement.py --limit 100 --concurrency 10
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
from app.schemas.job import MajorRequirement
from app.services.llm import llm_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAJOR_PROMPT = """\
你是 JD 专业要求抽取引擎。读完原始 JD 文本，只输出该岗位明确要求或优先的学术专业方向。

规则：
1. 仅包含 JD 中明确出现的专业要求（"X 专业"、"X 相关专业"、"Major in X"、"X background preferred"）
2. 保留 JD 原文出现的中文 / 英文名，不要翻译，不要合并同义词
   - "计算机科学" 和 "计算机科学与技术" 都保留各自原文
   - "Computer Science" 和 "CS" 都保留各自原文
3. 学历词（本科及以上 / Bachelor's / Master's / PhD）不要进这个字段
4. 不要从职位名称推断专业（"算法工程师" 不自动等于"计算机相关"）
5. 专业不限 / 无明确专业要求 / 没提到专业 → 空数组 []

示例输入: "本科及以上学历，计算机、电子工程、数学等相关专业"
示例输出: {"majors": ["计算机", "电子工程", "数学"]}

示例输入: "Bachelor's degree in Computer Science, Statistics, or related quantitative field"
示例输出: {"majors": ["Computer Science", "Statistics"]}

示例输入: "5 年以上互联网行业经验" (没提专业)
示例输出: {"majors": []}

严格输出 JSON：
{
  "majors": ["string"]
}"""


PER_JOB_TIMEOUT = 30  # seconds


async def label_one(
    job: Job,
    sem: asyncio.Semaphore,
) -> tuple[Job, MajorRequirement | None, str | None]:
    async with sem:
        try:
            data = await asyncio.wait_for(
                llm_json(
                    job.raw_content,
                    system=MAJOR_PROMPT,
                    temperature=0.1,
                    # deepseek-chat (direct API) is non-reasoning, ~50-200 output
                    # tokens for this prompt. 500 leaves headroom without bloat.
                    max_tokens=500,
                ),
                timeout=PER_JOB_TIMEOUT,
            )
            return job, MajorRequirement(**data), None
        except asyncio.TimeoutError:
            return job, None, f"timeout after {PER_JOB_TIMEOUT}s"
        except Exception as e:
            return job, None, str(e)[:200]


async def backfill(limit: int | None, concurrency: int) -> None:
    async with async_session() as db:
        stmt = select(Job).where(
            Job.parse_status == "parsed",
            Job.major_requirement.is_(None),
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
            for job, mr, err in results:
                if mr is None:
                    failed += 1
                    logger.warning("failed %s: %s", job.id, err)
                    continue
                job.major_requirement = mr.majors
                ok += 1
            await db.commit()
            logger.info(
                "progress: %d / %d (ok=%d failed=%d)",
                min(i + batch_size, len(jobs)),
                len(jobs),
                ok,
                failed,
            )

        logger.info("done — ok=%d failed=%d", ok, failed)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()
    await backfill(args.limit, args.concurrency)


if __name__ == "__main__":
    asyncio.run(main())
