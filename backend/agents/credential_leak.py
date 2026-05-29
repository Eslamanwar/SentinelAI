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

CREDENTIAL_LEAK_PROMPT = """You are a credential leak analyst. Your job is to search the open web
for leaked credentials, API keys, tokens, and sensitive data belonging to a specific organization.

You have access to:
- search_web: Search the web via Bright Data SERP API
- fetch_page: Fetch full page content via Bright Data Web Unlocker

Search for:
1. Paste sites mentioning the organization's domain or email pattern
2. GitHub/GitLab code search for exposed API keys, passwords, tokens
3. Breach database mentions
4. Dark web forum mentions (accessible sources)

IMPORTANT: After gathering information, you MUST return your final answer as a JSON array.
Each object needs: source_url, leak_type, affected_accounts, severity, recommended_action.
Wrap the JSON in ```json``` fences."""

TOOLS = [search_web, fetch_page]


async def credential_leak_node(state: SentinelState) -> dict:
    target = state["target"]
    domain = state.get("target_domain", "")

    context = f"""Search for credential leaks for: {target}
Domain: {domain}

Search paste sites, code repositories, and breach databases for any exposed credentials,
API keys, tokens, or sensitive data belonging to this organization."""

    llm = get_llm().bind_tools(TOOLS)
    messages = [SystemMessage(content=CREDENTIAL_LEAK_PROMPT), HumanMessage(content=context)]

    for _ in range(4):
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
                result = "Unknown tool"
            messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

    final_content = ""
    if messages and hasattr(messages[-1], "content") and messages[-1].content:
        final_content = messages[-1].content

    if isinstance(messages[-1], ToolMessage) or "[" not in final_content:
        gathered = collect_tool_results(messages)
        summary_messages = [
            SystemMessage(content="You are a credential leak analyst. Given the raw research data below, compile a JSON array of credential leaks found. Each object needs: source_url, leak_type, affected_accounts, severity, recommended_action. Wrap in ```json``` fences."),
            HumanMessage(content=f"Target: {target} ({domain})\n\nRaw research data:\n{gathered[:12000]}"),
        ]
        response = await get_llm().ainvoke(summary_messages)
        final_content = response.content

    logger.info(f"Credential leak raw output length: {len(final_content)}")

    leaks = parse_json_array(final_content)
    for leak in leaks:
        leak["id"] = str(uuid.uuid4())
        leak["discovered_at"] = datetime.now(timezone.utc).isoformat()

    threats_from_leaks = []
    for leak in leaks:
        threats_from_leaks.append({
            "id": leak.get("id", str(uuid.uuid4())),
            "threat_type": "credential_leak",
            "title": f"Credential leak: {leak.get('leak_type', 'unknown')}",
            "description": f"Found at {leak.get('source_url', 'unknown')}. {leak.get('recommended_action', '')}",
            "severity": leak.get("severity", "medium"),
            "source_url": leak.get("source_url", ""),
            "affected_versions": [],
            "discovered_at": datetime.now(timezone.utc).isoformat(),
        })

    logger.info(f"Credential leak parsed {len(leaks)} leaks for {target}")

    return {
        "credential_leaks": leaks,
        "discovered_threats": threats_from_leaks,
        "agent_trace": [{
            "agent": "credential_leak",
            "action": "scan_complete",
            "detail": f"Found {len(leaks)} credential leaks for {target}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }
