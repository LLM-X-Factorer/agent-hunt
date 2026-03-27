from __future__ import annotations

import hashlib
import json
import logging
import random
import re
from pathlib import Path

from playwright.async_api import async_playwright

from app.collectors.base import BaseCollector
from app.collectors.registry import register
from app.schemas.job import JobImportRequest

logger = logging.getLogger(__name__)

COOKIES_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "lagou_cookies.json"
SEARCH_URL = "https://www.lagou.com/wn/zhaopin?kd={keyword}"


class LagouCollector(BaseCollector):

    @property
    def platform_id(self) -> str:
        return "lagou"

    async def collect(
        self, keyword: str, max_pages: int = 5
    ) -> list[JobImportRequest]:
        jobs: list[JobImportRequest] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1440, "height": 900},
            )

            # Load cookies if available
            if COOKIES_PATH.exists():
                cookie_data = json.loads(COOKIES_PATH.read_text(encoding="utf-8"))
                await context.add_cookies(cookie_data["cookies"])
                logger.info("Lagou: loaded cookies from %s", COOKIES_PATH)
            else:
                logger.info("Lagou: no cookies file, attempting without login")

            page = await context.new_page()

            # Visit homepage first to get session cookies
            try:
                await page.goto(
                    "https://www.lagou.com", wait_until="domcontentloaded", timeout=20000
                )
                await page.wait_for_timeout(2000)
            except Exception:
                logger.warning("Lagou: homepage load failed")

            for page_num in range(max_pages):
                url = SEARCH_URL.format(keyword=keyword)
                if page_num > 0:
                    url += f"&pn={page_num + 1}"

                logger.info("Lagou: fetching page %d — %s", page_num, url)

                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(3000)
                except Exception:
                    logger.warning("Lagou: page %d load failed, stopping", page_num)
                    break

                card_data = await page.evaluate("""() => {
                    // Try multiple selectors for job cards
                    const selectors = [
                        '[class*="item__"]',
                        '.joblist-box .item',
                        '.list_item_top',
                        '[class*="job-card"]',
                        '.position-list .item',
                    ];
                    let cards = [];
                    for (const sel of selectors) {
                        cards = document.querySelectorAll(sel);
                        if (cards.length > 0) break;
                    }

                    let results = [];
                    for (const card of cards) {
                        const links = card.querySelectorAll('a[href]');
                        let jobLink = '';
                        for (const a of links) {
                            if (a.href.includes('/job/') || a.href.includes('/jobs/')) {
                                jobLink = a.href;
                                break;
                            }
                        }
                        if (!jobLink && links.length > 0) jobLink = links[0].href;
                        const text = card.textContent.trim();
                        if (text.length > 10) {
                            results.push({href: jobLink, text: text});
                        }
                    }
                    return results;
                }""")

                if not card_data:
                    logger.info("Lagou: no cards on page %d, stopping", page_num)
                    break

                for item in card_data:
                    job = self._parse_card(item)
                    if job:
                        jobs.append(job)

                logger.info("Lagou: page %d, %d cards", page_num, len(card_data))
                await page.wait_for_timeout(random.randint(3000, 6000))

                # Try clicking next page button
                if page_num < max_pages - 1:
                    try:
                        next_btn = await page.query_selector(
                            '[class*="pagination-next"], .lg-pagination-next, [class*="next"]'
                        )
                        if next_btn:
                            await next_btn.click()
                            await page.wait_for_timeout(random.randint(2000, 4000))
                    except Exception:
                        pass

            # Enrich with detail pages
            jobs = await self._enrich_with_details(page, jobs)
            await browser.close()

        logger.info("Lagou: collected %d jobs for %r", len(jobs), keyword)
        return jobs

    def _parse_card(self, item: dict) -> JobImportRequest | None:
        text = item.get("text", "").strip()
        href = item.get("href", "")

        if not text or len(text) < 10:
            return None

        source_url = href.split("?")[0] if href else None
        platform_job_id = _extract_job_id(source_url, text)

        return JobImportRequest(
            platform_id="lagou",
            platform_job_id=platform_job_id,
            source_url=source_url,
            raw_content=text,
            language="zh",
        )

    async def _enrich_with_details(
        self, page, jobs: list[JobImportRequest]
    ) -> list[JobImportRequest]:
        enriched = []
        for job in jobs:
            if not job.source_url:
                enriched.append(job)
                continue

            try:
                await page.goto(
                    job.source_url, wait_until="domcontentloaded", timeout=20000
                )
                await page.wait_for_timeout(2000)

                detail_text = await page.evaluate("""() => {
                    const selectors = [
                        '[class*="job-detail"]',
                        '[class*="position-detail"]',
                        '.job_bt .job-detail',
                        '.job_detail',
                        '[class*="desc"]',
                    ];
                    for (const sel of selectors) {
                        const el = document.querySelector(sel);
                        if (el && el.textContent.trim().length > 20) {
                            return el.textContent.trim();
                        }
                    }
                    return '';
                }""")

                if detail_text and len(detail_text) > 20:
                    job = JobImportRequest(
                        platform_id=job.platform_id,
                        platform_job_id=job.platform_job_id,
                        source_url=job.source_url,
                        raw_content=job.raw_content + "\n\n" + detail_text,
                        language=job.language,
                    )
            except Exception:
                logger.debug("Lagou: detail failed for %s", job.source_url)

            enriched.append(job)
            await page.wait_for_timeout(random.randint(2000, 4000))

        return enriched


def _extract_job_id(url: str | None, text: str) -> str:
    if url:
        m = re.search(r"/jobs?/(\d+)", url)
        if m:
            return m.group(1)
    return hashlib.md5(text.encode()).hexdigest()[:16]


lagou_collector = register(LagouCollector())
