#!/usr/bin/env python3
"""Re-enrich existing short Boss/Liepin JDs by attaching to user's real Chrome.

Why CDP attach instead of launching Playwright Chromium:
- Boss/Liepin reject Playwright-launched browsers via fingerprint detection
  (navigator.webdriver + many other automation signals), so the captcha
  component refuses interaction. Even with --disable-blink-features=
  AutomationControlled.
- User's real Chrome has a clean fingerprint. Once user logs in there,
  this script reuses that session via CDP — Boss/Liepin see a real human
  session and let detail pages render normally.

Prerequisite (user action):
    open -na "Google Chrome" --args \
        --remote-debugging-port=9222 \
        --user-data-dir="$HOME/.chrome-scrape"
    # then in that Chrome window: log into zhipin.com + liepin.com

Then run:
    cd backend && .venv/bin/python scripts/reenrich_boss_liepin.py
    cd backend && .venv/bin/python scripts/reenrich_boss_liepin.py --limit 5
    cd backend && .venv/bin/python scripts/reenrich_boss_liepin.py --platform liepin

Saves JD body text appended to job.raw_content. Resumable: skips jobs
whose raw_content already exceeds --min-length (default 250 chars).
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.async_api import async_playwright
from sqlalchemy import func, select

from app.database import async_session
from app.models.job import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CDP_URL = "http://localhost:9222"

# Per-platform JD body selectors. Ordered: tries first, fallback to later.
# Reverse-engineered from real Chrome inspection of zhipin.com / liepin.com.
# We pick the smallest element containing the responsibility keywords so
# we don't grab the entire page.
SELECTORS = {
    "boss_zhipin": [
        ".job-sec-text",
        ".job-detail-section .text",
        '[class*="job-sec"] .text',
        '[class*="detail-content"]',
        '[class*="job-detail"] [class*="text"]',
    ],
    "liepin": [
        ".job-intro-content",
        ".dia-content",
        '[class*="job-intro"]',
        '[class*="job-description"]',
        '[class*="responsibility"]',
        '[data-selector*="job-intro"]',
    ],
}

# JS that walks DOM and returns the smallest leaf containing JD body keywords.
# Used as a final fallback when known selectors don't match.
KEYWORD_FALLBACK_JS = r"""
() => {
  const keywords = /(职责|要求|岗位描述|职位描述|工作内容|任职资格|Responsibilities|Requirements|What you|Job Description|About the role|We are looking)/i;
  let best = null;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  let node;
  while ((node = walker.nextNode())) {
    const txt = node.innerText || node.textContent || '';
    const trimmed = txt.trim();
    if (trimmed.length < 100 || trimmed.length > 8000) continue;
    if (!keywords.test(trimmed)) continue;
    // require it not have a child that also matches (prefer smaller container)
    let childMatch = false;
    for (const c of node.children) {
      const ct = (c.innerText || c.textContent || '').trim();
      if (ct.length > 100 && ct.length < trimmed.length * 0.95 && keywords.test(ct)) {
        childMatch = true;
        break;
      }
    }
    if (childMatch) continue;
    if (!best || trimmed.length < best.length) {
      best = trimmed;
    }
  }
  return best;
}
"""


async def extract_body(page, platform_id: str) -> str | None:
    """Try platform-specific selectors first, then keyword-fallback walker.

    For selectors that have multiple matches (Boss has both 职位描述
    .job-sec-text and 公司介绍 .job-sec-text), pick the longest match.
    """
    for sel in SELECTORS.get(platform_id, []):
        try:
            handles = await page.query_selector_all(sel)
            best = ""
            for h in handles:
                try:
                    txt = (await h.inner_text()).strip()
                    if len(txt) > len(best):
                        best = txt
                except Exception:
                    continue
            if len(best) >= 100:
                return best
        except Exception:
            continue
    try:
        text = await page.evaluate(KEYWORD_FALLBACK_JS)
        if text and len(text) >= 100:
            return text
    except Exception:
        pass
    return None


def _url_changed_job_id(original: str, final: str) -> bool:
    """Boss closed jobs redirect to a similar but different job_id.
    Returns True when the path's job id portion has changed.
    Tolerates trailing query / fragment differences and login-callback URLs.
    """
    if not original or not final:
        return False
    import re
    # Boss: /job_detail/<id>.html
    m1 = re.search(r"/job_detail/([^./?]+)", original)
    m2 = re.search(r"/job_detail/([^./?]+)", final)
    if m1 and m2:
        return m1.group(1) != m2.group(1)
    # Liepin: /a/<id>.shtml  or /job/<id>.shtml
    m1l = re.search(r"/(?:a|job)/(\d+)\.shtml", original)
    m2l = re.search(r"/(?:a|job)/(\d+)\.shtml", final)
    if m1l and m2l:
        return m1l.group(1) != m2l.group(1)
    return False


async def detect_captcha(page) -> bool:
    """Detect anti-bot challenge pages so we can pause for user to solve."""
    try:
        url = page.url
        if "security-check" in url or "verify" in url or "captcha" in url.lower():
            return True
        # Boss: 滑动验证 / 极验
        body = await page.evaluate(
            "() => document.body ? (document.body.innerText || '').slice(0, 2000) : ''"
        )
        if "请完成安全验证" in body or "拖动滑块" in body or "滑动验证" in body:
            return True
    except Exception:
        pass
    return False


async def reenrich(limit: int | None, platform: str | None, min_length: int):
    async with async_playwright() as p:
        logger.info("Connecting to Chrome at %s ...", CDP_URL)
        try:
            browser = await p.chromium.connect_over_cdp(CDP_URL, timeout=5000)
        except Exception as e:
            logger.error(
                "Cannot connect to Chrome on port 9222: %s\n"
                "Launch it with:\n"
                '    open -na "Google Chrome" --args --remote-debugging-port=9222 '
                '--user-data-dir="$HOME/.chrome-scrape"',
                e,
            )
            return

        # Reuse the existing context so we get user's cookies.
        contexts = browser.contexts
        if not contexts:
            logger.error("Chrome has no open contexts — open a tab first")
            return
        context = contexts[0]
        page = await context.new_page()
        logger.info(
            "Connected: %d context(s), %d existing tab(s). Opened a new tab.",
            len(contexts),
            sum(len(c.pages) for c in contexts) - 1,
        )

        # Pull short Boss/Liepin jobs from DB
        async with async_session() as db:
            stmt = select(Job).where(
                Job.parse_status == "parsed",
                Job.source_url.isnot(None),
                func.length(Job.raw_content) < min_length,
            )
            if platform:
                stmt = stmt.where(Job.platform_id == platform)
            else:
                stmt = stmt.where(Job.platform_id.in_(["boss_zhipin", "liepin"]))
            stmt = stmt.order_by(Job.platform_id, Job.id)
            if limit:
                stmt = stmt.limit(limit)

            jobs = (await db.execute(stmt)).scalars().all()
            logger.info("Found %d short jobs to re-enrich", len(jobs))

            ok = skipped = failed = captcha_pauses = redirected = 0
            for i, job in enumerate(jobs, start=1):
                try:
                    response = await page.goto(
                        job.source_url, wait_until="domcontentloaded", timeout=20000
                    )
                except Exception as e:
                    logger.warning("[%d/%d] %s — navigation failed: %s",
                                   i, len(jobs), job.platform_job_id, str(e)[:80])
                    failed += 1
                    continue

                # Detect URL rewrites: Boss redirects closed jobs to a similar
                # one with a DIFFERENT job_id. Save body for the wrong job_id
                # would corrupt our data. Compare path segment.
                final_url = page.url
                if _url_changed_job_id(job.source_url, final_url):
                    logger.info(
                        "[%d/%d] %s — redirected to different job, skipping",
                        i, len(jobs), job.platform_job_id,
                    )
                    redirected += 1
                    continue

                # Wait a beat for client-side render. Boss sometimes paints
                # JD body after a short delay; give it up to 6s by polling
                # for the first platform selector.
                primary = SELECTORS.get(job.platform_id, [None])[0]
                if primary:
                    try:
                        await page.wait_for_selector(primary, timeout=6000)
                    except Exception:
                        pass
                await asyncio.sleep(1.0)

                if await detect_captcha(page):
                    captcha_pauses += 1
                    logger.warning(
                        "[%d/%d] CAPTCHA on %s — pausing 60s for you to solve it",
                        i, len(jobs), job.source_url,
                    )
                    await asyncio.sleep(60)
                    # try again once
                    if await detect_captcha(page):
                        logger.warning("  captcha unresolved — skipping")
                        failed += 1
                        continue

                body = await extract_body(page, job.platform_id)
                # Detect "page does not exist" / "offline" Boss page so we
                # mark the job and don't waste a network round-trip on it
                # next run.
                page_body = await page.evaluate(
                    "() => (document.body && document.body.innerText) ? "
                    "document.body.innerText.slice(0, 500) : ''"
                )
                is_offline = bool(
                    page_body
                    and (
                        "页面不存在" in page_body
                        or "Oops" in page_body
                        or "职位已关闭" in page_body
                    )
                )
                if not body:
                    if is_offline:
                        # Append a marker so next run skips this URL — its
                        # raw_content moves above --min-length threshold.
                        job.raw_content = (
                            (job.raw_content or "").rstrip()
                            + "\n\n--- detail unavailable ---\n"
                            + "[job offline on source platform — JD body not recoverable]"
                        )
                    logger.info(
                        "[%d/%d] %s — %s",
                        i, len(jobs), job.platform_job_id,
                        "OFFLINE (marked)" if is_offline else "no JD body found",
                    )
                    skipped += 1
                else:
                    # Append to existing raw_content. Keep the original list-page
                    # snippet too — it has salary / location / company info that
                    # the detail page may format differently.
                    job.raw_content = (
                        (job.raw_content or "").rstrip()
                        + "\n\n--- detail ---\n"
                        + body
                    )
                    ok += 1

                if i % 25 == 0:
                    await db.commit()
                    logger.info(
                        "[%d/%d] batch — ok=%d skipped=%d failed=%d redirected=%d captchas=%d",
                        i, len(jobs), ok, skipped, failed, redirected, captcha_pauses,
                    )

                # Slow rate to avoid triggering rate-based bot detection
                delay = random.uniform(3.0, 7.0)
                await asyncio.sleep(delay)

            await db.commit()
            logger.info(
                "Done — total=%d ok=%d skipped=%d failed=%d redirected=%d captchas_seen=%d",
                len(jobs), ok, skipped, failed, redirected, captcha_pauses,
            )

        await page.close()
        # Don't close the browser — it's the user's Chrome.


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None,
                        help="cap on JDs to process (for smoke test)")
    parser.add_argument("--platform", choices=["boss_zhipin", "liepin"],
                        default=None, help="default: both")
    parser.add_argument("--min-length", type=int, default=250,
                        help="skip JDs whose raw_content already exceeds this")
    args = parser.parse_args()
    await reenrich(args.limit, args.platform, args.min_length)


if __name__ == "__main__":
    asyncio.run(main())
