#!/usr/bin/env python3
"""Export real-salary-vs-JD-asking comparison (#15).

Aggregates SalaryReport (爆料) data per (company, role) and per (role)
into ``frontend/public/data/roles-real-salary.json``. Where we have
matching role-level Job stats, computes a ``gap_pct`` so aijobfit can
show "JD 报 30k，实际到手 24k" deltas.

Usage:
    cd backend && .venv/bin/python scripts/export_real_salary.py
"""
import asyncio
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.job import Job
from app.models.salary_report import SalaryReport
from scripts.analyze_roles import (
    DOMESTIC_ROLES,
    INTERNATIONAL_ROLES,
    classify_job,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "roles-real-salary.json"
)
RULES_BY_MARKET = {"domestic": DOMESTIC_ROLES, "international": INTERNATIONAL_ROLES}

# Map levels.fyi job_family slugs onto our internal roleIds (international rules).
JOB_FAMILY_TO_ROLE_INTL = {
    "Software Engineer": "sde",
    "Machine Learning Engineer": "ml_engineer",
    "Data Scientist": "data",
    "Product Manager": "product_manager",
    "Solutions Architect": "architect",
    "Hardware Engineer": "sde",
}
# Domestic role taxonomy is AI-focused (DOMESTIC_ROLES). Generic SE / Hardware
# at CN big-tech offices isn't an AI role, so skip those — only map the
# AI-adjacent families. Otherwise we'd inflate ai_engineer with non-AI SDE samples.
JOB_FAMILY_TO_ROLE_DOMESTIC = {
    "Machine Learning Engineer": "algorithm",
    "Research Scientist": "algorithm",
    "Data Scientist": "data",
    "Product Manager": "product_manager",
}


def map_role(job_family: str | None, market: str | None) -> str | None:
    if not job_family:
        return None
    if market == "domestic":
        return JOB_FAMILY_TO_ROLE_DOMESTIC.get(job_family)
    return JOB_FAMILY_TO_ROLE_INTL.get(job_family)


def percentiles(values: list[int]) -> dict | None:
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    return {
        "p25": s[n // 4],
        "p50": int(median(s)),
        "p75": s[(n * 3) // 4],
        "min": s[0],
        "max": s[-1],
        "sample_size": n,
    }


def gap_pct(jd_median: int | None, real_median: int | None) -> float | None:
    if not jd_median or not real_median:
        return None
    return round((real_median - jd_median) / jd_median * 100, 1)


async def main():
    async with async_session() as db:
        reports = (await db.execute(select(SalaryReport))).scalars().all()
        jobs = (await db.execute(
            select(Job).where(Job.parse_status == "parsed", Job.title.isnot(None))
        )).scalars().all()
    logger.info("loaded %d salary reports / %d parsed jobs", len(reports), len(jobs))

    # Bucket reports by (market, roleId). levels.fyi now includes CN big-tech;
    # SE samples there don't map to the AI-only DOMESTIC taxonomy and are skipped
    # at the by_role level (they still appear in by_company_role below).
    by_role_reports: dict[tuple[str, str], list[SalaryReport]] = defaultdict(list)
    for r in reports:
        if not r.total_comp_rmb_monthly:
            continue
        role_id = map_role(r.job_family, r.market)
        if not role_id:
            continue
        by_role_reports[(r.market or "international", role_id)].append(r)

    # Bucket jobs by (market, roleId) for the gap comparison.
    by_role_jd_salaries: dict[tuple[str, str], list[int]] = defaultdict(list)
    for j in jobs:
        rules = RULES_BY_MARKET.get(j.market or "")
        if not rules:
            continue
        rid = classify_job(j.title or "", rules)
        if rid in ("_noise", "other"):
            continue
        sal_mid = j.salary_mid_cny_monthly
        if sal_mid is not None:
            by_role_jd_salaries[(j.market, rid)].append(int(sal_mid))

    # Per-(market, role) summary.
    role_rows: list[dict] = []
    for (market, rid), rep_list in sorted(
        by_role_reports.items(), key=lambda kv: -len(kv[1])
    ):
        real_tcs = [r.total_comp_rmb_monthly for r in rep_list]
        bases = [r.base_salary for r in rep_list if r.base_salary]
        stocks = [r.stock_grant_value for r in rep_list if r.stock_grant_value]
        jd_salaries = by_role_jd_salaries.get((market, rid), [])

        real_p = percentiles(real_tcs)
        jd_p = percentiles(jd_salaries)

        role_rows.append({
            "market": market,
            "roleId": rid,
            "real_tc_rmb_monthly": real_p,
            "real_base_yearly": percentiles(bases),
            "real_stock_yearly": percentiles(stocks),
            "jd_asking_rmb_monthly": jd_p,
            "gap_pct": gap_pct(
                jd_p["p50"] if jd_p else None,
                real_p["p50"] if real_p else None,
            ),
            "sample_companies": sorted({r.company for r in rep_list})[:8],
        })

    # Per-(company, role) breakdown for the most-reported pairs.
    by_company_role: dict[tuple[str, str], list[SalaryReport]] = defaultdict(list)
    for r in reports:
        if r.total_comp_rmb_monthly and r.company and r.job_family:
            by_company_role[(r.company, r.job_family)].append(r)
    company_rows = []
    for (company, jf), rep_list in sorted(
        by_company_role.items(), key=lambda kv: -len(kv[1])
    )[:50]:
        tcs = [r.total_comp_rmb_monthly for r in rep_list]
        bases = [r.base_salary for r in rep_list if r.base_salary]
        company_rows.append({
            "company": company,
            "job_family": jf,
            "tc_rmb_monthly": percentiles(tcs),
            "base_usd_yearly": percentiles(bases),
            "level_breakdown": [
                {"level": lvl, "count": cnt}
                for lvl, cnt in sorted(
                    {(r.level, sum(1 for x in rep_list if x.level == r.level)) for r in rep_list},
                    key=lambda x: -x[1],
                )[:8]
            ],
        })

    output = {
        "by_role": role_rows,
        "by_company_role": company_rows,
        "sources": sorted({r.source for r in reports}),
        "total_reports": len(reports),
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
