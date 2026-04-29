#!/usr/bin/env python3
"""Export consolidated stats for the 5 narrative-handbook articles (P0).

Produces ``frontend/public/data/narrative-stats.json`` — single JSON the
narrative pages can read instead of cross-loading 4 different exports.

Aggregates:
  1. role_type x market totals (论断 1: 传统行业 vs 互联网 AI 增强需求)
  2. role_type x market salary medians (论断 4: 跨市场套利)
  3. domestic AI-augmented industry breakdown (links to industry-augmented-salary)
  4. ghost listing concentration by market (论断 5)

Usage:
    cd backend && .venv/bin/python scripts/export_narrative_stats.py
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
from app.services.currency import midpoint_cny_monthly

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "narrative-stats.json"
)

PREMIUM_TRADITIONAL = {"healthcare", "manufacturing", "finance"}
TRADITIONAL_INDUSTRIES = {
    "manufacturing", "automotive", "healthcare", "media",
    "finance", "education", "consulting", "retail",
    "energy", "telecom",
}


def median_int(values: list[float]) -> int | None:
    return int(median(values)) if values else None


def cny_mid(j: Job) -> float | None:
    """Midpoint of a job's salary in CNY/month, currency-normalized."""
    return midpoint_cny_monthly(j.salary_min, j.salary_max, j.salary_currency)


async def main():
    async with async_session() as db:
        jobs = (await db.execute(
            select(Job).where(Job.parse_status == "parsed")
        )).scalars().all()
    logger.info("loaded %d parsed jobs", len(jobs))

    # ---- 论断 1: role_type x market 总量 + 国内 augmented 行业分布 ----
    role_market_count: dict[tuple[str, str], int] = defaultdict(int)
    domestic_augmented_by_industry: dict[str, int] = defaultdict(int)
    for j in jobs:
        if j.role_type and j.market:
            role_market_count[(j.market, j.role_type)] += 1
        if (
            j.market == "domestic"
            and j.role_type == "ai_augmented_traditional"
            and j.industry
        ):
            domestic_augmented_by_industry[j.industry] += 1

    traditional_aug = sum(
        c for ind, c in domestic_augmented_by_industry.items()
        if ind in TRADITIONAL_INDUSTRIES
    )
    internet_aug = domestic_augmented_by_industry.get("internet", 0)

    market_basic = {
        "domestic_ai_native": role_market_count[("domestic", "ai_native")],
        "domestic_ai_augmented": role_market_count[("domestic", "ai_augmented_traditional")],
        "intl_ai_native": role_market_count[("international", "ai_native")],
        "intl_ai_augmented": role_market_count[("international", "ai_augmented_traditional")],
        "domestic_traditional_aug_total": traditional_aug,
        "domestic_internet_aug_total": internet_aug,
        "domestic_traditional_to_internet_ratio": (
            round(traditional_aug / internet_aug, 2) if internet_aug else None
        ),
        "domestic_industry_breakdown": [
            {"industry": ind, "count": cnt}
            for ind, cnt in sorted(domestic_augmented_by_industry.items(), key=lambda kv: -kv[1])
        ],
    }

    # ---- 论断 4: role_type x market 薪资中位数 (CNY/月，已汇率转换) ----
    salary_buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
    for j in jobs:
        if not (j.market and j.role_type):
            continue
        mid = cny_mid(j)
        if mid is not None:
            salary_buckets[(j.market, j.role_type)].append(mid)

    def bucket(market: str, rtype: str) -> dict | None:
        s = salary_buckets.get((market, rtype), [])
        if not s:
            return None
        return {"median": median_int(s), "sample_size": len(s)}

    cross_market = {
        "domestic_native": bucket("domestic", "ai_native"),
        "intl_native": bucket("international", "ai_native"),
        "domestic_augmented": bucket("domestic", "ai_augmented_traditional"),
        "intl_augmented": bucket("international", "ai_augmented_traditional"),
    }
    for variant in ("native", "augmented"):
        d = cross_market.get(f"domestic_{variant}")
        i = cross_market.get(f"intl_{variant}")
        if d and i and d["median"]:
            cross_market[f"{variant}_intl_to_domestic_ratio"] = round(
                i["median"] / d["median"], 2
            )

    # ---- 论断 2: 高薪传统行业 vs 互联网（domestic, augmented）-----
    by_industry_salary: dict[str, list[float]] = defaultdict(list)
    for j in jobs:
        if not (
            j.market == "domestic"
            and j.role_type == "ai_augmented_traditional"
            and j.industry
        ):
            continue
        mid = cny_mid(j)
        if mid is not None:
            by_industry_salary[j.industry].append(mid)

    premium = [s for ind, salaries in by_industry_salary.items()
               if ind in PREMIUM_TRADITIONAL for s in salaries]
    internet = by_industry_salary.get("internet", [])
    salary_premium = {
        "premium_industries": sorted(PREMIUM_TRADITIONAL),
        "premium_median": median_int(premium),
        "premium_sample_size": len(premium),
        "internet_median": median_int(internet),
        "internet_sample_size": len(internet),
    }
    if salary_premium["premium_median"] and salary_premium["internet_median"]:
        salary_premium["premium_over_internet_pct"] = round(
            (salary_premium["premium_median"] - salary_premium["internet_median"])
            / salary_premium["internet_median"] * 100, 1
        )

    # ---- 论断 5: ghost listing 集中度（reads existing quality-signals export）----
    quality_path = OUTPUT_PATH.parent / "jobs-quality-signals.json"
    p5_ghost = None
    if quality_path.exists():
        q = json.loads(quality_path.read_text(encoding="utf-8"))
        ghosts = q.get("top_ghost_listings", [])
        intl_ghost = sum(1 for g in ghosts if "international" in g.get("markets", []))
        dom_ghost = sum(1 for g in ghosts if "domestic" in g.get("markets", []))
        markets = {m["market"]: m["total"] for m in q.get("by_market", [])}
        intl_total = markets.get("international", 0)
        dom_total = markets.get("domestic", 0)
        intl_pct = round(intl_ghost / intl_total * 100, 2) if intl_total else None
        dom_pct = round(dom_ghost / dom_total * 100, 2) if dom_total else None
        p5_ghost = {
            "intl_ghost_clusters": intl_ghost,
            "intl_total_jobs": intl_total,
            "intl_ghost_pct": intl_pct,
            "domestic_ghost_clusters": dom_ghost,
            "domestic_total_jobs": dom_total,
            "domestic_ghost_pct": dom_pct,
            "intl_to_domestic_ratio": (
                round(intl_pct / dom_pct, 1) if intl_pct and dom_pct else None
            ),
            "top_ghost_listings": ghosts[:10],
        }

    output = {
        "totals": {
            "all_jobs": len(jobs),
            "labeled_jobs": sum(1 for j in jobs if j.role_type),
        },
        "p1_market_basic": market_basic,
        "p2_salary_premium": salary_premium,
        "p4_cross_market": cross_market,
        "p5_ghost": p5_ghost,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
