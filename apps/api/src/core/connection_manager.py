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
        self.active_connections: Dict[str, WebSocket] = {}  # user_id -> websocket
        self.redis_client = redis.from_url(settings.REDIS_URL or "redis://localhost:6379")
        self._broadcast_task: Optional[asyncio.Task] = None

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"✅ User {user_id} connected to WebSocket. Total: {len(self.active_connections)}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"❌ User {user_id} disconnected. Total: {len(self.active_connections)}")

    async def send_personal(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending personal message to {user_id}: {e}")
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        """Send message to ALL connected local users."""
        payload = json.dumps(message)
        disconnected = []
        for user_id, ws in self.active_connections.items():
            try:
                await ws.send_text(payload)
            except Exception:
                disconnected.append(user_id)
        
        for user_id in disconnected:
            self.disconnect(user_id)

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
