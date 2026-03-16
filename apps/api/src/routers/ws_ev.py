import asyncio
import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from core.config import settings
import redis.asyncio as redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["Institutional WebSockets"])
redis_client = redis.from_url(settings.REDIS_URL)

class WebSocketConnectionManager:
    """
    Sub-second Signal Distribution Manager.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.redis_client = redis_client

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"[WS] New connection. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"[WS] Connection closed. Active: {len(self.active_connections)}")

    async def broadcast_from_redis(self):
        """
        Listen to Redis pub/sub and broadcast to all connected institutional clients.
        """
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe("updates:global", "updates:ev", "updates:signals")
        
        logger.info("[WS] Neural Broadcast Loop Started.")
        
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = message['data'].decode('utf-8')
                    await self._broadcast(data)
        except Exception as e:
            logger.error(f"[WS] Broadcast error: {str(e)}")
        finally:
            await pubsub.unsubscribe()

    async def _broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # Connection might be stale
                pass

manager = WebSocketConnectionManager()

@router.websocket("/ev")
async def websocket_ev_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle client-side heartbeat or subscriptions if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"[WS] WebSocket error: {str(e)}")
        manager.disconnect(websocket)

# Background Task Starter (to be called in main.py)
async def start_websocket_broadcast():
    asyncio.create_task(manager.broadcast_from_redis())
