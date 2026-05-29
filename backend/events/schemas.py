EVENT_SCHEMAS = {
    "threat.discovered": {
        "type": "object",
        "properties": {
            "investigation_id": {"type": "string"},
            "threat": {"type": "object"},
            "timestamp": {"type": "string"},
        },
    },
    "threat.correlated": {
        "type": "object",
        "properties": {
            "investigation_id": {"type": "string"},
            "correlation": {"type": "object"},
            "timestamp": {"type": "string"},
        },
    },
    "risk.scored": {
        "type": "object",
        "properties": {
            "investigation_id": {"type": "string"},
            "risk": {"type": "object"},
            "timestamp": {"type": "string"},
        },
    },
    "remediation.generated": {
        "type": "object",
        "properties": {
            "investigation_id": {"type": "string"},
            "plan": {"type": "object"},
            "timestamp": {"type": "string"},
        },
    },
    "alert.dispatched": {
        "type": "object",
        "properties": {
            "investigation_id": {"type": "string"},
            "alert": {"type": "object"},
            "timestamp": {"type": "string"},
        },
    },
}
