#!/usr/bin/env python3
"""Pull MiniMax / 百川智能 jobs via 飞书招聘 (#12).

飞书招聘 API responses are encrypted (`_signature` query param + encrypted
`post_param`), so we render with Playwright and scrape the DOM. Both portals
use identical card structure:
    <a data-id="..." href="/<slug>/position/<id>/detail">
      <div class="positionItem-title-text">岗位名</div>
      <div class="positionItem-subTitle">
        <span>城市</span>
        <span>校招/社招</span>
        <span>全职/实习</span>
        <span>研发 - 算法</span>            <!-- category -->
        <span>2027届实习生招聘</span>       <!-- recruitment kind, 校招 only -->
      </div>
      <div class="positionItem-jobDesc">JD 摘要 ~500 字</div>
    </a>

Each tenant has 1-2 portals (社招 / 校招). With ?limit=50 we get 50 cards
per render; loop pages until card count < 50.

Upstream is structurally clean — title / company / location / market are
direct fields on the card. We backfill them straight to ``jobs`` and mark
``parse_status='parsed'`` so the LLM pipeline skips this batch (matches the
GitHub hiring collector pattern).

Usage:
    cd backend && .venv/bin/python scripts/collect_feishu_jobs.py
    cd backend && .venv/bin/python scripts/collect_feishu_jobs.py --vendor vendor_minimax
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright
from sqlalchemy import update

from app.collectors.manual_import import import_jobs
from app.database import async_session
from app.models.job import Job
from app.schemas.job import JobImportRequest
from app.services.seed import seed_platforms

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
PAGE_LIMIT = 50  # cards per page render
WAIT_MS = 6000  # SPA hydration window

# (platform_id, company_name, [portal_url_template]).
# Each template carries `?current={page}&limit=50` so we can paginate.
VENDORS: list[tuple[str, str, list[str]]] = [
    ("vendor_minimax", "MiniMax", [
        "https://vrfi1sk8a0.jobs.feishu.cn/index/?current={page}&limit=50",
        "https://vrfi1sk8a0.jobs.feishu.cn/379481/?current={page}&limit=50",
    ]),
    ("vendor_baichuan", "百川智能", [
        "https://cq6qe6bvfr6.jobs.feishu.cn/baichuanzhaopin?current={page}&limit=50",
    ]),
]

# JS that reads every job card on the current page and returns structured rows.
EXTRACT_JS = """
() => {
  const cards = document.querySelectorAll('a[data-id][href*="/position/"][href*="/detail"]');
  const out = [];
  for (const a of cards) {
    const id = a.getAttribute('data-id');
    if (!id) continue;
    const title = a.querySelector('.positionItem-title-text')?.textContent?.trim() || '';
    const subSpans = Array.from(a.querySelectorAll('.positionItem-subTitle span'))
      .map(s => s.textContent?.trim() || '')
      .filter(Boolean);
    const jobDesc = a.querySelector('.positionItem-jobDesc')?.textContent?.trim() || '';
    const href = a.getAttribute('href') || '';
    out.push({id, title, subSpans, jobDesc, href});
  }
  return out;
}
"""


def parse_card(card: dict, base_url: str) -> dict:
    """Split subSpans into structured fields.

    Heuristics: first span = location, then tags fall into 校招/社招 /
    全职/实习 / category (contains "-" like "研发 - 算法") / recruitment_kind.
    """
    subs = card["subSpans"]
    location = subs[0] if subs else None
    is_campus = any("校招" in s for s in subs)
    has_社招 = any("社招" in s for s in subs)
    has_intern = any("实习" in s for s in subs)
    category = next((s for s in subs if " - " in s or " · " in s), None)
    recruitment_kind = next(
        (s for s in subs if any(kw in s for kw in ("招聘", "人才计划", "Top Talent"))),
        None,
    )

    # `experience_requirement` is varchar(10) — keep it tight. We only know
    # "fresh" reliably (校招/实习). 社招 doesn't disclose a band on the card,
    # so leave it null and let LLM/manual review fill later.
    experience = "fresh" if (is_campus or has_intern) else None

    full_url = base_url.rstrip("/") + card["href"] if card["href"].startswith("/") else card["href"]
    return {
        "id": card["id"],
        "title": card["title"],
        "location": location,
        "tags": subs,
        "category": category,
        "recruitment_kind": recruitment_kind,
        "is_campus": is_campus,
        "internship_friendly": has_intern,
        "experience_requirement": experience,
        "jobDesc": card["jobDesc"],
        "url": full_url,
    }


def to_import_request(platform_id: str, company: str, parsed: dict) -> JobImportRequest | None:
    if not parsed["title"] or len(parsed["jobDesc"]) < 30:
        return None
    parts = [parsed["title"], f"公司: {company}"]
    if parsed["location"]:
        parts.append(f"工作地点: {parsed['location']}")
    if parsed["tags"]:
        parts.append("标签: " + " / ".join(parsed["tags"]))
    parts.append("")
    parts.append(parsed["jobDesc"])
    raw = "\n".join(parts)
    return JobImportRequest(
        platform_id=platform_id,
        platform_job_id=parsed["id"],
        source_url=parsed["url"],
        raw_content=raw[:60000],
        language="zh",
        source="vendor_official",
    )


async def fetch_portal(page, url_template: str) -> list[dict]:
    """Walk pages of a single portal until cards exhaust."""
    parsed_cards: list[dict] = []
    base_url_origin = url_template.split("/", 3)[0] + "//" + url_template.split("/", 3)[2]
    page_num = 1
    while True:
        url = url_template.format(page=page_num)
        logger.info("  fetching page %d — %s", page_num, url)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            logger.warning("  goto failed: %s", str(e)[:120])
            break

        # Wait for SPA to render. The selector appears once cards mount.
        try:
            await page.wait_for_selector('a[data-id][href*="/position/"]', timeout=WAIT_MS)
        except Exception:
            logger.info("  no cards rendered — assume end of pages")
            break

        cards = await page.evaluate(EXTRACT_JS)
        if not cards:
            break
        for c in cards:
            parsed_cards.append(parse_card(c, base_url_origin))
        logger.info("  page %d → %d cards (running total %d)",
                    page_num, len(cards), len(parsed_cards))
        if len(cards) < PAGE_LIMIT:
            break
        page_num += 1
        if page_num > 30:
            logger.warning("  hit safety cap of 30 pages")
            break
    return parsed_cards


async def backfill_structured_fields(
    platform_id: str, company: str, parsed_cards: list[dict]
) -> int:
    if not parsed_cards:
        return 0
    now = dt.datetime.now(dt.timezone.utc)
    updated = 0
    async with async_session() as db:
        for p in parsed_cards:
            title = (p["title"] or "")[:250] or None
            location = (p["location"] or "")[:250] or None
            res = await db.execute(
                update(Job)
                .where(Job.platform_id == platform_id)
                .where(Job.platform_job_id == p["id"])
                .values(
                    title=title,
                    company_name=company,
                    location=location,
                    market="domestic",
                    is_campus=p["is_campus"],
                    internship_friendly=p["internship_friendly"],
                    experience_requirement=p["experience_requirement"],
                    parse_status="parsed",
                    parsed_at=now,
                    language="zh",
                )
            )
            updated += res.rowcount or 0
        await db.commit()
    return updated


async def collect_one(browser, platform_id: str, company: str, portals: list[str]) -> None:
    context = await browser.new_context(
        user_agent=UA,
        viewport={"width": 1440, "height": 900},
        locale="zh-CN",
    )
    page = await context.new_page()
    try:
        all_parsed: list[dict] = []
        for portal in portals:
            cards = await fetch_portal(page, portal)
            all_parsed.extend(cards)
        # Dedup within batch by job id (在两个 portal 间偶尔有重叠是可能的)
        seen: set[str] = set()
        deduped = []
        for c in all_parsed:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            deduped.append(c)
        logger.info("%s — %d unique cards across %d portal(s)",
                    platform_id, len(deduped), len(portals))

        requests = [r for r in (to_import_request(platform_id, company, c) for c in deduped) if r]
        imported_total = 0
        re_seen_total = 0
        for i in range(0, len(requests), 50):
            batch = requests[i : i + 50]
            async with async_session() as db:
                res = await import_jobs(db, batch)
            imported_total += res.imported
            re_seen_total += res.skipped
        logger.info("%s — imported=%d (new) re-seen=%d",
                    platform_id, imported_total, re_seen_total)

        # Backfill structured fields so LLM pipeline skips these.
        bf = await backfill_structured_fields(platform_id, company, deduped)
        logger.info("%s — backfilled %d rows (parse_status='parsed')", platform_id, bf)
    finally:
        await context.close()


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vendor",
        default=None,
        help="comma-sep platform_id(s); default = all from VENDORS",
    )
    args = parser.parse_args()

    targets = VENDORS
    if args.vendor:
        wanted = set(args.vendor.split(","))
        targets = [v for v in VENDORS if v[0] in wanted]

    # Make sure platform rows exist (FK target for jobs.platform_id).
    async with async_session() as db:
        await seed_platforms(db)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            for platform_id, company, portals in targets:
                try:
                    await collect_one(browser, platform_id, company, portals)
                except Exception as e:
                    logger.exception("collector failed for %s: %s", platform_id, str(e)[:200])
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
