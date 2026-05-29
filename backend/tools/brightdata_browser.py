from playwright.async_api import async_playwright
from langchain_core.tools import tool

from config import settings


@tool
async def scrape_dynamic_page(url: str, wait_selector: str = "body") -> str:
    """Scrape a JavaScript-heavy page using Bright Data Scraping Browser.
    Use for GitHub Security Advisories, AWS Health Dashboard, SaaS status pages,
    and any page that requires JavaScript rendering.
    Optionally specify a CSS selector to wait for before extracting content.
    Returns the rendered page content as text."""
    async with async_playwright() as pw:
        browser = await pw.chromium.connect_over_cdp(
            settings.brightdata_scraping_browser_ws
        )
        try:
            page = await browser.new_page()
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_selector(wait_selector, timeout=30000)
            content = await page.content()

            if len(content) > 15000:
                content = content[:15000] + "\n\n[Content truncated at 15000 chars]"

            return content
        finally:
            await browser.close()
