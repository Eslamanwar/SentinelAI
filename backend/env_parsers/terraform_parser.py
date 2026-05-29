import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_terraform_state(path: str) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        logger.warning(f"Terraform state not found at {path}, using empty state")
        return {"resources": [], "source": "none"}

    with open(filepath) as f:
        data = json.load(f)

    resources = []
    for res in data.get("resources", []):
        res_type = res.get("type", "")
        res_name = res.get("name", "")
        provider = res.get("provider", "")

        for instance in res.get("instances", []):
            attrs = instance.get("attributes", {})
            resources.append({
                "type": res_type,
                "name": res_name,
                "provider": provider,
                "arn": attrs.get("arn", ""),
                "id": attrs.get("id", ""),
                "tags": attrs.get("tags", {}),
                "region": _extract_region(attrs),
                "version": attrs.get("engine_version", attrs.get("version", "")),
                "is_public": attrs.get("publicly_accessible", False),
            })

    return {"resources": resources, "source": str(filepath)}


def _extract_region(attrs: dict) -> str:
    arn = attrs.get("arn", "")
    if arn and arn.count(":") >= 3:
        parts = arn.split(":")
        return parts[3] if len(parts) > 3 else ""
    return attrs.get("region", "")


def get_resource_types(state: dict) -> list[str]:
    return sorted(set(r["type"] for r in state.get("resources", [])))


def format_state_for_llm(state: dict) -> str:
    lines = ["## Terraform / AWS Resource Inventory\n"]
    by_type: dict[str, list] = {}
    for res in state.get("resources", []):
        by_type.setdefault(res["type"], []).append(res)

    for rtype, resources in sorted(by_type.items()):
        lines.append(f"### {rtype} ({len(resources)} resources)")
        for r in resources[:10]:
            public_marker = " [PUBLIC]" if r.get("is_public") else ""
            version_info = f" v{r['version']}" if r.get("version") else ""
            lines.append(f"- {r['name']}{version_info}{public_marker}")
        if len(resources) > 10:
            lines.append(f"  ... and {len(resources) - 10} more")
        lines.append("")
    return "\n".join(lines)
