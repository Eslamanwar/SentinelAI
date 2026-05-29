import logging
from datetime import datetime, timezone

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from agents._utils import collect_tool_results, parse_json_array
from graph.llm import get_llm
from graph.state import SentinelState
from tools.brightdata_serp import search_web
from tools.brightdata_unlocker import fetch_page

logger = logging.getLogger("sentinel")

VENDOR_RISK_PROMPT = """You are a third-party vendor risk analyst. Your job is to assess
the security posture of an organization's vendors and SaaS providers.

You have access to:
- search_web: Search the web via Bright Data SERP API
- fetch_page: Fetch full page content via Bright Data Web Unlocker

For each vendor:
1. Search for recent breaches, security incidents, or data leaks
2. Check their status page for ongoing incidents
3. Look for compliance issues, lawsuits, or regulatory actions

IMPORTANT: After gathering information, you MUST return your final answer as a JSON array.
Each object needs: vendor_name, risk_score (0-100), incidents (list), compliance_issues (list), recommendation.
Wrap the JSON in ```json``` fences."""

TOOLS = [search_web, fetch_page]


async def vendor_risk_node(state: SentinelState) -> dict:
    target = state["target"]
    env = state.get("environment_inventory", {})
    vendors = env.get("vendors", {}).get("vendors", [])

    vendor_names = [v.get("name", "") for v in vendors] if vendors else []
    vendor_list = ", ".join(vendor_names) if vendor_names else "No vendor inventory available"

    context = f"""Assess vendor risk for: {target}

Known vendors: {vendor_list}

Search for recent security incidents, breaches, compliance issues, and status page
problems for each vendor."""

    llm = get_llm().bind_tools(TOOLS)
    messages = [SystemMessage(content=VENDOR_RISK_PROMPT), HumanMessage(content=context)]

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
            SystemMessage(content="You are a vendor risk analyst. Given the raw research data below, compile a JSON array of vendor risk assessments. Each object needs: vendor_name, risk_score (0-100), incidents (list of objects with title/date/severity), compliance_issues (list of strings), recommendation. Wrap in ```json``` fences."),
            HumanMessage(content=f"Target: {target}\nVendors: {vendor_list}\n\nRaw research data:\n{gathered[:12000]}"),
        ]
        response = await get_llm().ainvoke(summary_messages)
        final_content = response.content

    logger.info(f"Vendor risk raw output length: {len(final_content)}")

    risks = parse_json_array(final_content)

    vendor_threats = []
    for vr in risks:
        if vr.get("risk_score", 0) >= 60:
            vendor_threats.append({
                "id": f"vendor-{vr.get('vendor_name', 'unknown')}",
                "threat_type": "vendor_breach",
                "title": f"High vendor risk: {vr.get('vendor_name', 'Unknown')}",
                "description": f"Risk score {vr.get('risk_score')}/100. {vr.get('recommendation', '')}",
                "severity": "high" if vr.get("risk_score", 0) >= 80 else "medium",
                "source_url": "",
                "affected_versions": [],
                "discovered_at": datetime.now(timezone.utc).isoformat(),
            })

    logger.info(f"Vendor risk parsed {len(risks)} vendors, {len(vendor_threats)} high-risk")

    return {
        "vendor_risks": risks,
        "discovered_threats": vendor_threats,
        "agent_trace": [{
            "agent": "vendor_risk",
            "action": "assessment_complete",
            "detail": f"Assessed {len(risks)} vendors, {len(vendor_threats)} high-risk",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }],
    }
