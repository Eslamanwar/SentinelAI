import logging
from datetime import datetime, timezone

from config import settings
from env_parsers.k8s_inventory import format_inventory_for_llm, load_k8s_inventory
from env_parsers.terraform_parser import format_state_for_llm, load_terraform_state
from env_parsers.vendor_inventory import format_vendors_for_llm, load_vendor_inventory
from graph.state import SentinelState

logger = logging.getLogger(__name__)


async def orchestrator_node(state: SentinelState) -> dict:
    """Load environment inventory and prepare investigation context."""
    target = state["target"]
    domain = state.get("target_domain", "")

    k8s = load_k8s_inventory(settings.kubeconfig_path)
    tf = load_terraform_state(settings.terraform_state_path)
    vendors = load_vendor_inventory(settings.vendor_inventory_path)

    environment_inventory = {
        "kubernetes": k8s,
        "terraform": tf,
        "vendors": vendors,
        "summary": {
            "k8s_clusters": len(k8s.get("clusters", [])),
            "tf_resources": len(tf.get("resources", [])),
            "vendor_count": len(vendors.get("vendors", [])),
        },
    }

    trace_entry = {
        "agent": "orchestrator",
        "action": "initialize",
        "detail": (
            f"Starting investigation for '{target}'. "
            f"Environment: {environment_inventory['summary']['k8s_clusters']} K8s clusters, "
            f"{environment_inventory['summary']['tf_resources']} Terraform resources, "
            f"{environment_inventory['summary']['vendor_count']} vendors. "
            f"Dispatching parallel agents: discovery, credential_leak, vendor_risk."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "environment_inventory": environment_inventory,
        "status": "investigating",
        "agent_trace": [trace_entry],
    }
