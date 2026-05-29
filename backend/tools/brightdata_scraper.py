import httpx
from langchain_core.tools import tool

from config import settings


@tool
async def extract_structured_data(url: str, extraction_prompt: str) -> str:
    """Extract structured data from a web page using Bright Data Web Scraper API.
    Use for CVE databases, compliance registries, vendor incident pages.
    Provide a URL and an extraction prompt describing what data to extract.
    Returns clean structured JSON data."""
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            settings.brightdata_web_unlocker_url,
            headers={
                "Authorization": f"Bearer {settings.brightdata_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "url": url,
                "format": "json",
                "data_extraction": {
                    "instructions": extraction_prompt,
                },
            },
        )
        response.raise_for_status()
        return response.text
