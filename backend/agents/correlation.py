import json
import logging
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger("sentinel")

from env_parsers.k8s_inventory import format_inventory_for_llm
from env_parsers.terraform_parser import format_state_for_llm
from graph.llm import get_llm
from graph.state import SentinelState

logger = logging.getLogger(__name__)

CORRELATION_PROMPT = """You are an infrastructure security correlation engine.
Given a list of discovered threats and the organization's environment inventory,
determine which threats actually affect this specific environment.

For each threat, check:
1. Does the CVE affect a Kubernetes version running in any cluster?
2. Does the vulnerability affect any deployed container image?
3. Does the advisory apply to any AWS resource in the Terraform state?
4. Is the affected vendor in the organization's vendor list?

Return a JSON array of correlated threats:
- threat_id: ID of the original threat
- environment_match: true/false
- affected_resources: list of {resource_type, resource_name, cluster, namespace} objects
- match_details: explanation of why this threat matches (or doesn't)

Only include threats that have environment_match: true."""


async def correlation_node(state: SentinelState) -> dict:
    threats = state.get("discovered_threats", [])
    env = state.get("environment_inventory", {})

    logger.info(f"Correlation received {len(threats)} threats to correlate")

    if not threats:
        logger.info("Correlation: no threats to correlate, skipping")
        return {
            "correlated_threats": [],
            "agent_trace": [{
                "agent": "correlation",
                "action": "no_threats",
                "detail": "No threats to correlate",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }],
        }

    k8s_summary = format_inventory_for_llm(env.get("kubernetes", {}))
    tf_summary = format_state_for_llm(env.get("terraform", {}))

    threats_text = json.dumps(threats, indent=2, default=str)

    context = f"""## Discovered Threats
{threats_text}

## Environment Inventory
{k8s_summary}

{tf_summary}

Correlate each threat against the environment. Which threats actually affect this infrastructure?"""

    llm = get_llm()
    messages = [SystemMessage(content=CORRELATION_PROMPT), HumanMessage(content=context)]
    response = await llm.ainvoke(messages)

    correlated = []
    try:
        content = response.content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "[" in content:
            json_str = content[content.index("["):content.rindex("]") + 1]
        else:
            json_str = "[]"
        correlated = json.loads(json_str)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to parse correlation output")

    matched_count = len([c for c in correlated if c.get("environment_match")])
    trace_entry = {
        "agent": "correlation",
        "action": "correlation_complete",
        "detail": f"Correlated {len(threats)} threats: {matched_count} match environment",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "correlated_threats": correlated,
        "agent_trace": [trace_entry],
    }
