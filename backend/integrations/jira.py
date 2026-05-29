import logging
from base64 import b64encode
from typing import Any, Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


async def create_jira_ticket(
    title: str,
    description: str,
    priority: str = "High",
    labels: list[str] | None = None,
) -> Optional[dict]:
    if not settings.jira_base_url or not settings.jira_api_token:
        logger.info(f"Jira not configured, skipping ticket: {title}")
        return None

    priority_map = {
        "critical": "Highest",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "info": "Lowest",
    }

    payload = {
        "fields": {
            "project": {"key": settings.jira_project_key},
            "summary": f"[SentinelAI] {title}",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}],
                    }
                ],
            },
            "issuetype": {"name": "Bug"},
            "priority": {"name": priority_map.get(priority, "High")},
            "labels": labels or ["sentinel-ai", "security"],
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{settings.jira_base_url}/rest/api/3/issue",
                headers={
                    "Authorization": f"Bearer {settings.jira_api_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"Jira ticket created: {result.get('key')}")
            return {"key": result.get("key"), "url": f"{settings.jira_base_url}/browse/{result.get('key')}"}
    except Exception as e:
        logger.error(f"Failed to create Jira ticket: {e}")
        return None
