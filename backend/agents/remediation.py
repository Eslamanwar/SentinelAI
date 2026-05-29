import json
import logging
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage

from graph.llm import get_llm
from graph.state import SentinelState

logger = logging.getLogger(__name__)

REMEDIATION_PROMPT = """You are an SRE remediation agent. Given high-severity threats with their
risk scores and environment context, generate actionable remediation plans.

For each threat, provide:
1. Exact kubectl commands to patch, upgrade, or roll back
2. Terraform code changes if AWS resources are affected
3. Helm chart version bumps with the correct chart and version
4. Container image upgrade paths
5. Network policy or WAF rule changes if applicable

Return a JSON array of remediation plans:
- threat_id: ID of the threat being remediated
- title: short title for the remediation
- priority: "critical", "high", "medium", or "low"
- steps: list of human-readable steps
- commands: list of exact CLI commands to execute (kubectl, terraform, helm, aws cli)
- terraform_changes: HCL code snippet if applicable (or null)
- estimated_effort: "minutes", "hours", or "days"

Be specific. Use exact version numbers, image tags, and resource names from the environment."""


async def remediation_node(state: SentinelState) -> dict:
    scores = state.get("risk_scores", [])
    correlated = state.get("correlated_threats", [])
    threats = state.get("discovered_threats", [])
    env = state.get("environment_inventory", {})

    high_severity = [s for s in scores if s.get("score", 0) >= 70]
    if not high_severity:
        return {
            "remediation_plans": [],
            "agent_trace": [{
                "agent": "remediation",
                "action": "no_remediation_needed",
                "detail": "No high-severity threats to remediate",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        }

    context = f"""## High-Severity Threats Requiring Remediation
{json.dumps(high_severity, indent=2, default=str)}

## Correlated Threat Details
{json.dumps(correlated, indent=2, default=str)}

## Original Threat Data
{json.dumps(threats, indent=2, default=str)}

## Environment
- Kubernetes clusters: {json.dumps(env.get('kubernetes', {}).get('clusters', []), indent=2, default=str)}

Generate specific, actionable remediation plans for each high-severity threat."""

    llm = get_llm()
    messages = [SystemMessage(content=REMEDIATION_PROMPT), HumanMessage(content=context)]
    response = await llm.ainvoke(messages)

    plans = []
    try:
        content = response.content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "[" in content:
            json_str = content[content.index("["):content.rindex("]") + 1]
        else:
            json_str = "[]"
        plans = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to parse remediation output")

    trace_entry = {
        "agent": "remediation",
        "action": "plans_generated",
        "detail": f"Generated {len(plans)} remediation plans",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "remediation_plans": plans,
        "agent_trace": [trace_entry],
    }
