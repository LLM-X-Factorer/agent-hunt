#!/usr/bin/env python3
"""Export applicant-side profile distributions per role (#14).

Joins ApplicantProfile to our internal roleId taxonomy via title/role_title
classifier (same rules as analyze_roles), so aijobfit can answer "what do
the people who apply to this role look like" questions.

Output: ``frontend/public/data/roles-applicant-profile.json``

Usage:
    cd backend && .venv/bin/python scripts/export_applicant_profiles.py
"""
import asyncio
import json
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.database import async_session
from app.models.applicant_profile import ApplicantProfile
from scripts.analyze_roles import (
    DOMESTIC_ROLES,
    INTERNATIONAL_ROLES,
    classify_job,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend" / "public" / "data" / "roles-applicant-profile.json"
)
RULES_BY_MARKET = {"domestic": DOMESTIC_ROLES, "international": INTERNATIONAL_ROLES}


def classify_profile(p: ApplicantProfile) -> str | None:
    """Map a profile to one of our internal role IDs."""
    rules = RULES_BY_MARKET.get(p.market or "domestic", DOMESTIC_ROLES)
    for source in (p.role_title, p.title):
        if source:
            rid = classify_job(source, rules)
            if rid not in ("_noise", "other"):
                return rid
    return None


def role_stats(rows: list[ApplicantProfile]) -> dict:
    schools = Counter(r.school for r in rows if r.school)
    school_tiers = Counter(r.school_tier for r in rows if r.school_tier)
    majors = Counter(r.major for r in rows if r.major)
    degrees = Counter(r.degree for r in rows if r.degree)
    offer_statuses = Counter(r.offer_status for r in rows if r.offer_status)
    grad_years = Counter(r.graduation_year for r in rows if r.graduation_year)
    companies = Counter(r.company for r in rows if r.company)
    comps = [r.compensation_disclosed for r in rows if r.compensation_disclosed]

    yoes = [r.years_experience for r in rows if r.years_experience is not None]
    return {
        "totalProfiles": len(rows),
        "schoolTierShare": dict(school_tiers),
        "topSchools": [{"school": s, "count": c} for s, c in schools.most_common(15)],
        "topMajors": [{"major": m, "count": c} for m, c in majors.most_common(15)],
        "degreeShare": dict(degrees),
        "offerStatusShare": dict(offer_statuses),
        "graduationYears": dict(sorted(grad_years.items())),
        "topCompanies": [
            {"company": c, "count": cnt} for c, cnt in companies.most_common(15)
        ],
        "yearsExperience": {
            "median": sorted(yoes)[len(yoes) // 2] if yoes else None,
            "p25": sorted(yoes)[len(yoes) // 4] if yoes else None,
            "p75": sorted(yoes)[len(yoes) * 3 // 4] if yoes else None,
            "sample": len(yoes),
        },
        "selfReportedComp": {
            "median": sorted(comps)[len(comps) // 2] if comps else None,
            "sample": len(comps),
        },
    }


async def main():
    async with async_session() as db:
        rows = (await db.execute(select(ApplicantProfile))).scalars().all()
    logger.info("loaded %d applicant_profiles", len(rows))

    by_market_role: dict[str, dict[str, list[ApplicantProfile]]] = defaultdict(
        lambda: defaultdict(list)
    )
    classified = 0
    for r in rows:
        rid = classify_profile(r)
        if rid:
            classified += 1
            by_market_role[r.market or "domestic"][rid].append(r)

    logger.info(
        "classified %d / %d (%.1f%%) into roles",
        classified, len(rows), 100 * classified / max(1, len(rows)),
    )

    output: dict[str, dict[str, dict]] = {"domestic": {}, "international": {}}
    role_names_by_market: dict[str, dict[str, str]] = {}
    for market in ("domestic", "international"):
        rules = RULES_BY_MARKET[market]
        role_names_by_market[market] = {rid: name for rid, name, _ in rules}
        for rid, rrows in sorted(by_market_role[market].items(), key=lambda kv: -len(kv[1])):
            if len(rrows) < 3:
                continue
            output[market][rid] = role_stats(rrows)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(
            {
                "data": output,
                "roleNames": role_names_by_market,
                "totalProfiles": len(rows),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.info("wrote %s", OUTPUT_PATH.relative_to(OUTPUT_PATH.parent.parent.parent))


if __name__ == "__main__":
    asyncio.run(main())
