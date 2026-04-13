from typing import Optional
import asyncio
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from core.connection_manager import manager
from deps.auth_ws import get_current_user_ws

logger = logging.getLogger(__name__)

# Note: Prefix is handled in main.py as /api/ws_ev
router = APIRouter(tags=["Institutional WebSockets"])

@router.websocket("")
@router.websocket("/")
async def websocket_ev_endpoint(
    websocket: WebSocket,
    current_user = Depends(get_current_user_ws)
):
    """
    Main WebSocket endpoint for EV signals and alerts.
    Path: /api/ws_ev
    """
    # Use user_id for connection tracking, fallback to "anonymous" if no user
    user_id = "anonymous"
    if current_user:
        if hasattr(current_user, 'id'):
            user_id = current_user.id
        elif isinstance(current_user, dict) and 'id' in current_user:
            user_id = current_user['id']
        elif isinstance(current_user, dict) and 'sub' in current_user:
            user_id = current_user['sub']

    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Listen for client messages (heartbeats, subscriptions, etc.)
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "ping":
                    await manager.send_personal({"type": "pong"}, user_id)
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"[WS] WebSocket error for {user_id}: {str(e)}")
        manager.disconnect(user_id)

async def notify_ev_update(sport: str):
    """
    Broadcast to all connected users that new EV signals are available.
    """
    await manager.broadcast({
        "type": "ev_update",
        "sport": sport,
        "timestamp": asyncio.get_event_loop().time()
    })
