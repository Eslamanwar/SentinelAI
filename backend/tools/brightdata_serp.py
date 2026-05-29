import json
from urllib.parse import quote_plus

import httpx
from langchain_core.tools import tool

from config import settings


@tool
async def search_web(query: str, num_results: int = 10) -> str:
    """Search the web using Bright Data SERP API. Use this to find CVEs, security advisories,
    breach announcements, credential leaks, vendor incidents, and regulatory changes.
    Returns search results with titles, URLs, and snippets."""
    search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}&brd_json=1"

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.brightdata.com/request",
            headers={
                "Authorization": f"Bearer {settings.brightdata_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "zone": settings.brightdata_serp_zone,
                "url": search_url,
                "format": "raw",
            },
        )
        response.raise_for_status()

        try:
            data = response.json()
        except json.JSONDecodeError:
            content = response.text
            if len(content) > 5000:
                content = content[:5000]
            return content

        results = []
        organic = data.get("organic", data.get("results", []))
        if isinstance(organic, list):
            for item in organic:
                results.append(
                    f"Title: {item.get('title', 'N/A')}\n"
                    f"URL: {item.get('link', item.get('url', 'N/A'))}\n"
                    f"Snippet: {item.get('snippet', item.get('description', 'N/A'))}\n"
                )

        return "\n---\n".join(results) if results else f"Raw: {response.text[:3000]}"
