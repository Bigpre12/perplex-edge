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
        self.api_key_id = os.getenv("KALSHI_API_KEY_ID") or os.getenv("KALSHI_API_KEY")
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
        self.enabled = False
        self.available = False
        self._disabled = True # Default until loaded
        self._disabled_logged = False
        self._auth_failure_count = 0
        self._auth_disabled = False

        self._load_key_safely()

    def _load_key_safely(self):
        """Standardized robust key loader with defensive error handling."""
        try:
            # 1. Try Base64-specific variable first
            b64_val = (os.getenv("KALSHI_PRIVATE_KEY_B64") or "").strip()
            if b64_val:
                try:
                    # Robust cleaning: remove all whitespace and potential non-b64 chars
                    import re
                    clean_b64 = re.sub(r'[^a-zA-Z0-9+/=]', '', b64_val)
                    key_bytes = base64.b64decode(clean_b64)
                    
                    # Validation: must look like a PEM after decoding
                    try:
                        decoded_text = key_bytes.decode("utf-8")
                        if "-----BEGIN" in decoded_text:
                            self._private_key = serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                            self.enabled = True
                            logger.info("KalshiWS: key loaded successfully from B64_ENV")
                            return
                    except (UnicodeDecodeError, ValueError):
                        # Not a PEM, maybe it's DER?
                        try:
                            self._private_key = serialization.load_der_private_key(key_bytes, password=None, backend=default_backend())
                            self.enabled = True
                            logger.info("KalshiWS: key loaded successfully from DER bytes via B64_ENV")
                            return
                        except Exception:
                            pass
                    logger.error("KalshiWS: Decoded B64 key does not contain PEM header or valid DER")
                except Exception as e:
                    logger.error(f"KalshiWS: Failed to load B64 key: {e}")

            # 2. Try Raw PEM or Base64 in KALSHI_PRIVATE_KEY
            raw_val = self.private_key_content
            if raw_val:
                # Remove common surrounding noise from env vars
                raw_val = raw_val.strip().strip('"').strip("'")
                
                # Case A: It's a raw PEM
                if "-----BEGIN" in raw_val:
                    try:
                        # Handle literal '\n' characters and ensure proper line breaks for PEM
                        normalized_pem = raw_val.replace("\\n", "\n").replace(" ", "\n").replace("\n\n", "\n")
                        # If we replaced spaces with newlines, we might have broken the header/footer
                        normalized_pem = normalized_pem.replace("BEGIN\nPRIVATE\nKEY", "BEGIN PRIVATE KEY")
                        normalized_pem = normalized_pem.replace("END\nPRIVATE\nKEY", "END PRIVATE KEY")
                        
                        key_bytes = normalized_pem.encode("utf-8")
                        self._private_key = serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                        self.enabled = True
                        logger.info("KalshiWS: key loaded successfully from raw PEM")
                        return
                    except Exception as e:
                        logger.error(f"KalshiWS: Failed to load raw PEM: {e}")
                
                # Case B: It's Base64 (likely single-line from Railway)
                else:
                    try:
                        # Robust cleaning: remove all whitespace and potential non-b64 chars
                        import re
                        clean_b64 = re.sub(r'[^a-zA-Z0-9+/=]', '', raw_val)
                        key_bytes = base64.b64decode(clean_b64)
                        
                        # Check if decoded bytes look like a PEM
                        try:
                            decoded_text = key_bytes.decode("utf-8")
                            if "-----BEGIN" in decoded_text:
                                self._private_key = serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                                self.enabled = True
                                logger.info("KalshiWS: key loaded successfully from B64 in KALSHI_PRIVATE_KEY")
                                return
                        except (UnicodeDecodeError, ValueError):
                            # Not a PEM, maybe it's the DER bytes directly?
                            try:
                                self._private_key = serialization.load_der_private_key(key_bytes, password=None, backend=default_backend())
                                self.enabled = True
                                logger.info("KalshiWS: key loaded successfully from DER bytes in KALSHI_PRIVATE_KEY")
                                return
                            except Exception:
                                pass
                        
                        logger.error("KalshiWS: Potential B64 in KALSHI_PRIVATE_KEY is not a valid PEM or DER after decoding")
                    except Exception as e:
                        logger.error(f"KalshiWS: Failed to load potential B64 in KALSHI_PRIVATE_KEY: {e}")

            # 3. Try File Path
            path_val = self.private_key_path
            if path_val and os.path.exists(path_val):
                try:
                    with open(path_val, "rb") as f:
                        self._private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
                        self.enabled = True
                        logger.info(f"KalshiWS: key loaded successfully from file {path_val}")
                        return
                except Exception as e:
                    logger.error(f"KalshiWS: Failed to load key from file {path_val}: {e}")
        except Exception as e:
            logger.critical(f"KalshiWS: Unexpected crash in _load_key_safely: {e}")

        # Diagnostic logging for Railway debugging
        logger.info(f"KalshiWS Config: KEY_ID={bool(self.api_key_id)} (len={len(self.api_key_id) if self.api_key_id else 0}), PRIV_KEY={self.enabled}")

        self.available = self.enabled
        self._disabled = not self.available
        if not self.enabled:
            logger.warning("KalshiWS: Initialization reached end without loading a key. Service will be disabled.")

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
        """Subscribe to ticker, orderbook, and trade updates"""
        # 1. Subscribe to 'ticker' (all markets)
        ticker_msg = {
            "id": 1,
            "cmd": "subscribe",
            "params": {
                "channels": ["ticker"]
            }
        }
        await websocket.send(json.dumps(ticker_msg))
        
        # 2. Subscribe to 'orderbook_delta' and 'trade' for specific markets if provided
        if tickers:
            market_msg = {
                "id": 2,
                "cmd": "subscribe",
                "params": {
                    "channels": ["orderbook_delta", "trade"],
                    "market_tickers": tickers
                }
            }
            await websocket.send(json.dumps(market_msg))
            logger.info(f"KalshiWS: Subscribed to ticker (all) and {tickers} for orderbook/trades")
        else:
            logger.info("KalshiWS: Subscribed to ticker (all)")

    async def run(self, tickers: List[str]):
        if not os.getenv("KALSHI_PRIVATE_KEY") or not os.getenv("KALSHI_API_KEY_ID"):
            logger.warning("Kalshi credentials not configured — WebSocket disabled. Set KALSHI_PRIVATE_KEY and KALSHI_API_KEY_ID in Railway env vars to enable.")
            return

        if self._disabled:
            if not self._disabled_logged:
                logger.warning(
                    "KalshiWS: Disabled — missing KALSHI_API_KEY_ID (or KALSHI_API_KEY) or private key "
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
