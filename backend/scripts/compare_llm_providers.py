#!/usr/bin/env python3
"""Compare LLM providers (MiniMax M2.7 / Kimi K2.6) for JD parsing quality.

Pulls N already-parsed jobs from the DB, re-parses them with each provider,
and writes a side-by-side JSON for manual review.

Usage:
    cd backend && .venv/bin/python scripts/compare_llm_providers.py [--samples 5]
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# Allow importing app.* when run from backend/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.job import Job
from app.services.jd_parser import SYSTEM_PROMPT


PROVIDERS = {
    "minimax-m2.7": "minimax/minimax-m2.7",
    "kimi-k2.6": "moonshotai/kimi-k2.6",
}


async def parse_with_openrouter(client: AsyncOpenAI, model: str, jd_text: str) -> dict:
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": jd_text},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--concurrency", type=int, default=3,
                        help="Concurrent requests per provider")
    args = parser.parse_args()

    api_key = getattr(settings, "openrouter_api_key", None) or __import__("os").environ.get("AH_OPENROUTER_API_KEY")
    if not api_key:
        sys.exit("AH_OPENROUTER_API_KEY not set in .env")

    engine = create_async_engine(settings.database_url)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        result = await db.execute(
            select(Job)
            .where(Job.parse_status == "parsed", Job.raw_content.isnot(None))
            .limit(args.samples)
        )
        jobs = list(result.scalars().all())

    if not jobs:
        sys.exit("No parsed jobs found in DB")

    print(f"Loaded {len(jobs)} sample JDs from DB\n")

    client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    results: dict[str, dict] = {}
    for name, model in PROVIDERS.items():
        print(f"=== {name} ({model}) ===")
        sem = asyncio.Semaphore(args.concurrency)

        async def run_one(idx: int, job: Job):
            async with sem:
                t0 = time.time()
                try:
                    parsed = await parse_with_openrouter(client, model, job.raw_content)
                    dt = time.time() - t0
                    print(f"  [{idx}/{len(jobs)}] OK in {dt:.2f}s — {parsed.get('title', '?')[:40]}")
                    return {
                        "job_id": str(job.id),
                        "title_orig": job.title,
                        "title_new": parsed.get("title"),
                        "industry_orig": job.industry,
                        "industry_new": parsed.get("industry"),
                        "salary_orig": [job.salary_min, job.salary_max],
                        "salary_new": [parsed.get("salary_min_rmb"), parsed.get("salary_max_rmb")],
                        "skills_orig": (job.required_skills or [])[:8],
                        "skills_new": (parsed.get("required_skills") or [])[:8],
                        "education_orig": job.education,
                        "education_new": parsed.get("education"),
                        "duration_s": round(dt, 2),
                    }
                except Exception as e:
                    dt = time.time() - t0
                    print(f"  [{idx}/{len(jobs)}] FAILED in {dt:.2f}s: {str(e)[:150]}")
                    return {"job_id": str(job.id), "error": str(e)[:300], "duration_s": round(dt, 2)}

        t_start = time.time()
        per_job = await asyncio.gather(*[run_one(i + 1, j) for i, j in enumerate(jobs)])
        wall_time = time.time() - t_start

        ok = [r for r in per_job if "error" not in r]
        results[name] = {
            "model": model,
            "wall_time_s": round(wall_time, 2),
            "avg_per_job_s": round(sum(r["duration_s"] for r in per_job) / len(per_job), 2),
            "success": len(ok),
            "failed": len(per_job) - len(ok),
            "per_job": per_job,
        }
        print()

    out_path = Path(__file__).resolve().parent.parent.parent / "tmp_llm_comparison.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))

    print("=== Summary ===")
    print(f"{'Provider':<20} {'Wall':<10} {'Avg/job':<10} {'OK':<5} {'Fail':<5}")
    for name, data in results.items():
        print(f"{name:<20} {data['wall_time_s']:<10} {data['avg_per_job_s']:<10} "
              f"{data['success']:<5} {data['failed']:<5}")
    print(f"\nFull results: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
