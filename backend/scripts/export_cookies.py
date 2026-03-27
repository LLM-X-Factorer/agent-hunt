#!/usr/bin/env python3
"""Open a browser for manual login, then export cookies for collectors.

Usage:
    python scripts/export_cookies.py boss_zhipin
    python scripts/export_cookies.py lagou

The script opens a headed Chromium browser. Log in manually, then press
Enter in the terminal to save cookies and close the browser.
"""
import asyncio
import json
import sys
from pathlib import Path

from playwright.async_api import async_playwright

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

PLATFORMS = {
    "boss_zhipin": {
        "url": "https://www.zhipin.com/web/user/?ka=header-login",
        "cookie_file": "boss_cookies.json",
        "verify_url": "https://www.zhipin.com/web/geek/job?query=AI&city=100010000",
    },
    "lagou": {
        "url": "https://passport.lagou.com/login/login.html",
        "cookie_file": "lagou_cookies.json",
        "verify_url": "https://www.lagou.com/wn/zhaopin?kd=AI",
    },
}


async def main(platform_id: str):
    if platform_id not in PLATFORMS:
        print(f"Supported platforms: {', '.join(PLATFORMS)}")
        sys.exit(1)

    config = PLATFORMS[platform_id]
    cookie_path = DATA_DIR / config["cookie_file"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
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

        print(f"\n{'='*60}")
        print(f"  Platform: {platform_id}")
        print(f"  Opening: {config['url']}")
        print(f"  Cookie will be saved to: {cookie_path}")
        print(f"{'='*60}")
        print("\n  1. Log in manually in the browser window")
        print("  2. After login succeeds, come back here and press Enter")
        print()

        await page.goto(config["url"], wait_until="domcontentloaded")

        input("  >>> Press Enter after you have logged in... ")

        cookies = await context.cookies()
        cookie_data = {"cookies": cookies}

        cookie_path.parent.mkdir(parents=True, exist_ok=True)
        cookie_path.write_text(
            json.dumps(cookie_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\n  Saved {len(cookies)} cookies to {cookie_path}")

        # Verify by navigating to search page
        print(f"  Verifying login at {config['verify_url']}...")
        await page.goto(config["verify_url"], wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        title = await page.title()
        print(f"  Page title: {title}")

        await browser.close()

    print(f"\n  Done! You can now use the {platform_id} collector.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <platform_id>")
        print(f"Supported: {', '.join(PLATFORMS)}")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
