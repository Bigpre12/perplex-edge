import asyncio
import json
import logging
import os
import datetime
import base64
import websockets
from typing import Optional, List, Dict
import redis.asyncio as aioredis
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from core.config import settings
from core.kalshi_urls import resolve_kalshi_ws_url

logger = logging.getLogger(__name__)

class KalshiWSManager:
    def __init__(self):
        self.api_key_id = os.getenv("KALSHI_API_KEY_ID")
        self.private_key_path = os.getenv("KALSHI_PRIVATE_KEY_PATH")
        self.private_key_content = os.getenv("KALSHI_PRIVATE_KEY")
        self.ws_url = resolve_kalshi_ws_url(
            os.getenv("KALSHI_WS_URL"),
            os.getenv("KALSHI_BASE_URL"),
        )
        self.redis_url = settings.REDIS_URL
        self.redis = None
        self._stop_event = asyncio.Event()
        self._private_key = None
        
        # Priority 1: Direct content from environment variable
        if self.private_key_content:
            try:
                key_bytes = self.private_key_content.replace("\\n", "\n").encode('utf-8')
                self._private_key = serialization.load_pem_private_key(
                    key_bytes,
                    password=None,
                    backend=default_backend()
                )
            except Exception as e:
                logger.error(f"KalshiWS: Failed to load private key from env: {e}")
        
        # Priority 2: Load from file path if not already loaded
        if not self._private_key and self.private_key_path and os.path.exists(self.private_key_path):
            try:
                with open(self.private_key_path, "rb") as key_file:
                    self._private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )
            except Exception as e:
                logger.error(f"KalshiWS: Failed to load private key from file: {e}")

        self._disabled = not (self.api_key_id and self._private_key)
        self._disabled_logged = False
        self._auth_failure_count = 0
        self._auth_disabled = False

    def _create_signature(self, timestamp: str, method: str, path: str) -> str:
        if not self._private_key: return ""
        message = f"{timestamp}{method}{path}".encode('utf-8')
        signature = self._private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    async def get_auth_headers(self) -> Dict[str, str]:
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        # WS signature path is hardcoded in docs as /trade-api/ws/v2
        path = "/trade-api/ws/v2"
        signature = self._create_signature(timestamp, "GET", path)
        return {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp
        }

    async def connect_redis(self):
        if not self.redis and self.redis_url:
            self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
            logger.info("KalshiWS: Connected to Redis for Pub/Sub")
        elif not self.redis_url:
            logger.warning("KalshiWS: REDIS_URL not configured, skipping Redis")

    async def subscribe(self, websocket, tickers: List[str]):
        sub_msg = {
            "id": 2,
            "type": "subscribe",
            "channels": ["orderbook_delta", "trade"],
            "tickers": tickers
        }
        await websocket.send(json.dumps(sub_msg))
        logger.info(f"KalshiWS: Subscribed to {tickers}")

    async def run(self, tickers: List[str]):
        if self._disabled:
            if not self._disabled_logged:
                logger.warning(
                    "KalshiWS: Disabled — missing KALSHI_API_KEY_ID or private key "
                    "(KALSHI_PRIVATE_KEY / KALSHI_PRIVATE_KEY_PATH). WebSocket will not connect."
                )
                self._disabled_logged = True
            await self._stop_event.wait()
            return

        if self._auth_disabled:
            await self._stop_event.wait()
            return

        await self.connect_redis()
        retry_delay = 1
        
        while not self._stop_event.is_set():
            try:
                headers = await self.get_auth_headers()
                async with websockets.connect(self.ws_url, additional_headers=headers) as websocket:
                    await self.subscribe(websocket, tickers)
                    
                    retry_delay = 1 # Reset retry delay on successful connect
                    
                    async for message in websocket:
                        data = json.loads(message)
                        # Push to Redis pub/sub channel "kalshi:prices"
                        if self.redis:
                            await self.redis.publish("kalshi:prices", json.dumps(data))
                            
            except Exception as e:
                err_s = str(e).lower()
                if "401" in err_s or "403" in err_s or "unauthorized" in err_s:
                    self._auth_failure_count += 1
                    if self._auth_failure_count >= 2:
                        self._auth_disabled = True
                        logger.error(
                            "KalshiWS: Repeated HTTP 401/403 on WebSocket handshake. "
                            "Use the same environment as your API keys: demo REST "
                            "(https://demo-api.kalshi.co/trade-api/v2) + demo WS, or production "
                            "(https://api.elections.kalshi.com/trade-api/v2) + set KALSHI_WS_URL "
                            "or KALSHI_BASE_URL so the WS host matches. Disabling Kalshi WS."
                        )
                        await self._stop_event.wait()
                        return
                logger.error(f"KalshiWS: Connection error: {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30) # Exponential backoff

    def stop(self):
        self._stop_event.set()

kalshi_ws_manager = KalshiWSManager()
