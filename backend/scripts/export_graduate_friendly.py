#!/usr/bin/env python3
"""Export graduate-friendliness scores per role (#11).

Combines is_campus / experience_requirement=fresh / internship_friendly
into a single 0-100 score per role, plus a fresh-only salary median
(社招 medians don't translate for an applying student).

Usage:
    cd backend && .venv/bin/python scripts/export_graduate_friendly.py
"""
import asyncio
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.applicant_profile import ApplicantProfile
from app.models.job import Job
from scripts.analyze_roles import (
    DOMESTIC_ROLES,
    INTERNATIONAL_ROLES,
    classify_job,
)

CITY_NORMALIZE_RE = re.compile(r"^(北京|上海|深圳|杭州|成都|广州|南京|武汉|西安|苏州|天津|厦门|郑州|香港|台北|新加坡|吉隆坡|远程)")


# Common US state abbreviations + countries — drop them so they don't show
# up as "cities" in the distribution.
NOISE_TOKENS = {
    "ca", "ny", "wa", "tx", "ma", "il", "nj", "co", "ga", "fl", "va", "or",
    "az", "nc", "pa", "mn", "oh", "mi", "mo", "ut", "tn", "md", "wi",
    "us", "usa", "uk", "canada", "remote", "hybrid", "onsite", "on", "qc",
    "and", "or", "nan", "none",
}


def normalize_city(raw: str) -> str | None:
    """Map "北京市" → "北京", "深圳·南山区" → "深圳"; for non-Chinese keep
    as-is but drop state codes and obvious noise."""
    if not raw:
        return None
    raw = raw.strip().replace("·", " ").rstrip(",.;")
    if not raw or raw.lower() in NOISE_TOKENS:
        return None

    # Chinese cities: collapse "X市" / "X·区·街道" → X
    m = CITY_NORMALIZE_RE.match(raw)
    if m:
        return m.group(1)
    if raw.endswith("市") and len(raw) <= 6:
        return raw[:-1]
    if any("一" <= ch <= "鿿" for ch in raw):
        return raw[:6] if len(raw) > 6 else raw

    # Latin: keep multi-word names intact (don't truncate "San Francisco" to "San F").
    # If it's a single short token with only letters, also drop tokens < 3 chars.
    if len(raw) < 3:
        return None
    return raw


# Latin city splits use ", " or " / " or "|" — Chinese splits use "、，".
CITY_SPLIT_LATIN_RE = re.compile(r"\s*[,/|;]\s*")
CITY_SPLIT_CN_RE = re.compile(r"[、，]")


def split_locations(loc: str | None) -> list[str]:
    """A single Job.location can be "北京、上海" / "San Francisco, CA, Seattle, WA" —
    return canonical city tokens (state abbrevs / noise dropped)."""
    if not loc:
        return []
    has_cn = any("一" <= ch <= "鿿" for ch in loc)
    parts = (CITY_SPLIT_CN_RE.split(loc) if has_cn else CITY_SPLIT_LATIN_RE.split(loc))
    return [c for p in parts if (c := normalize_city(p))]

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "roles-graduate-friendly.json"
)
RULES_BY_MARKET = {"domestic": DOMESTIC_ROLES, "international": INTERNATIONAL_ROLES}


