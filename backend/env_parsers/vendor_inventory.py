import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_vendor_inventory(path: str) -> dict[str, Any]:
    filepath = Path(path)
    if not filepath.exists():
        logger.warning(f"Vendor inventory not found at {path}, using empty list")
        return {"vendors": [], "source": "none"}

    with open(filepath) as f:
        data = json.load(f)

    return {"vendors": data.get("vendors", []), "source": str(filepath)}


def get_vendor_names(inventory: dict) -> list[str]:
    return [v.get("name", "") for v in inventory.get("vendors", [])]


def format_vendors_for_llm(inventory: dict) -> str:
    lines = ["## Third-Party Vendor Inventory\n"]
    for vendor in inventory.get("vendors", []):
        lines.append(f"### {vendor.get('name', 'Unknown')}")
        lines.append(f"- Category: {vendor.get('category', 'N/A')}")
        lines.append(f"- Criticality: {vendor.get('criticality', 'N/A')}")
        lines.append(f"- URL: {vendor.get('url', 'N/A')}")
        if vendor.get("data_shared"):
            lines.append(f"- Data shared: {', '.join(vendor['data_shared'])}")
        lines.append("")
    return "\n".join(lines)
