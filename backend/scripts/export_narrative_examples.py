#!/usr/bin/env python3
"""Export real JD examples for the 5 narrative-handbook pages.

Each page needs concrete JD samples (title + company + salary + skills)
to convince skeptical readers. Numbers + bar charts alone aren't enough.

Output: ``frontend/public/data/narrative-examples.json`` with:
  - p1_p2_industries: per-industry examples (domestic ai_augmented_traditional)
  - p3_vendor_examples: per-vendor × category examples for OpenAI/Anthropic
  - p4_cross_market_examples: 4 buckets (market × role_type) sample JDs

Usage:
    cd backend && .venv/bin/python scripts/export_narrative_examples.py
"""
import asyncio
import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.job import Job
from app.services.currency import midpoint_cny_monthly, to_cny_monthly

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "narrative-examples.json"
)

# Reuse the same patterns as export_vendor_title_breakdown.py.
VENDOR_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("fde", re.compile(r"\bforward deployed\b", re.IGNORECASE)),
    ("solutions", re.compile(r"\b(solutions engineer|solution architect|solutions architect)\b", re.IGNORECASE)),
    ("deploy", re.compile(r"\b(deployment|implementation|onboarding)\b", re.IGNORECASE)),
    ("applied", re.compile(r"\bapplied (engineer|engineering|ai)\b", re.IGNORECASE)),
    ("customer", re.compile(r"\b(customer success|customer engineer|technical success)\b", re.IGNORECASE)),
]


def categorize_vendor(title: str) -> str:
    for cat, pattern in VENDOR_PATTERNS:
        if pattern.search(title):
            return cat
    return "core"


def job_to_example(j: Job, max_resp: int = 3) -> dict:
    """Distill a Job row to a render-friendly example."""
    sal_min_cny = to_cny_monthly(j.salary_min, j.salary_currency)
    sal_max_cny = to_cny_monthly(j.salary_max, j.salary_currency)
    return {
        "title": j.title,
        "company": j.company_name,
        "location": j.location,
        "salary_min": j.salary_min,
        "salary_max": j.salary_max,
        "salary_currency": j.salary_currency,
        # CNY/month equivalent — already FX-converted, so frontend can compare
        # across markets without re-doing the conversion.
        "salary_min_cny_monthly": int(sal_min_cny) if sal_min_cny else None,
        "salary_max_cny_monthly": int(sal_max_cny) if sal_max_cny else None,
        "experience_requirement": j.experience_requirement,
        "education": j.education,
        "work_mode": j.work_mode,
        "required_skills": (j.required_skills or [])[:8],
        "preferred_skills": (j.preferred_skills or [])[:6],
        "responsibilities": [r for r in (j.responsibilities or [])[:max_resp] if r],
        "base_profession": j.base_profession,
        "platform_id": j.platform_id,
        "source_url": j.source_url,
    }


# Some Anthropic/OpenAI jobs got parsed at *annual* CNY scale (e.g. 2.4M/月).
# Anything above this is a parser bug, not a real monthly salary.
SALARY_SANITY_CAP = 500_000  # CNY/月


def has_sane_salary(j: Job) -> bool:
    if not (j.salary_min and j.salary_max):
        return False
    return j.salary_min < SALARY_SANITY_CAP and j.salary_max < SALARY_SANITY_CAP


def example_score(j: Job) -> tuple:
    """Sort key: rich example first (resp + skills + URL + salary present)."""
    return (
        bool(j.responsibilities),
        len(j.required_skills or []) + len(j.preferred_skills or []),
        bool(j.source_url),
        bool(j.salary_min),
    )


