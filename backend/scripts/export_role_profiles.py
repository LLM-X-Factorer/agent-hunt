#!/usr/bin/env python3
"""Merge role aggregates with hand-written descriptions into one file (#18 P0).

Reads:
  - frontend/public/data/roles-domestic.json (output of analyze_roles.py)
  - frontend/public/data/roles-international.json
  - backend/data/role_descriptions.json (hand-written)

Joins on (market, role_id) and writes the union to
``frontend/public/data/role-profiles.json`` for the /roles page.

Pure file merge — no DB. Run after ``analyze_roles.py`` whenever role
aggregates or hand-written copy change.

Usage:
    cd backend && .venv/bin/python scripts/export_role_profiles.py
"""
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DATA = REPO_ROOT / "frontend" / "public" / "data"
DESCRIPTIONS_FILE = REPO_ROOT / "backend" / "data" / "role_descriptions.json"
OUTPUT_FILE = FRONTEND_DATA / "role-profiles.json"


def main() -> int:
    if not DESCRIPTIONS_FILE.exists():
        logger.error("missing %s", DESCRIPTIONS_FILE)
        return 1

    descriptions = {
        (d["market"], d["role_id"]): d
        for d in json.loads(DESCRIPTIONS_FILE.read_text())
    }

    profiles = []
    missing_desc: list[tuple[str, str]] = []
    missing_agg: list[tuple[str, str]] = set(descriptions.keys())

    for market, filename in [
        ("domestic", "roles-domestic.json"),
        ("international", "roles-international.json"),
    ]:
        path = FRONTEND_DATA / filename
        if not path.exists():
            logger.error("missing %s — run analyze_roles.py first", path)
            return 1
        for role in json.loads(path.read_text()):
            key = (market, role["role_id"])
            desc = descriptions.get(key)
            if not desc:
                missing_desc.append(key)
                continue
            missing_agg.discard(key)
            profiles.append({
                "market": market,
                **role,
                "role_description": desc["role_description"],
                "core_skills": desc["core_skills"],
                "vs_neighbor": desc["vs_neighbor"],
                "narrative": desc["narrative"],
                "who_fits": desc["who_fits"],
                "who_doesnt": desc["who_doesnt"],
            })

    if missing_desc:
        logger.warning("aggregate present but no description: %s", missing_desc)
    if missing_agg:
        logger.warning("description present but no aggregate: %s", sorted(missing_agg))

    profiles.sort(key=lambda p: (p["market"], -p["job_count"]))

    OUTPUT_FILE.write_text(json.dumps(profiles, ensure_ascii=False, indent=2))
    logger.info("wrote %s (%d roles)", OUTPUT_FILE.relative_to(REPO_ROOT), len(profiles))
    return 0


if __name__ == "__main__":
    sys.exit(main())
