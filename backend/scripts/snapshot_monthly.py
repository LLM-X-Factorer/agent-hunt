#!/usr/bin/env python3
"""Aggregate parsed jobs into monthly snapshots.

Issue #13: writes (skill_id, market, month) / (role_id, market, month) /
(industry, market, month) rows to the snapshot tables. Idempotent — a re-run
on the same month overwrites that month's rows; older months are untouched.

Doubles as historical backfill: with no extra args it walks every month
present in the data and writes them all (uses ``Job.collected_at``).

Usage:
    cd backend && .venv/bin/python scripts/snapshot_monthly.py
    cd backend && .venv/bin/python scripts/snapshot_monthly.py --month 2026-04
"""
import argparse
import asyncio
import datetime
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.models.job import Job
from app.models.snapshot import (
    IndustryMonthlySnapshot,
    RoleMonthlySnapshot,
    SkillMonthlySnapshot,
)
from app.services.skill_extractor import extractor

# Reuse the classification rules from analyze_roles.
from scripts.analyze_roles import (
    DOMESTIC_ROLES,
    INTERNATIONAL_ROLES,
    classify_job,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MARKETS = ("domestic", "international")
RULES_BY_MARKET = {"domestic": DOMESTIC_ROLES, "international": INTERNATIONAL_ROLES}


def month_floor(d: datetime.datetime) -> datetime.date:
    return datetime.date(d.year, d.month, 1)


def salary_mid(j: Job) -> int | None:
    s = j.salary_mid_cny_monthly
    return int(s) if s is not None else None


def aggregate_salary(salaries: list[int]) -> tuple[int | None, int | None]:
    if not salaries:
        return None, None
    return int(median(salaries)), int(sum(salaries) / len(salaries))


async def upsert_skill_rows(db: AsyncSession, rows: list[dict]) -> None:
    if not rows:
        return
    stmt = insert(SkillMonthlySnapshot).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="pk_skill_monthly",
        set_={
            "job_count": stmt.excluded.job_count,
            "salary_median": stmt.excluded.salary_median,
            "salary_avg": stmt.excluded.salary_avg,
        },
    )
    await db.execute(stmt)


async def upsert_role_rows(db: AsyncSession, rows: list[dict]) -> None:
    if not rows:
        return
    stmt = insert(RoleMonthlySnapshot).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="pk_role_monthly",
        set_={
            "job_count": stmt.excluded.job_count,
            "salary_median": stmt.excluded.salary_median,
            "salary_avg": stmt.excluded.salary_avg,
            "top_skills": stmt.excluded.top_skills,
        },
    )
    await db.execute(stmt)


async def upsert_industry_rows(db: AsyncSession, rows: list[dict]) -> None:
    if not rows:
        return
    stmt = insert(IndustryMonthlySnapshot).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="pk_industry_monthly",
        set_={
            "job_count": stmt.excluded.job_count,
            "salary_median": stmt.excluded.salary_median,
            "salary_avg": stmt.excluded.salary_avg,
        },
    )
    await db.execute(stmt)


async def snapshot(target_month: datetime.date | None = None) -> None:
    async with async_session() as db:
        result = await db.execute(
            select(Job).where(
                Job.parse_status == "parsed",
                Job.market.in_(MARKETS),
                Job.collected_at.isnot(None),
            )
        )
        jobs = result.scalars().all()
        logger.info("loaded %d parsed jobs", len(jobs))

        # Bucket by (market, month).
        buckets: dict[tuple[str, datetime.date], list[Job]] = defaultdict(list)
        for j in jobs:
            m = month_floor(j.collected_at)
            if target_month and m != target_month:
                continue
            buckets[(j.market, m)].append(j)

        if not buckets:
            logger.warning("no jobs match the target window")
            return

        skill_rows: list[dict] = []
        role_rows: list[dict] = []
        industry_rows: list[dict] = []

        for (market, month), bucket_jobs in sorted(buckets.items()):
            rules = RULES_BY_MARKET[market]

            # Skills.
            skill_jobs: dict[str, list[Job]] = defaultdict(list)
            for j in bucket_jobs:
                seen: set[str] = set()
                for raw in (j.required_skills or []) + (j.preferred_skills or []):
                    sid = extractor.normalize(raw)
                    if sid and sid not in seen:
                        seen.add(sid)
                        skill_jobs[sid].append(j)
            for sid, sjobs in skill_jobs.items():
                sals = [s for s in (salary_mid(j) for j in sjobs) if s]
                med, avg = aggregate_salary(sals)
                skill_rows.append({
                    "skill_id": sid,
                    "market": market,
                    "month": month,
                    "job_count": len(sjobs),
                    "salary_median": med,
                    "salary_avg": avg,
                })

            # Roles.
            role_groups: dict[str, list[Job]] = defaultdict(list)
            for j in bucket_jobs:
                rid = classify_job(j.title or "", rules)
                if rid in ("_noise", "other"):
                    continue
                role_groups[rid].append(j)
            for rid, rjobs in role_groups.items():
                sals = [s for s in (salary_mid(j) for j in rjobs) if s]
                med, avg = aggregate_salary(sals)
                top_skills_counter: Counter = Counter()
                for j in rjobs:
                    for raw in (j.required_skills or []):
                        sid = extractor.normalize(raw)
                        if sid:
                            top_skills_counter[sid] += 1
                role_rows.append({
                    "role_id": rid,
                    "market": market,
                    "month": month,
                    "job_count": len(rjobs),
                    "salary_median": med,
                    "salary_avg": avg,
                    "top_skills": [
                        {"skill_id": s, "count": c}
                        for s, c in top_skills_counter.most_common(10)
                    ],
                })

            # Industries.
            ind_groups: dict[str, list[Job]] = defaultdict(list)
            for j in bucket_jobs:
                if j.industry:
                    ind_groups[j.industry].append(j)
            for industry, ijobs in ind_groups.items():
                sals = [s for s in (salary_mid(j) for j in ijobs) if s]
                med, avg = aggregate_salary(sals)
                industry_rows.append({
                    "industry": industry,
                    "market": market,
                    "month": month,
                    "job_count": len(ijobs),
                    "salary_median": med,
                    "salary_avg": avg,
                })

            logger.info(
                "%s %s — %d jobs / %d skills / %d roles / %d industries",
                market, month, len(bucket_jobs),
                len(skill_jobs), len(role_groups), len(ind_groups),
            )

        await upsert_skill_rows(db, skill_rows)
        await upsert_role_rows(db, role_rows)
        await upsert_industry_rows(db, industry_rows)
        await db.commit()

        logger.info(
            "wrote %d skill rows / %d role rows / %d industry rows",
            len(skill_rows), len(role_rows), len(industry_rows),
        )


def parse_month(value: str) -> datetime.date:
    return datetime.datetime.strptime(value + "-01", "%Y-%m-%d").date()


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--month",
        type=parse_month,
        default=None,
        help="restrict to a single month (YYYY-MM); default = all months in data",
    )
    args = parser.parse_args()
    await snapshot(args.month)


if __name__ == "__main__":
    asyncio.run(main())
