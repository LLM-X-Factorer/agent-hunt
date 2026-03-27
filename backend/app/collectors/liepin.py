from __future__ import annotations

import hashlib
import logging
import random
import re

from playwright.async_api import async_playwright

from app.collectors.base import BaseCollector
from app.collectors.registry import register
from app.schemas.job import JobImportRequest

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.liepin.com/zhaopin/?key={keyword}&curPage={page}"


class LiepinCollector(BaseCollector):

    @property
    def platform_id(self) -> str:
        return "liepin"

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
            page = await context.new_page()

            for page_num in range(max_pages):
                url = SEARCH_URL.format(keyword=keyword, page=page_num)
                logger.info("Liepin: fetching page %d — %s", page_num, url)

                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    await page.wait_for_timeout(3000)
                    await page.wait_for_selector(
                        ".job-card-pc-container", timeout=10000
                    )
                except Exception:
                    logger.warning("Liepin: page %d load failed, stopping", page_num)
                    break

                card_data = await page.evaluate("""() => {
                    const cards = document.querySelectorAll('.job-card-pc-container');
                    let results = [];
                    for (const card of cards) {
                        const link = card.querySelector('a[href]');
                        const href = link ? link.href : '';
                        const text = card.textContent.trim();
                        results.push({href, text});
                    }
                    return results;
                }""")

                if not card_data:
                    logger.info("Liepin: no cards on page %d, stopping", page_num)
                    break

                for item in card_data:
                    job = self._parse_card(item)
                    if job:
                        jobs.append(job)

                delay = random.uniform(3, 6)
                logger.info(
                    "Liepin: page %d, %d cards, sleeping %.1fs",
                    page_num, len(card_data), delay,
                )
                await page.wait_for_timeout(int(delay * 1000))

            # Enrich with detail pages
            jobs = await self._enrich_with_details(page, jobs)
            await browser.close()

        logger.info("Liepin: collected %d jobs for %r", len(jobs), keyword)
        return jobs

    def _parse_card(self, item: dict) -> JobImportRequest | None:
        text = item.get("text", "").strip()
        href = item.get("href", "")

        if not text or len(text) < 10:
            return None

        source_url = href.split("?")[0] if href else None
        if source_url and not source_url.startswith("http"):
            source_url = f"https://www.liepin.com{source_url}"

        platform_job_id = _extract_job_id(source_url, text)

        return JobImportRequest(
            platform_id="liepin",
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
                        '.job-intro-container',
                        '.job-detail-container',
                        '.job-item-des',
                        '[class*="job-intro"]',
                        '[class*="job-detail"]',
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
                logger.debug("Liepin: detail fetch failed for %s", job.source_url)

            enriched.append(job)
            await page.wait_for_timeout(random.randint(2000, 4000))

        return enriched


def _extract_job_id(url: str | None, text: str) -> str:
    if url:
        m = re.search(r"/a/(\d+)\.shtml", url)
        if m:
            return m.group(1)
    return hashlib.md5(text.encode()).hexdigest()[:16]


liepin_collector = register(LiepinCollector())
