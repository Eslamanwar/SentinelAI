import asyncio
import json
import logging
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import settings
from events.bus import EventBus
from graph.builder import build_sentinel_graph
from graph.state import SentinelState
from models.schemas import InvestigationRequest, ThreatReport

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("sentinel")

event_bus = EventBus()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await event_bus.start()
    yield
    await event_bus.stop()


app = FastAPI(
    title="SentinelAI",
    description="Autonomous Infrastructure Threat Intelligence Agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/api/investigate")
async def start_investigation(request: InvestigationRequest):
    investigation_id = str(uuid.uuid4())
    graph = build_sentinel_graph()

    initial_state: SentinelState = {
        "investigation_id": investigation_id,
        "target": request.target,
        "target_domain": request.domain or "",
        "industry": request.industry or "technology",
        "discovered_threats": [],
        "correlated_threats": [],
        "risk_scores": [],
        "remediation_plans": [],
        "credential_leaks": [],
        "vendor_risks": [],
        "notifications_sent": [],
        "environment_inventory": {},
        "agent_trace": [],
        "status": "started",
        "error": None,
    }

    async def event_stream():
        logger.info(f"[{investigation_id[:8]}] Investigation started for '{request.target}'")
        yield f"data: {json.dumps({'type': 'started', 'investigation_id': investigation_id})}\n\n"

        try:
            async for event in graph.astream_events(initial_state, version="v2"):
                kind = event.get("event")
                name = event.get("name", "")

                # skip internal LangGraph nodes
                if name.startswith("_") or name in ("", "__start__", "LangGraph"):
                    continue

                if kind == "on_chain_start":
                    logger.info(f"[{investigation_id[:8]}] AGENT START: {name}")
                    yield f"data: {json.dumps({'type': 'agent_start', 'agent': name})}\n\n"

                elif kind == "on_chain_end":
                    data = event.get("data", {})
                    output = data.get("output", {})
                    trace_entry = {
                        "type": "agent_complete",
                        "agent": name,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    if isinstance(output, dict):
                        threats = output.get("discovered_threats", [])
                        creds = output.get("credential_leaks", [])
                        vendors = output.get("vendor_risks", [])
                        risks = output.get("risk_scores", [])
                        plans = output.get("remediation_plans", [])
                        correlated = output.get("correlated_threats", [])
                        notifications = output.get("notifications_sent", [])

                        if threats:
                            trace_entry["threats_found"] = len(threats)
                        counts = []
                        if threats: counts.append(f"{len(threats)} threats")
                        if creds: counts.append(f"{len(creds)} cred leaks")
                        if vendors: counts.append(f"{len(vendors)} vendor risks")
                        if risks: counts.append(f"{len(risks)} risk scores")
                        if plans: counts.append(f"{len(plans)} remediation plans")

                        summary = ", ".join(counts) if counts else "done"
                        logger.info(f"[{investigation_id[:8]}] AGENT DONE: {name} -> {summary}")

                        # Send actual data to frontend
                        if threats:
                            yield f"data: {json.dumps({'type': 'threats', 'data': threats}, default=str)}\n\n"
                        if creds:
                            yield f"data: {json.dumps({'type': 'credential_leaks', 'data': creds}, default=str)}\n\n"
                        if vendors:
                            yield f"data: {json.dumps({'type': 'vendor_risks', 'data': vendors}, default=str)}\n\n"
                        if correlated:
                            yield f"data: {json.dumps({'type': 'correlated_threats', 'data': correlated}, default=str)}\n\n"
                        if risks:
                            yield f"data: {json.dumps({'type': 'risk_scores', 'data': risks}, default=str)}\n\n"
                        if plans:
                            yield f"data: {json.dumps({'type': 'remediation_plans', 'data': plans}, default=str)}\n\n"
                        if notifications:
                            yield f"data: {json.dumps({'type': 'notifications', 'data': notifications}, default=str)}\n\n"
                    else:
                        logger.info(f"[{investigation_id[:8]}] AGENT DONE: {name}")

                    yield f"data: {json.dumps(trace_entry)}\n\n"

                elif kind == "on_tool_start":
                    tool_name = event.get("data", {}).get("input", {}).get("name", name)
                    logger.info(f"[{investigation_id[:8]}] TOOL CALL: {tool_name}")

                elif kind == "on_tool_end":
                    logger.info(f"[{investigation_id[:8]}] TOOL DONE: {name}")

                elif kind == "on_chat_model_stream":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

            logger.info(f"[{investigation_id[:8]}] Investigation COMPLETE")
            yield f"data: {json.dumps({'type': 'complete', 'investigation_id': investigation_id})}\n\n"

        except Exception as e:
            logger.error(f"[{investigation_id[:8]}] Investigation ERROR: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/investigations/{investigation_id}")
async def get_investigation(investigation_id: str):
    # TODO: fetch from PostgreSQL checkpoint store
    raise HTTPException(status_code=404, detail="Investigation not found")


@app.get("/api/threats")
async def list_threats():
    # TODO: fetch from database
    return {"threats": []}


@app.get("/api/vendors")
async def list_vendors():
    # TODO: fetch from database
    return {"vendors": []}


@app.get("/api/environment")
async def get_environment():
    from env_parsers.k8s_inventory import load_k8s_inventory
    from env_parsers.terraform_parser import load_terraform_state
    from env_parsers.vendor_inventory import load_vendor_inventory

    return {
        "kubernetes": load_k8s_inventory(settings.kubeconfig_path),
        "terraform": load_terraform_state(settings.terraform_state_path),
        "vendors": load_vendor_inventory(settings.vendor_inventory_path),
    }
