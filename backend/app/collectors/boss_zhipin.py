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

COOKIES_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "boss_cookies.json"
SEARCH_URL = "https://www.zhipin.com/web/geek/job?query={keyword}&city=100010000"

# Boss 直聘薪资字体加密映射（自定义 Unicode codepoint → 数字）
SALARY_FONT_MAP = {
    chr(0xE031): "0", chr(0xE032): "1", chr(0xE033): "2",
    chr(0xE034): "3", chr(0xE035): "4", chr(0xE036): "5",
    chr(0xE037): "6", chr(0xE038): "7", chr(0xE039): "8",
    chr(0xE03A): "9",
}


def _decode_salary(text: str) -> str:
    for enc, dec in SALARY_FONT_MAP.items():
        text = text.replace(enc, dec)
    return text


class BossZhipinCollector(BaseCollector):

    @property
    def platform_id(self) -> str:
        return "boss_zhipin"

    async def collect(
        self, keyword: str, max_pages: int = 5
    ) -> list[JobImportRequest]:
        if not COOKIES_PATH.exists():
            logger.error(
                "Boss直聘需要登录 Cookie。请先手动登录后导出 Cookie 到 %s\n"
                "格式: {\"cookies\": [playwright cookie array]}",
                COOKIES_PATH,
            )
            return []

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

            # Load cookies
            cookie_data = json.loads(COOKIES_PATH.read_text(encoding="utf-8"))
            await context.add_cookies(cookie_data["cookies"])

            page = await context.new_page()
            url = SEARCH_URL.format(keyword=keyword)
            logger.info("Boss直聘: navigating to %s", url)

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)
            except Exception:
                logger.error("Boss直聘: failed to load search page")
                await browser.close()
                return []

            # Scroll to load more jobs
            scroll_rounds = min(max_pages, 10)
            for i in range(scroll_rounds):
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await page.wait_for_timeout(random.randint(2000, 5000))
                logger.info("Boss直聘: scroll %d/%d", i + 1, scroll_rounds)

            # Extract job cards
            card_data = await page.evaluate("""() => {
                const cards = document.querySelectorAll('.job-card-wrapper, .job-card-left, [class*="job-card"]');
                let results = [];
                let seen = new Set();
                for (const card of cards) {
                    const link = card.querySelector('a[href*="/job_detail"]');
                    if (!link) continue;
                    const href = link.href;
                    if (seen.has(href)) continue;
                    seen.add(href);
                    const text = card.textContent.trim();
                    results.push({href, text});
                }
                return results;
            }""")

            logger.info("Boss直聘: found %d job cards", len(card_data))

            for item in card_data:
                job = self._parse_card(item)
                if job:
                    jobs.append(job)

            # Enrich with detail pages
            jobs = await self._enrich_with_details(page, jobs)
            await browser.close()

        logger.info("Boss直聘: collected %d jobs for %r", len(jobs), keyword)
        return jobs

    def _parse_card(self, item: dict) -> JobImportRequest | None:
        text = item.get("text", "").strip()
        href = item.get("href", "")

        if not text or len(text) < 10:
            return None

        text = _decode_salary(text)

        source_url = href.split("?")[0] if href else None
        platform_job_id = _extract_job_id(source_url, text)

        return JobImportRequest(
            platform_id="boss_zhipin",
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
                        '.job-detail-section .text',
                        '.job-sec-text',
                        '.job-detail .text',
                        '[class*="job-detail"] [class*="text"]',
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
                    detail_text = _decode_salary(detail_text)
                    job = JobImportRequest(
                        platform_id=job.platform_id,
                        platform_job_id=job.platform_job_id,
                        source_url=job.source_url,
                        raw_content=job.raw_content + "\n\n" + detail_text,
                        language=job.language,
                    )
            except Exception:
                logger.debug("Boss直聘: detail failed for %s", job.source_url)

            enriched.append(job)
            delay = random.randint(3000, 8000)
            await page.wait_for_timeout(delay)

        return enriched


def _extract_job_id(url: str | None, text: str) -> str:
    if url:
        m = re.search(r"/job_detail/([^./?]+)", url)
        if m:
            return m.group(1)
    return hashlib.md5(text.encode()).hexdigest()[:16]


boss_zhipin_collector = register(BossZhipinCollector())