def score_role(jobs: list[Job]) -> dict:
    """Composite friendliness score in [0, 100] + the building blocks."""
    total = len(jobs)
    if not total:
        return {"graduateFriendlyScore": 0}

    campus = sum(1 for j in jobs if j.is_campus)
    intern = sum(1 for j in jobs if j.internship_friendly)
    fresh = sum(1 for j in jobs if j.experience_requirement == "fresh")
    fresh_or_under_1y = sum(
        1 for j in jobs if j.experience_requirement in ("fresh", "0-1y")
    )

    # Weighted: campus is the strongest positive signal, fresh second,
    # internship-friendly third. All shares scale to 100 then averaged.
    campus_share = campus / total
    fresh_share = fresh / total
    fresh_or_junior_share = fresh_or_under_1y / total
    intern_share = intern / total

    score = (
        campus_share * 50
        + fresh_share * 30
        + fresh_or_junior_share * 10
        + intern_share * 10
    )
    score = round(min(100, score * 100 / 100), 1)

    fresh_jobs = [j for j in jobs if j.experience_requirement == "fresh"]
    fresh_salaries = [s for j in fresh_jobs if (s := j.salary_mid_cny_monthly) is not None]
    social_jobs = [j for j in jobs if j.experience_requirement not in ("fresh", None)]
    social_salaries = [s for j in social_jobs if (s := j.salary_mid_cny_monthly) is not None]

    # City distribution — split multi-city listings ("北京、上海") so each city
    # gets its own count. Only count campus-friendly listings (intern + campus + fresh).
    campus_jobs = [j for j in jobs if j.is_campus or j.internship_friendly
                   or j.experience_requirement == "fresh"]
    city_counter: Counter = Counter()
    for j in campus_jobs:
        for c in split_locations(j.location):
            city_counter[c] += 1

    return {
        "graduateFriendlyScore": score,
        "totalJobs": total,
        "campusJobCount": campus,
        "internshipJobCount": intern,
        "freshJobCount": fresh,
        "freshSalaryMedian": int(median(fresh_salaries)) if fresh_salaries else None,
        "socialSalaryMedian": int(median(social_salaries)) if social_salaries else None,
        "topCampusCities": [
            {"city": c, "count": n} for c, n in city_counter.most_common(8)
        ],
    }


def classify_profile(p: ApplicantProfile) -> tuple[str, str] | None:
    """Map a nowcoder profile to (market, role_id). Returns None if no match."""
    market = p.market or "domestic"
    rules = RULES_BY_MARKET.get(market, DOMESTIC_ROLES)
    for source in (p.role_title, p.title):
        if source:
            rid = classify_job(source, rules)
            if rid not in ("_noise", "other"):
                return market, rid
    return None


async def main():
    async with async_session() as db:
        jobs = (await db.execute(
            select(Job).where(Job.parse_status == "parsed", Job.title.isnot(None))
        )).scalars().all()
        profiles = (await db.execute(select(ApplicantProfile))).scalars().all()
    logger.info("loaded %d parsed jobs, %d applicant profiles", len(jobs), len(profiles))

    # Pre-bucket applicant profiles by (market, role_id) for the join below.
    # offer_status="offered" reflects actual hires — a stronger signal than
    # generic "applied".
    profile_total: dict[tuple[str, str], int] = defaultdict(int)
    profile_offered: dict[tuple[str, str], int] = defaultdict(int)
    for p in profiles:
        match = classify_profile(p)
        if not match:
            continue
        profile_total[match] += 1
        if p.offer_status == "offered":
            profile_offered[match] += 1

    output: dict[str, list[dict]] = {}
    for market, rules in RULES_BY_MARKET.items():
        market_jobs = [j for j in jobs if j.market == market]
        role_names = {rid: name for rid, name, _ in rules}

        groups: dict[str, list[Job]] = defaultdict(list)
        for j in market_jobs:
            rid = classify_job(j.title or "", rules)
            if rid in ("_noise", "other"):
                continue
            groups[rid].append(j)

        rows = []
        for rid, gjobs in groups.items():
            if len(gjobs) < 3:
                continue
            stats = score_role(gjobs)
            stats["roleId"] = rid
            stats["roleName"] = role_names.get(rid, rid)
            stats["applicantSignalCount"] = profile_total.get((market, rid), 0)
            stats["applicantOfferCount"] = profile_offered.get((market, rid), 0)
            rows.append(stats)
        rows.sort(key=lambda r: -r["graduateFriendlyScore"])
        output[market] = rows
        logger.info("%s — %d roles scored", market, len(rows))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
