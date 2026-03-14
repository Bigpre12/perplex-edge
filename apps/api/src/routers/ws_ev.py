# apps/api/src/routers/ws_ev.py
import logging
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.cache import cache

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Websocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/ev")
async def ws_ev(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # If Redis is available, we could sub to a channel here
        # For now, we provide the endpoint and a way to broadcast
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # If we wanted to echo or handle client messages
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WS Error: {e}")
        manager.disconnect(websocket)

async def notify_ev_update(sport: str):
    """Call this from workers to trigger a frontend refresh signal."""
    await manager.broadcast({
        "type": "ev_update",
        "sport": sport
    })
