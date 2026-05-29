import logging
import uuid
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from agents._utils import collect_tool_results, parse_json_array
from graph.llm import get_llm
from graph.state import SentinelState
from tools.brightdata_serp import search_web
from tools.brightdata_unlocker import fetch_page

logger = logging.getLogger("sentinel")

DISCOVERY_SYSTEM_PROMPT = """You are a threat intelligence analyst. Your job is to search the open web
for security threats relevant to a specific organization and its infrastructure.

You have access to:
- search_web: Search the web via Bright Data SERP API
- fetch_page: Fetch full page content via Bright Data Web Unlocker

Search for:
1. Kubernetes CVEs affecting the organization's cluster versions
2. AWS security advisories relevant to their services
3. GitHub Security Advisories for dependencies
4. Recent security incidents or breaches mentioning the organization
5. New CVEs in the last 30 days for software they run

IMPORTANT: After gathering information, you MUST return your final answer as a JSON array.
Each object must have: threat_type, title, description, severity, source_url, cve_id (if applicable), affected_versions.
Wrap the JSON in ```json``` code fences."""

TOOLS = [search_web, fetch_page]


async def discovery_node(state: SentinelState) -> dict:
    target = state["target"]
    domain = state.get("target_domain", "")
    env = state.get("environment_inventory", {})

    k8s_versions = []
    for cluster in env.get("kubernetes", {}).get("clusters", []):
        k8s_versions.append(f"{cluster['name']}: {cluster['version']}")

    context = f"""Investigate threats for: {target}
Domain: {domain}

Kubernetes clusters:
{chr(10).join(k8s_versions) if k8s_versions else "No cluster data available"}

Search for recent CVEs, security advisories, and threats that could affect this environment.
Focus on actionable, high-severity findings."""

    llm = get_llm().bind_tools(TOOLS)
    messages = [SystemMessage(content=DISCOVERY_SYSTEM_PROMPT), HumanMessage(content=context)]

    for _ in range(5):
        response = await llm.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        for tc in response.tool_calls:
            if tc["name"] == "search_web":
                result = await search_web.ainvoke(tc["args"])
            elif tc["name"] == "fetch_page":
                result = await fetch_page.ainvoke(tc["args"])
            else:
                result = f"Unknown tool: {tc['name']}"
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    # Check if final message has JSON already
    final_content = ""
    if messages and hasattr(messages[-1], "content") and messages[-1].content:
        final_content = messages[-1].content

    # If the last message is a tool result or the AI didn't produce JSON, do a clean summarization call
    if isinstance(messages[-1], ToolMessage) or "[" not in final_content:
        gathered = collect_tool_results(messages)
        summary_messages = [
            SystemMessage(content="You are a threat analyst. Given the raw research data below, compile a JSON array of threats found. Each object needs: threat_type, title, description, severity, source_url, cve_id, affected_versions. Wrap in ```json``` fences."),
            HumanMessage(content=f"Target: {target}\n\nRaw research data:\n{gathered[:12000]}"),
        ]
        llm_plain = get_llm()
        response = await llm_plain.ainvoke(summary_messages)
        final_content = response.content

    logger.info(f"Discovery raw output length: {len(final_content)}")

    discovered = parse_json_array(final_content)
    for t in discovered:
        t["id"] = str(uuid.uuid4())
        t["discovered_at"] = datetime.now(timezone.utc).isoformat()

    logger.info(f"Discovery parsed {len(discovered)} threats for {target}")

    return {
        "discovered_threats": discovered,
        "agent_trace": [{
            "agent": "discovery",
            "action": "scan_complete",
            "detail": f"Found {len(discovered)} threats for {target}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }
