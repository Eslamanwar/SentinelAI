import json
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


def load_k8s_inventory(path: str) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        logger.warning(f"Kubeconfig not found at {path}, using empty inventory")
        return {"clusters": [], "source": "none"}

    with open(filepath) as f:
        data = yaml.safe_load(f)

    clusters = []
    for cluster_entry in data.get("clusters", []):
        cluster = cluster_entry.get("cluster", {})
        name = cluster_entry.get("name", "unknown")

        namespaces = cluster.get("namespaces", [])
        workloads = cluster.get("workloads", [])
        version = cluster.get("version", "unknown")

        clusters.append({
            "name": name,
            "version": version,
            "server": cluster.get("server", ""),
            "namespaces": namespaces,
            "workloads": workloads,
            "node_count": cluster.get("node_count", 0),
            "is_internet_facing": cluster.get("is_internet_facing", False),
            "network_policies_enabled": cluster.get("network_policies_enabled", False),
            "images": cluster.get("images", []),
        })

    return {"clusters": clusters, "source": str(filepath)}


def get_cluster_versions(inventory: dict) -> list[dict]:
    return [
        {"name": c["name"], "version": c["version"]}
        for c in inventory.get("clusters", [])
    ]


def get_running_images(inventory: dict) -> list[str]:
    images = set()
    for cluster in inventory.get("clusters", []):
        for img in cluster.get("images", []):
            images.add(img)
    return sorted(images)


def format_inventory_for_llm(inventory: dict) -> str:
    lines = ["## Kubernetes Environment Inventory\n"]
    for cluster in inventory.get("clusters", []):
        lines.append(f"### Cluster: {cluster['name']}")
        lines.append(f"- Version: {cluster['version']}")
        lines.append(f"- Nodes: {cluster.get('node_count', 'unknown')}")
        lines.append(f"- Internet-facing: {cluster.get('is_internet_facing', False)}")
        lines.append(f"- Network policies: {cluster.get('network_policies_enabled', False)}")
        if cluster.get("namespaces"):
            lines.append(f"- Namespaces: {', '.join(cluster['namespaces'])}")
        if cluster.get("images"):
            lines.append(f"- Images: {', '.join(cluster['images'][:20])}")
        lines.append("")
    return "\n".join(lines)
