import logging
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)


async def send_slack_alert(
    title: str,
    severity: str,
    details: str,
    remediation: str = "",
    investigation_id: str = "",
) -> bool:
    if not settings.slack_webhook_url:
        logger.info(f"Slack not configured, skipping alert: {title}")
        return False

    severity_emoji = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🔵",
        "info": "⚪",
    }
    emoji = severity_emoji.get(severity, "⚪")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} SentinelAI: {title}",
            },
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Severity:*\n{severity.upper()}"},
                {"type": "mrkdwn", "text": f"*Investigation:*\n{investigation_id[:8]}..."},
            ],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Details:*\n{details[:2000]}"},
        },
    ]

    if remediation:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Remediation:*\n```{remediation[:1500]}```"},
        })

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                settings.slack_webhook_url,
                json={"blocks": blocks},
            )
            response.raise_for_status()
            logger.info(f"Slack alert sent: {title}")
            return True
    except Exception as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False
