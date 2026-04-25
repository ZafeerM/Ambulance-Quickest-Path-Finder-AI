"""
Ambulance Quickest Path Finder — FastAPI Server
================================================
Monolithic architecture.

Endpoints
---------
GET  /health           — liveness probe
GET  /                 — API info
WS   /ws/applyAI       — main WebSocket endpoint (send payload, receive steps)

WebSocket flow
--------------
1. Client connects to /ws/applyAI
2. Client sends ONE JSON message matching GridPayload schema
3. Server streams back WSMessage objects until type == "done" or "error"
4. Connection may be kept open for subsequent runs (client sends a new payload)
"""

from __future__ import annotations

import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from config import settings
from schemas import GridPayload, WSMessage
from services.astar import astar_steps

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
log = logging.getLogger("server")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Ambulance Quickest Path Finder",
    description="REST + WebSocket API for AI pathfinding on a 2-D grid.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── REST helpers ──────────────────────────────────────────────────────────────

@app.get("/", tags=["meta"])
async def root():
    return {
        "name": "Ambulance Quickest Path Finder API",
        "version": "1.0.0",
        "websocket_endpoint": "/ws/applyAI",
    }


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}


# ── WebSocket helpers ─────────────────────────────────────────────────────────

async def _send(ws: WebSocket, msg_type: str, grid: list, message: str) -> None:
    """Serialise and send a WSMessage over *ws*."""
    payload = WSMessage(type=msg_type, grid=grid, message=message)
    await ws.send_text(payload.model_dump_json())


# ── Main WebSocket endpoint ───────────────────────────────────────────────────

@app.websocket("/ws/applyAI")
async def apply_ai(websocket: WebSocket):
    """
    Accept a GridPayload JSON message from the client, run the requested
    algorithm, and stream step-by-step updates back.

    The connection stays alive so the client can submit multiple runs
    (e.g. change the algorithm and rerun on the same grid).
    """
    await websocket.accept()
    log.info("WebSocket connection accepted from %s", websocket.client)

    try:
        while True:
            # ── Receive payload ───────────────────────────────────────────────
            raw = await websocket.receive_text()

            try:
                payload = GridPayload.model_validate_json(raw)
            except (ValidationError, ValueError) as exc:
                await _send(
                    websocket,
                    "error",
                    [],
                    f"Invalid payload: {exc}",
                )
                continue   # keep connection open, wait for a valid payload

            algorithm = payload.algorithm.lower().strip()
            log.info(
                "Run requested — algorithm=%s  grid=%dx%d",
                algorithm,
                payload.rows,
                payload.cols,
            )

            # ── Dispatch to the correct algorithm ─────────────────────────────
            if algorithm == "astar":
                heuristic = str(payload.params.get("heuristic", "manhattan")).lower()
                generator = astar_steps(payload.grid, heuristic)                        # Call the Astar Service

            else:
                await _send(
                    websocket,
                    "error",
                    payload.grid,
                    f"Algorithm '{algorithm}' is not yet implemented. "
                    "Currently supported: 'astar'.",
                )
                continue

            # ── Stream steps ──────────────────────────────────────────────────
            for grid_state, msg_type, message in generator:
                await _send(websocket, msg_type, grid_state, message)

                if msg_type == "step":
                    # Yield control to the event loop so the message is flushed
                    # before the next iteration, and respect the configured delay.
                    await asyncio.sleep(settings.step_delay_seconds)
                elif msg_type in ("done", "error"):
                    # Final message sent — stop iterating this run.
                    break

            log.info("Run complete — algorithm=%s", algorithm)

    except WebSocketDisconnect:
        log.info("WebSocket disconnected by client")

    except Exception as exc:
        log.exception("Unexpected error in WebSocket handler: %s", exc)
        try:
            await _send(
                websocket,
                "error",
                [],
                f"Internal server error: {exc}",
            )
        except Exception:
            pass   # socket may already be closed
