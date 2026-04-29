#!/usr/bin/env python3
"""Pull salary reports from levels.fyi public SEO pages (#15).

Each URL ``https://www.levels.fyi/companies/<slug>/salaries/<role>``
embeds full SSR data inside ``<script id="__NEXT_DATA__">``. We extract
the per-sample records (uuid / company / level / yearsOfExperience /
baseSalary / totalCompensation / stockGrant / bonus / location) and write
to ``salary_reports``. Idempotent via (source, source_record_id) unique
constraint.

Coverage targets the AI-relevant company × role matrix from issue #15
(OpenAI / Anthropic / Google DeepMind / Meta AI / xAI / Mistral / Cohere
× software-engineer / machine-learning-engineer / data-scientist /
product-manager / research-scientist).

Usage:
    cd backend && .venv/bin/python scripts/collect_levels_fyi.py
    cd backend && .venv/bin/python scripts/collect_levels_fyi.py --company anthropic
"""
from __future__ import annotations

import argparse
import asyncio
import datetime
import json
import logging
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.database import async_session
from app.models.salary_report import SalaryReport

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
    re.DOTALL,
)

# AI-relevant companies from issue #12 + roles likely to have AI salary data.
AI_COMPANIES = [
    "openai",
    "anthropic",
    "google",  # DeepMind rolls up under Google on levels
    "meta",
    "xai",
    "mistral-ai",
    "cohere",
    "deepmind",
]
# CN big-tech with international hiring footprint -- gives us ground-truth
# 实际到手 numbers for major Chinese employers without needing the (now-offline)
# kanzhun salary baoliao board (#15 fallback after kanzhun shut down).
CN_BIGTECH_COMPANIES = [
    "bytedance",
    "alibaba",
    "tencent",
    "meituan",
    "pinduoduo",
    "xiaomi",
    "baidu",
    "huawei",
    "didi",
    "netease",
    "shein",
    "kwai",
    "jdcom",
]
AI_ROLES = [
    "software-engineer",
    "machine-learning-engineer",
    "data-scientist",
    "product-manager",
    "research-scientist",
    "hardware-engineer",
]


CN_LOCATION_HINTS = (
    "china", "beijing", "shanghai", "shenzhen", "hangzhou", "guangzhou",
    "chengdu", "wuhan", "xi'an", "xi an", "nanjing", "suzhou", "tianjin",
    "hong kong", "hongkong", "taipei", "taiwan",
    "北京", "上海", "深圳", "杭州", "广州", "成都", "武汉", "西安", "南京",
    "苏州", "天津", "香港", "台北", "中国",
)


def detect_market(country: str | None, location: str | None = None) -> str | None:
    if country and country.lower() in ("china", "cn"):
        return "domestic"
    loc = (location or "").lower()
    if any(hint in loc for hint in CN_LOCATION_HINTS):
        return "domestic"
    if country or location:
        return "international"
    return None


def to_rmb_monthly(total_yearly: int | None, currency: str | None) -> int | None:
    if not total_yearly:
        return None
    rate = {"USD": settings.usd_to_cny, "EUR": settings.eur_to_cny, "CNY": 1.0}.get(
        (currency or "USD").upper()
    )
    if not rate:
        return None
    return int(total_yearly * rate / 12)


