import json
import logging
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage

from graph.llm import get_llm
from graph.state import SentinelState

logger = logging.getLogger(__name__)

RISK_ASSESSMENT_PROMPT = """You are an infrastructure risk assessment agent.
Given correlated threats (threats that match the environment), calculate a contextual risk score.

For each correlated threat, assess:
1. Blast radius — how many clusters, services, or resources are affected?
2. Exposure — is the affected component internet-facing or internal-only?
3. Exploitability — is there a known exploit? Is it trivially exploitable?
4. Existing mitigations — are there network policies, WAF rules, or other controls?
5. Data sensitivity — does the affected component handle sensitive data?

Return a JSON array of risk scores:
- threat_id: ID of the threat
- score: 0-100 (0 = no risk, 100 = critical immediate action needed)
- blast_radius: description of impact scope
- exploitability: "trivial", "moderate", "complex", "theoretical"
- is_internet_facing: true/false
- existing_mitigations: list of existing controls
- reasoning: brief explanation of the score

Score guidelines:
- 90-100: Critical — actively exploited, internet-facing, no mitigations
- 70-89: High — known exploits exist, significant blast radius
- 40-69: Medium — potential risk but mitigated or limited exposure
- 0-39: Low — theoretical risk, internal only, well-mitigated"""


async def risk_assessment_node(state: SentinelState) -> dict:
    correlated = state.get("correlated_threats", [])

    if not correlated:
        return {
            "risk_scores": [],
            "agent_trace": [{
                "agent": "risk_assessment",
                "action": "no_correlations",
                "detail": "No correlated threats to score",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        }

    env = state.get("environment_inventory", {})
    context = f"""## Correlated Threats
{json.dumps(correlated, indent=2, default=str)}

## Environment Context
- K8s Clusters: {env.get('summary', {}).get('k8s_clusters', 0)}
- AWS Resources: {env.get('summary', {}).get('tf_resources', 0)}
- Vendors: {env.get('summary', {}).get('vendor_count', 0)}

Score each correlated threat based on its actual impact in this environment."""

    llm = get_llm()
    messages = [SystemMessage(content=RISK_ASSESSMENT_PROMPT), HumanMessage(content=context)]
    response = await llm.ainvoke(messages)

    scores = []
    try:
        content = response.content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "[" in content:
            json_str = content[content.index("["):content.rindex("]") + 1]
        else:
            json_str = "[]"
        scores = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to parse risk assessment output")

    high_count = len([s for s in scores if s.get("score", 0) >= 70])
    trace_entry = {
        "agent": "risk_assessment",
        "action": "scoring_complete",
        "detail": f"Scored {len(scores)} threats: {high_count} high/critical severity",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "risk_scores": scores,
        "agent_trace": [trace_entry],
    }
