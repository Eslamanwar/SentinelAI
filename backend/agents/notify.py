import logging
from datetime import datetime, timezone

from graph.state import SentinelState
from integrations.jira import create_jira_ticket
from integrations.slack import send_slack_alert

logger = logging.getLogger(__name__)


async def notify_node(state: SentinelState) -> dict:
    plans = state.get("remediation_plans", [])
    scores = state.get("risk_scores", [])
    investigation_id = state.get("investigation_id", "")
    target = state.get("target", "")

    notifications = []

    score_map = {s.get("threat_id"): s for s in scores}

    for plan in plans:
        threat_id = plan.get("threat_id", "")
        score = score_map.get(threat_id, {})
        severity = plan.get("priority", "high")
        risk_score = score.get("score", 0)

        title = plan.get("title", "Security threat detected")
        commands = plan.get("commands", [])
        commands_text = "\n".join(commands[:5]) if commands else "See full plan for details"

        details = (
            f"Target: {target}\n"
            f"Risk Score: {risk_score}/100\n"
            f"Blast Radius: {score.get('blast_radius', 'Unknown')}\n"
            f"Steps:\n" + "\n".join(f"  {i+1}. {s}" for i, s in enumerate(plan.get("steps", [])[:5]))
        )

        slack_sent = await send_slack_alert(
            title=title,
            severity=severity,
            details=details,
            remediation=commands_text,
            investigation_id=investigation_id,
        )

        jira_result = await create_jira_ticket(
            title=title,
            description=f"{details}\n\nRemediation Commands:\n{commands_text}",
            priority=severity,
            labels=["sentinel-ai", "security", severity],
        )

        notifications.append({
            "threat_id": threat_id,
            "slack_sent": slack_sent,
            "jira_ticket": jira_result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    trace_entry = {
        "agent": "notify",
        "action": "notifications_sent",
        "detail": (
            f"Sent {sum(1 for n in notifications if n['slack_sent'])} Slack alerts, "
            f"created {sum(1 for n in notifications if n['jira_ticket'])} Jira tickets"
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "notifications_sent": notifications,
        "status": "complete",
        "agent_trace": [trace_entry],
    }