def parse_offer_date(value) -> datetime.date | None:
    if not value:
        return None
    if isinstance(value, str):
        try:
            return datetime.datetime.strptime(value[:10], "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def extract_samples(next_data: dict, company_name: str) -> list[dict]:
    """Walk the SSR blob and pull every per-sample salary record."""
    pp = next_data.get("props", {}).get("pageProps", {})
    out: list[dict] = []
    seen: set[str] = set()

    for level_group in pp.get("averages", []) or []:
        for s in level_group.get("samples", []) or []:
            uuid = s.get("uuid")
            if not uuid or uuid in seen:
                continue
            seen.add(uuid)
            out.append(s)

    median = pp.get("median")
    if median:
        uid = median.get("uuid")
        if uid and uid not in seen:
            seen.add(uid)
            out.append(median)

    # Tag with the page's company name in case sample is missing it
    for s in out:
        s.setdefault("_pageCompany", company_name)
    return out


def _str_or_none(v) -> str | None:
    """Coerce to str | None — defends against levels.fyi sometimes returning bool
    (e.g. focusTag=false) for nullable string fields, which crashes asyncpg."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, str):
        return v.strip() or None
    return str(v)


def _int_or_none(v) -> int | None:
    if v is None or isinstance(v, bool):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def sample_to_row(s: dict) -> dict:
    company = _str_or_none(
        (s.get("companyInfo") or {}).get("name")
        or s.get("_pageCompany")
        or s.get("company")
    )
    location = _str_or_none(s.get("location"))
    currency = _str_or_none(s.get("baseSalaryCurrency")) or "USD"
    country = None  # levels.fyi page is per-company × per-role, country is in URL/page meta
    tc = _int_or_none(s.get("totalCompensation"))

    return {
        "source": "levels_fyi",
        "source_record_id": _str_or_none(s.get("uuid")),
        "company": company or "",
        "role_title": _str_or_none(s.get("title")),
        "job_family": _str_or_none(s.get("jobFamily")),
        "level": _str_or_none(s.get("level")),
        "focus_tag": _str_or_none(s.get("focusTag")),
        "location": location,
        "country": country,
        "market": detect_market(country, location) or "international",
        "years_experience": _int_or_none(s.get("yearsOfExperience")),
        "years_at_company": _int_or_none(s.get("yearsAtCompany")),
        "base_salary": _int_or_none(s.get("baseSalary")),
        "stock_grant_value": _int_or_none(s.get("avgAnnualStockGrantValue")),
        "bonus_value": _int_or_none(s.get("avgAnnualBonusValue")),
        "total_compensation": tc,
        "currency": currency,
        "total_comp_rmb_monthly": to_rmb_monthly(tc, currency),
        "offer_date": parse_offer_date(s.get("offerDate")),
    }


async def fetch_one(client: httpx.AsyncClient, company: str, role: str) -> list[dict]:
    url = f"https://www.levels.fyi/companies/{company}/salaries/{role}"
    try:
        resp = await client.get(url, timeout=30)
        if resp.status_code != 200:
            logger.info("skip %s/%s — HTTP %d", company, role, resp.status_code)
            return []
        m = NEXT_DATA_RE.search(resp.text)
        if not m:
            logger.warning("no __NEXT_DATA__ for %s/%s", company, role)
            return []
        data = json.loads(m.group(1))
        company_name = (
            data.get("props", {}).get("pageProps", {}).get("company", {}).get("name")
            or company
        )
        samples = extract_samples(data, company_name)
        rows = [sample_to_row(s) for s in samples]
        rows = [r for r in rows if r["source_record_id"] and r["company"]]
        logger.info("%s/%s — %d samples", company, role, len(rows))
        return rows
    except Exception as e:
        logger.warning("fetch failed %s/%s: %s", company, role, str(e)[:200])
        return []


async def collect(companies: list[str], roles: list[str], delay: float) -> int:
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html"}
    all_rows: list[dict] = []
    async with httpx.AsyncClient(headers=headers) as client:
        for company in companies:
            for role in roles:
                rows = await fetch_one(client, company, role)
                all_rows.extend(rows)
                await asyncio.sleep(delay)

    if not all_rows:
        logger.warning("no rows collected")
        return 0

    async with async_session() as db:
        # Upsert by (source, source_record_id) — re-runs refresh stats
        # without duplicating.
        stmt = insert(SalaryReport).values(all_rows)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_salary_source_record",
            set_={
                "company": stmt.excluded.company,
                "role_title": stmt.excluded.role_title,
                "job_family": stmt.excluded.job_family,
                "level": stmt.excluded.level,
                "focus_tag": stmt.excluded.focus_tag,
                "location": stmt.excluded.location,
                "country": stmt.excluded.country,
                "market": stmt.excluded.market,
                "years_experience": stmt.excluded.years_experience,
                "years_at_company": stmt.excluded.years_at_company,
                "base_salary": stmt.excluded.base_salary,
                "stock_grant_value": stmt.excluded.stock_grant_value,
                "bonus_value": stmt.excluded.bonus_value,
                "total_compensation": stmt.excluded.total_compensation,
                "currency": stmt.excluded.currency,
                "total_comp_rmb_monthly": stmt.excluded.total_comp_rmb_monthly,
                "offer_date": stmt.excluded.offer_date,
            },
        )
        await db.execute(stmt)
        await db.commit()

    logger.info("upserted %d salary reports from levels.fyi", len(all_rows))
    return len(all_rows)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--company", default=None,
        help="comma-sep slugs; default = AI_COMPANIES + CN_BIGTECH_COMPANIES",
    )
    parser.add_argument("--role", default=None, help="comma-sep role slugs; default = AI roles")
    parser.add_argument("--delay", type=float, default=1.5, help="seconds between requests")
    parser.add_argument(
        "--cn-only", action="store_true",
        help="only run CN big-tech slugs (faster re-runs once AI cos are cached)",
    )
    args = parser.parse_args()

    if args.company:
        companies = args.company.split(",")
    elif args.cn_only:
        companies = CN_BIGTECH_COMPANIES
    else:
        companies = AI_COMPANIES + CN_BIGTECH_COMPANIES
    roles = args.role.split(",") if args.role else AI_ROLES
    await collect(companies, roles, args.delay)


if __name__ == "__main__":
    asyncio.run(main())
