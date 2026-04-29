#!/usr/bin/env python3
"""Pull 智谱 / Moonshot jobs via Moka HR (#12).

Moka API responses are encrypted (`data` is a ciphertext blob with a paired
``necromancer`` key for in-browser decryption), so we render the React SPA
with Playwright and scrape the DOM. Card structure is identical across
Moka tenants:

    <a class="link-..." href="#/job/<UUID>">
      <span class="title-...">岗位名</span>
      <span class="published-at-...">发布于 YYYY-MM-DD</span>
      <div class="info-...">
        <div class="no-adaptive-tooltip">部门</div>
        <div class="no-adaptive-tooltip">全职/实习/兼职</div>
        <div class="no-adaptive-tooltip">岗位族 (e.g. 算法类)</div>  # optional
        <div class="no-adaptive-tooltip">城市 (e.g. 北京市)</div>     # optional
      </div>
      <div>JD body 截断 ~500 字</div>
    </a>

Pagination is direct via URL hash: ``#/jobs?page=N&pageSize=50`` (50 is the
server cap — bigger values silently fall back to 50).

Upstream is structurally clean — title / location / job_type are direct
fields. We backfill them straight to ``jobs`` with parse_status='parsed'
so the LLM pipeline skips this batch (mirrors the GitHub hiring + 飞书
collector pattern).

Usage:
    cd backend && .venv/bin/python scripts/collect_moka_jobs.py
    cd backend && .venv/bin/python scripts/collect_moka_jobs.py --vendor vendor_zhipuai
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import logging
import re
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
PAGE_SIZE = 50  # Moka caps at 50 server-side
WAIT_MS = 8000
RENDER_SETTLE_MS = 2500  # extra time after first card mounts so all 50 fill in

# (platform_id, company_name, [(portal_url_template, kind)])
# kind ∈ {"social", "campus"} drives is_campus / experience_requirement.
# 智谱社招 portal already covers their campus listings (titles include
# "（校招）" etc.), so we don't need a separate campus URL.
VENDORS: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("vendor_zhipuai", "智谱AI", [
        ("https://app.mokahr.com/social-recruitment/zphz/148983?locale=zh-CN#/jobs?page={page}&pageSize=50", "social"),
    ]),
    ("vendor_moonshot", "Moonshot AI", [
        ("https://app.mokahr.com/apply/moonshot/148506?sourceToken=7bec6769f2bfa471e5c9ce21b6b1096b#/jobs?page={page}&pageSize=50", "social"),
    ]),
]

# JS that reads every job card on the current page and returns structured rows.
EXTRACT_JS = """
() => {
  const seen = new Set();
  const out = [];
  // a[href*="#/job/"] matches any card link — class names rotate, so we
  // filter by href shape instead of relying on the rotating CSS hash.
  const cards = document.querySelectorAll('a[href*="#/job/"]');
  for (const a of cards) {
    const m = a.getAttribute('href')?.match(/#\\/job\\/([a-f0-9-]+)/);
    if (!m) continue;
    const id = m[1];
    if (seen.has(id)) continue;
    seen.add(id);
    const title = (a.querySelector('[class*="title-"]')?.textContent || '').trim();
    const publishedAt = (a.querySelector('[class*="published-at-"]')?.textContent || '').trim();
    const infoArea = a.querySelector('[class*="info-"]');
    const segs = infoArea
      ? [...new Set(Array.from(infoArea.querySelectorAll('div.no-adaptive-tooltip'))
          .map(d => (d.textContent || '').trim())
          .filter(Boolean))]
      : [];
    // Fall back to whole-card innerText (deduped) — robust against rotating
    // class hashes. raw_content downstream is a free-form blob anyway.
    const fullText = (a.innerText || '').replace(/\\s+\\n/g, '\\n').trim();
    out.push({id, title, publishedAt, segs, jobDesc: fullText, href: a.getAttribute('href')});
  }
  return out;
}
"""

CITY_RE = re.compile(
    r"(北京|上海|深圳|杭州|成都|广州|南京|武汉|西安|苏州|天津|厦门|香港|台北|新加坡|吉隆坡|远程)"
)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def parse_card(card: dict, kind: str, base_origin: str) -> dict:
    segs = card["segs"]
    location = next((s for s in segs if CITY_RE.search(s)), None)
    department = next((s for s in segs if not CITY_RE.search(s) and "全职" not in s
                       and "实习" not in s and "兼职" not in s), None)
    job_type = next((s for s in segs if any(t in s for t in ("全职", "实习", "兼职"))), None)

    has_intern = bool(job_type and "实习" in job_type)
    title_lc = card["title"]
    title_hints_campus = any(kw in title_lc for kw in ("校招", "应届", "实习生"))
    is_campus = (kind == "campus") or has_intern or title_hints_campus

    experience = "fresh" if (is_campus or has_intern) else None

    pub_match = DATE_RE.search(card["publishedAt"] or "")
    posted_date = pub_match.group(1) if pub_match else None

    full_url = base_origin + card["href"] if card["href"].startswith("#/") else card["href"]
    return {
        "id": card["id"],
        "title": card["title"],
        "department": department,
        "job_type": job_type,
        "location": location,
        "is_campus": is_campus,
        "internship_friendly": has_intern,
        "experience_requirement": experience,
        "posted_date": posted_date,
        "jobDesc": card["jobDesc"],
        "url": full_url,
    }


def to_import_request(platform_id: str, company: str, parsed: dict) -> JobImportRequest | None:
    if not parsed["title"] or len(parsed["jobDesc"]) < 30:
        return None
    parts = [parsed["title"], f"公司: {company}"]
    if parsed["department"]:
        parts.append(f"部门: {parsed['department']}")
    if parsed["location"]:
        parts.append(f"工作地点: {parsed['location']}")
    if parsed["job_type"]:
        parts.append(f"工作类型: {parsed['job_type']}")
    if parsed["posted_date"]:
        parts.append(f"发布日期: {parsed['posted_date']}")
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


def origin_of(url_template: str) -> str:
    """Return scheme://host for the URL (drops path/hash/query)."""
    return "/".join(url_template.split("/", 3)[:3])


async def fetch_portal(page, url_template: str, kind: str) -> list[dict]:
    parsed_cards: list[dict] = []
    base_origin = origin_of(url_template)
    page_num = 1
    while True:
        url = url_template.format(page=page_num)
        logger.info("  fetching page %d — %s", page_num, url)
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector('a[href*="#/job/"]', timeout=WAIT_MS)
            # Cards mount one-by-one — give the SPA a moment to fill the page.
            await page.wait_for_timeout(RENDER_SETTLE_MS)
        except Exception as e:
            logger.info("  no cards rendered on page %d (%s) — assume end",
                        page_num, str(e)[:60])
            break

        cards = await page.evaluate(EXTRACT_JS)
        if not cards:
            break
        for c in cards:
            parsed_cards.append(parse_card(c, kind, base_origin))
        logger.info("  page %d → %d cards (running total %d)",
                    page_num, len(cards), len(parsed_cards))
        if len(cards) < PAGE_SIZE:
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


async def collect_one(browser, platform_id: str, company: str,
                       portals: list[tuple[str, str]]) -> None:
    context = await browser.new_context(
        user_agent=UA,
        viewport={"width": 1440, "height": 900},
        locale="zh-CN",
    )
    page = await context.new_page()
    try:
        all_parsed: list[dict] = []
        for portal_url, kind in portals:
            cards = await fetch_portal(page, portal_url, kind)
            all_parsed.extend(cards)
        # Dedup across portals (campus titles can sometimes also appear in social).
        seen: set[str] = set()
        deduped: list[dict] = []
        for c in all_parsed:
            if c["id"] in seen:
                continue
            seen.add(c["id"])
            deduped.append(c)
        logger.info("%s — %d unique cards across %d portal(s)",
                    platform_id, len(deduped), len(portals))

        requests = [r for r in (to_import_request(platform_id, company, c) for c in deduped) if r]
        skipped_no_desc = len(deduped) - len(requests)
        if skipped_no_desc:
            logger.info("%s — skipped %d cards with empty/short JD body",
                        platform_id, skipped_no_desc)

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
