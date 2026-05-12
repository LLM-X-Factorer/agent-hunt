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
        # cookie name that only exists after successful login (geek session token)
        "auth_cookie": "wt2",
    },
    "lagou": {
        "url": "https://passport.lagou.com/login/login.html",
        "cookie_file": "lagou_cookies.json",
        "verify_url": "https://www.lagou.com/wn/zhaopin?kd=AI",
        "auth_cookie": "_putrc",
    },
    "liepin": {
        "url": "https://passport.liepin.com/h5login",
        "cookie_file": "liepin_cookies.json",
        "verify_url": "https://www.liepin.com/zhaopin/?key=AI",
        "auth_cookie": "__uuid",
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

        print(f"\n{'='*60}", flush=True)
        print(f"  Platform: {platform_id}", flush=True)
        print(f"  Opening: {config['url']}", flush=True)
        print(f"  Cookie will be saved to: {cookie_path}", flush=True)
        print(f"{'='*60}", flush=True)
        print("\n  Log in manually in the browser window.", flush=True)
        print(
            "  Script will auto-detect login completion via cookie %r."
            % config["auth_cookie"],
            flush=True,
        )
        print("  Timeout: 4 minutes.", flush=True)
        print("", flush=True)

        await page.goto(config["url"], wait_until="domcontentloaded")

        # Poll for the auth cookie. No stdin required.
        auth_name = config["auth_cookie"]
        max_wait = 240  # seconds
        interval = 3
        elapsed = 0
        found = False
        while elapsed < max_wait:
            cookies = await context.cookies()
            names = {c["name"] for c in cookies}
            if auth_name in names:
                found = True
                break
            await asyncio.sleep(interval)
            elapsed += interval
            print(
                f"  ... waiting for {auth_name} cookie ({elapsed}s/{max_wait}s)",
                flush=True,
            )

        if not found:
            print(
                f"  ✗ Timeout — {auth_name} cookie never appeared. "
                "Login may not have completed.",
                flush=True,
            )
            await browser.close()
            sys.exit(2)

        cookies = await context.cookies()
        cookie_data = {"cookies": cookies}

        cookie_path.parent.mkdir(parents=True, exist_ok=True)
        cookie_path.write_text(
            json.dumps(cookie_data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(
            f"\n  ✓ Detected {auth_name} — saved {len(cookies)} cookies to {cookie_path}",
            flush=True,
        )

        # Verify by navigating to search page
        print(f"  Verifying login at {config['verify_url']}...", flush=True)
        await page.goto(config["verify_url"], wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        title = await page.title()
        print(f"  Page title: {title}", flush=True)

        await browser.close()

    print(f"\n  Done! You can now use the {platform_id} collector.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <platform_id>")
        print(f"Supported: {', '.join(PLATFORMS)}")
        sys.exit(1)

    asyncio.run(main(sys.argv[1]))
