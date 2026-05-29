from langgraph.graph import END, StateGraph

from graph.state import SentinelState
from agents.orchestrator import orchestrator_node
from agents.discovery import discovery_node
from agents.credential_leak import credential_leak_node
from agents.vendor_risk import vendor_risk_node
from agents.correlation import correlation_node
from agents.risk_assessment import risk_assessment_node
from agents.remediation import remediation_node
from agents.notify import notify_node


def should_remediate(state: SentinelState) -> str:
    high_severity = any(
        score.get("score", 0) >= 70 for score in state.get("risk_scores", [])
    )
    if high_severity:
        return "remediation"
    return "log_and_store"


def build_sentinel_graph() -> StateGraph:
    graph = StateGraph(SentinelState)

    # Add nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("discovery", discovery_node)
    graph.add_node("credential_leak", credential_leak_node)
    graph.add_node("vendor_risk", vendor_risk_node)
    graph.add_node("correlation", correlation_node)
    graph.add_node("risk_assessment", risk_assessment_node)
    graph.add_node("remediation", remediation_node)
    graph.add_node("notify", notify_node)

    # Entry point
    graph.set_entry_point("orchestrator")

    # Orchestrator fans out to 3 parallel agents
    graph.add_edge("orchestrator", "discovery")
    graph.add_edge("orchestrator", "credential_leak")
    graph.add_edge("orchestrator", "vendor_risk")

    # All three merge into correlation
    graph.add_edge("discovery", "correlation")
    graph.add_edge("credential_leak", "correlation")
    graph.add_edge("vendor_risk", "correlation")

    # Correlation -> Risk Assessment
    graph.add_edge("correlation", "risk_assessment")

    # Conditional: high severity -> remediation, else end
    graph.add_conditional_edges(
        "risk_assessment",
        should_remediate,
        {
            "remediation": "remediation",
            "log_and_store": END,
        },
    )

    # Remediation -> Notify -> End
    graph.add_edge("remediation", "notify")
    graph.add_edge("notify", END)

    return graph.compile()
