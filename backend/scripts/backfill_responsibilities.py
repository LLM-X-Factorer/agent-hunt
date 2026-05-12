#!/usr/bin/env python3
"""Backfill responsibilities on domestic JDs (v0.12 B1 follow-up).

Why this exists: post-B1 diagnostics showed domestic responsibilities
coverage was 3.9% (3786 jobs / 146 with content), driven by:
  - 腾讯 1557 jobs collected via rule-based backfill_tencent_metadata.py
    that never ran the LLM JD parser — responsibilities is NULL
  - Boss/Liepin domestic LLM parse extracted on average 0.28 items/JD,
    much sparser than intl (8.87 items/JD)

Narrow prompt — only fills responsibilities, doesn't touch other fields.
Keeps cost minimal (~$0.30 for ~3640 jobs at DeepSeek prices) and avoids
regressing curated salary / skills / role_type.

Usage:
    cd backend && .venv/bin/python scripts/backfill_responsibilities.py --limit 5
    cd backend && .venv/bin/python scripts/backfill_responsibilities.py
    cd backend && .venv/bin/python scripts/backfill_responsibilities.py --concurrency 10
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, or_, select

from app.database import async_session
from app.models.job import Job
from app.schemas.job import ResponsibilitiesOnly
from app.services.llm import llm_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

RESP_PROMPT = """\
你是 JD 工作职责抽取引擎。读完原始 JD 文本，只输出该岗位的具体工作职责短句。

规则：
1. 优先从"工作职责"/"岗位职责"/"工作内容"/"Responsibilities"/"What you'll do"/"Job Description"
   段落抽取；如果没有显式段落，从描述性文字（"你将..." / "You will..." / "负责..." / 编号
   列表 "1. 2. 3."）中提取
2. 每条保留 JD 原文一句话或一个 bullet，不要总结、不要翻译、不要合并
3. 保留原文动词起头的具体动作（如"参与构建 RAG 系统" / "Lead the design of..."）
4. 跳过纯背景介绍 / 公司宣传 / 团队规模 / 福利
5. 跳过任职要求 / 技能要求（"熟悉 X" / "Required: X experience" / "本科及以上"）
6. 数量 0-10 条。如果 JD 完全没写职责描述（如只列要求），返回空数组

示例输入：
"业务经营管理部-AI Agent 研发工程师
事业群: CSIG / 技术 / 腾讯云
位置: 深圳
经验: 1年以上

1.参与腾讯云 AI Agent 开发工作，优化 AI 智能体的使用体验，持续提升用户的使用效率；
2.参与AI Agent 记忆机制、任务编排等能力的探索；
3.参与传统系统Skill化通用方案的设计和落地。"

示例输出：
{"responsibilities": [
  "参与腾讯云 AI Agent 开发工作，优化 AI 智能体的使用体验，持续提升用户的使用效率",
  "参与AI Agent 记忆机制、任务编排等能力的探索",
  "参与传统系统Skill化通用方案的设计和落地"
]}

严格输出 JSON：
{"responsibilities": ["string"]}"""


PER_JOB_TIMEOUT = 30  # seconds


async def label_one(
    job: Job,
    sem: asyncio.Semaphore,
) -> tuple[Job, ResponsibilitiesOnly | None, str | None]:
    async with sem:
        try:
            data = await asyncio.wait_for(
                llm_json(
                    job.raw_content,
                    system=RESP_PROMPT,
                    temperature=0.1,
                    max_tokens=1000,
                ),
                timeout=PER_JOB_TIMEOUT,
            )
            return job, ResponsibilitiesOnly(**data), None
        except asyncio.TimeoutError:
            return job, None, f"timeout after {PER_JOB_TIMEOUT}s"
        except Exception as e:
            return job, None, str(e)[:200]


async def backfill(
    limit: int | None,
    concurrency: int,
    market: str,
) -> None:
    async with async_session() as db:
        stmt = (
            select(Job)
            .where(
                Job.market == market,
                Job.parse_status == "parsed",
                or_(
                    Job.responsibilities.is_(None),
                    func.cardinality(Job.responsibilities) == 0,
                ),
            )
            .order_by(Job.id)
        )
        if limit:
            stmt = stmt.limit(limit)
        jobs = (await db.execute(stmt)).scalars().all()
        logger.info(
            "backfilling %d %s jobs (concurrency=%d)", len(jobs), market, concurrency
        )

        sem = asyncio.Semaphore(concurrency)
        ok = failed = empty = 0
        batch_size = 50
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]
            results = await asyncio.gather(*[label_one(j, sem) for j in batch])
            for job, ro, err in results:
                if ro is None:
                    failed += 1
                    logger.warning("failed %s: %s", job.id, err)
                    continue
                # Only write — preserve all other fields. Even an empty array
                # is meaningful here: it says "LLM looked and JD had no
                # responsibilities section", which differs from the NULL
                # placeholder.
                job.responsibilities = ro.responsibilities
                if not ro.responsibilities:
                    empty += 1
                ok += 1
            await db.commit()
            logger.info(
                "progress: %d / %d (ok=%d empty=%d failed=%d)",
                min(i + batch_size, len(jobs)),
                len(jobs),
                ok,
                empty,
                failed,
            )

        logger.info(
            "done — ok=%d (of which %d had no responsibilities text) failed=%d",
            ok,
            empty,
            failed,
        )


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument(
        "--market",
        default="domestic",
        choices=["domestic", "international"],
        help="default domestic — intl already has 54.6%% coverage from parse",
    )
    args = parser.parse_args()
    await backfill(args.limit, args.concurrency, args.market)


if __name__ == "__main__":
    asyncio.run(main())
