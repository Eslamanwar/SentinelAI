from typing import Annotated, Any, Optional, TypedDict

from langgraph.graph.message import add_messages

from models.schemas import (
    AgentTraceEntry,
    CorrelatedThreat,
    CredentialLeak,
    DiscoveredThreat,
    RemediationPlan,
    RiskScore,
    VendorRisk,
)


def merge_lists(left: list, right: list) -> list:
    return left + right


class SentinelState(TypedDict):
    investigation_id: str
    target: str
    target_domain: str
    industry: str

    # Web intelligence outputs
    discovered_threats: Annotated[list[dict], merge_lists]
    correlated_threats: Annotated[list[dict], merge_lists]
    risk_scores: Annotated[list[dict], merge_lists]
    remediation_plans: Annotated[list[dict], merge_lists]
    credential_leaks: Annotated[list[dict], merge_lists]
    vendor_risks: Annotated[list[dict], merge_lists]

    # Notifications
    notifications_sent: Annotated[list[dict], merge_lists]

    # Environment context
    environment_inventory: dict

    # Agent trace for UI streaming
    agent_trace: Annotated[list[dict], merge_lists]

    # Control flow
    status: str
    error: Optional[str]