async def main():
    async with async_session() as db:
        all_jobs = (await db.execute(
            select(Job).where(Job.parse_status == "parsed", Job.title.isnot(None))
        )).scalars().all()
    logger.info("loaded %d parsed jobs", len(all_jobs))

    # ---- P1 / P2: domestic ai_augmented_traditional, by industry ----
    by_industry: dict[str, list[Job]] = defaultdict(list)
    for j in all_jobs:
        if (
            j.market == "domestic"
            and j.role_type == "ai_augmented_traditional"
            and j.industry
            and has_sane_salary(j)
        ):
            by_industry[j.industry].append(j)

    p1p2 = {}
    for industry, jobs in by_industry.items():
        # Pick "typical" examples — within IQR of currency-normalized salary,
        # so the showcase matches the narrative median, not wild outliers.
        with_mid = [(j, midpoint_cny_monthly(j.salary_min, j.salary_max, j.salary_currency)) for j in jobs]
        with_mid = [(j, m) for j, m in with_mid if m is not None]
        if not with_mid:
            continue
        salaries = sorted(m for _, m in with_mid)
        n = len(salaries)
        p25 = salaries[n // 4]
        p75 = salaries[(n * 3) // 4]
        in_band = [j for j, m in with_mid if p25 <= m <= p75]
        # Dedup by (company, title) and rank by example richness.
        seen: set[tuple] = set()
        examples = []
        for j in sorted(in_band, key=example_score, reverse=True):
            key = (j.company_name, j.title)
            if key in seen:
                continue
            seen.add(key)
            examples.append(job_to_example(j))
            if len(examples) >= 5:
                break
        p1p2[industry] = examples

    # ---- P3: vendor_official × category ----
    vendor_examples: dict[str, dict[str, list]] = {}
    for vendor in ("vendor_openai", "vendor_anthropic"):
        cats: dict[str, list[Job]] = defaultdict(list)
        for j in all_jobs:
            if j.platform_id == vendor:
                cats[categorize_vendor(j.title)].append(j)
        bucket = {}
        for cat in ("fde", "solutions", "applied", "deploy", "customer"):
            samples = sorted(cats.get(cat, []), key=example_score, reverse=True)
            bucket[cat] = [job_to_example(j) for j in samples[:4]]
        vendor_examples[vendor] = bucket

    # ---- P4: cross-market role_type comparison ----
    cross_buckets: dict[str, list[Job]] = defaultdict(list)
    for j in all_jobs:
        if j.market and j.role_type and has_sane_salary(j):
            cross_buckets[f"{j.market}_{j.role_type}"].append(j)

    p4 = {}
    for key in (
        "domestic_ai_native",
        "international_ai_native",
        "domestic_ai_augmented_traditional",
        "international_ai_augmented_traditional",
    ):
        jobs = cross_buckets.get(key, [])
        if not jobs:
            p4[key] = []
            continue
        # Pick samples in the IQR (currency-normalized) — matches narrative median.
        with_mid = [(j, midpoint_cny_monthly(j.salary_min, j.salary_max, j.salary_currency)) for j in jobs]
        with_mid = [(j, m) for j, m in with_mid if m is not None]
        if not with_mid:
            p4[key] = []
            continue
        salaries = sorted(m for _, m in with_mid)
        n = len(salaries)
        p25 = salaries[n // 4]
        p75 = salaries[(n * 3) // 4]
        in_band = [j for j, m in with_mid if p25 <= m <= p75]
        # Dedup by (company, title), then rank by example richness.
        seen: set[tuple] = set()
        unique = []
        for j in sorted(in_band, key=example_score, reverse=True):
            k = (j.company_name, j.title)
            if k in seen:
                continue
            seen.add(k)
            unique.append(j)
        p4[key] = [job_to_example(j) for j in unique[:4]]

    output = {
        "p1_p2_industries": p1p2,
        "p3_vendor_examples": vendor_examples,
        "p4_cross_market_examples": p4,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "wrote %s — %d industries, %d vendors, %d cross-market buckets",
        OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent),
        len(p1p2), len(vendor_examples), len(p4),
    )


if __name__ == "__main__":
    asyncio.run(main())
