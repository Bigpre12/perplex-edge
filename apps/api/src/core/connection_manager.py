from typing import Dict, Set, List, Optional
from fastapi import WebSocket
import json
import asyncio
import logging
import redis.asyncio as redis
from core.config import settings

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}  # user_id -> set of websockets
        self.redis_client = redis.from_url(settings.REDIS_URL or "redis://localhost:6379")
        self._broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"✅ User {user_id} connected to WebSocket. Total users: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"❌ User {user_id} connection closed. Remaining users: {len(self.active_connections)}")

    async def send_personal(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            payload = json.dumps(message)
            dead_ws = []
            for ws in list(self.active_connections[user_id]):
                try:
                    await ws.send_text(payload)
                except Exception as e:
                    logger.error(f"Error sending personal message to {user_id}: {e}")
                    dead_ws.append(ws)
            
            for ws in dead_ws:
                self.disconnect(ws, user_id)

    async def broadcast(self, message: dict):
        """Send message to ALL connected local users."""
        payload = json.dumps(message)
        dead_connections = []
        
        # Iterate over a copy of the items to avoid modification during iteration
        for user_id, ws_set in list(self.active_connections.items()):
            for ws in list(ws_set):
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead_connections.append((ws, user_id))
        
        for ws, user_id in dead_connections:
            self.disconnect(ws, user_id)

    async def start_redis_listener(self):
        """Listen to Redis pub/sub and broadcast to local connections."""
        task = self._broadcast_task
        if task and not task.done():
            return

        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe("updates:global", "updates:ev", "updates:signals")
        
        logger.info("[WS] Redis Broadcast Listener Started.")
        
        async def _listen():
            try:
                async for message in pubsub.listen():
                    if message['type'] == 'message':
                        try:
                            data = json.loads(message['data'].decode('utf-8'))
                            await self.broadcast(data)
                        except Exception as e:
                            logger.error(f"[WS] Error processing Redis message: {e}")
            except Exception as e:
                logger.error(f"[WS] Redis Listener error: {e}")
            finally:
                await pubsub.unsubscribe()

        self._broadcast_task = asyncio.create_task(_listen())

manager = ConnectionManager()
