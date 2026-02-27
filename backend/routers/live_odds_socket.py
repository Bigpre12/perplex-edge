import asyncio
import json
import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from services.webhook_manager import dispatch_webhooks

router = APIRouter(tags=["Real-Time WebSockets"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🟢 Client connected to Live Engine WS. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"🔴 Client disconnected from Live Engine WS. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        # Convert dict to JSON string once
        payload = json.dumps(message)
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception as e:
                print(f"WS Broadcast error: {e}")
                self.disconnect(connection)

manager = ConnectionManager()

# Background task that polls the local EV engine and broadcasts the diff/state
# In a pure event-driven architecture, the core scraper would emit events to a Redis PubSub channel.
# For simplicity here, we simulate the "Push" by having the WS server poll internal memory every 10 seconds and broadcast.
async def live_odds_broadcaster():
    print("🚀 Starting WebSockets Live Odds Broadcaster Loop...")
    import os
    port = os.environ.get("PORT", "8000")
    internal_url = f"http://localhost:{port}/immediate/working-player-props?limit=15"
    async with httpx.AsyncClient() as client:
        while True:
            try:
                # Only poll if we have connected clients to save CPU
                if len(manager.active_connections) > 0:
                    res = await client.get(internal_url, timeout=5.0)
                    if res.status_code == 200:
                        data = res.json()
                        await manager.broadcast({"type": "LIVE_EV_UPDATE", "data": data})

                        # Phase 11: Trigger Institutional Webhook Pipes for Whales & High-EV Signals
                        if data.get("items"):
                            asyncio.create_task(dispatch_webhooks(data["items"]))
            except Exception as e:
                print(f"WS Engine Polling Error: {e}")
            
            # Broadcast every 8 seconds
            await asyncio.sleep(8)

@router.websocket("/api/ws/live-odds")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect the client to send much data, but we must keep the loop open
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS Unexpected Error: {e}")
        manager.disconnect(websocket)
