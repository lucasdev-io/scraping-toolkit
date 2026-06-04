"""
example_browser_ua_rotation.py

Demonstrates how browser_utils handles anti-scraping measures:
  - User-Agent rotation across Chrome 131 fingerprints
  - Automatic context rebuild on HTTP 403
  - Locale / timezone spoofing for Taiwan-targeted sites

Part of lucasdev-io/scraping-toolkit
"""

import asyncio
from playwright.async_api import async_playwright
from scraping_toolkit.browser_utils import make_browser_context, fetch_with_retry


async def main():
    target_url = "https://example-ticketing-site.com/events/some-event"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        # Build a context with randomised UA + Taiwan locale
        context = await make_browser_context(
            browser,
            referer="https://example-ticketing-site.com/",
            locale="zh-TW",
            timezone_id="Asia/Taipei",
        )
        page = await context.new_page()

        # fetch_with_retry handles 403 automatically:
        #   1. Detects 403 response
        #   2. Waits 15 seconds
        #   3. Spawns a new context with a different UA
        #   4. Retries the request once
        title, body = await fetch_with_retry(page, target_url, wait=15)

        if title and body:
            print(f"✅ Page fetched: {title}")
            print(f"   Body preview: {body[:200]}")
        else:
            print("❌ Failed after retry — page may require login or JS challenge")

        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
