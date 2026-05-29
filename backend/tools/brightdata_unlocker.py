import httpx
from langchain_core.tools import tool

from config import settings


@tool
async def fetch_page(url: str) -> str:
    """Fetch a web page using Bright Data Web Unlocker. Bypasses anti-bot protections.
    Use for accessing NVD, AWS bulletins, vendor security portals, paste sites,
    and regulatory body websites that block standard requests.
    Returns the page content as text."""
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.brightdata.com/request",
            headers={
                "Authorization": f"Bearer {settings.brightdata_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "zone": settings.brightdata_unlocker_zone,
                "url": url,
                "format": "raw",
            },
        )
        response.raise_for_status()
        content = response.text

        if len(content) > 15000:
            content = content[:15000] + "\n\n[Content truncated at 15000 chars]"

        return content
