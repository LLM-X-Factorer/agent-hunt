from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.models.skill import Skill
from app.services.skill_extractor import extractor


async def skill_cooccurrence(
    db: AsyncSession,
    top_n: int = 30,
    min_cooccurrence: int = 3,
    market: str | None = None,
) -> dict:
    query = select(Job).where(Job.parse_status == "parsed")
    if market:
        query = query.where(Job.market == market)
    result = await db.execute(query)
    jobs = result.scalars().all()

    # Count individual skill occurrences and co-occurrences
    skill_counts: Counter[str] = Counter()
    pair_counts: Counter[tuple[str, str]] = Counter()
    jobs_analyzed = 0

    for job in jobs:
        all_skills = (job.required_skills or []) + (job.preferred_skills or [])
        normalized = extractor.normalize_list(all_skills)
        if len(normalized) < 2:
            continue

        jobs_analyzed += 1
        for sid in normalized:
            skill_counts[sid] += 1

        for a, b in combinations(sorted(normalized), 2):
            pair_counts[(a, b)] += 1

    # Get canonical names
    skill_result = await db.execute(select(Skill))
    skill_map = {s.id: s.canonical_name for s in skill_result.scalars().all()}

    # Build top pairs with Jaccard index
    top_pairs = []
    for (a, b), count in pair_counts.most_common():
        if count < min_cooccurrence:
            break
        union = skill_counts[a] + skill_counts[b] - count
        jaccard = round(count / union, 3) if union > 0 else 0

        top_pairs.append({
            "skill_a": a,
            "skill_b": b,
            "skill_a_name": skill_map.get(a, a),
            "skill_b_name": skill_map.get(b, b),
            "cooccurrence_count": count,
            "jaccard_index": jaccard,
        })

        if len(top_pairs) >= top_n:
            break

    return {
        "top_pairs": top_pairs,
        "total_jobs_analyzed": jobs_analyzed,
    }
