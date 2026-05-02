import logging
import time
import base64
import os
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from .base_client import ResilientBaseClient
from core.config import settings

logger = logging.getLogger(__name__)

class KalshiClient(ResilientBaseClient):
    """
    Kalshi Elite Client (v2 RSA-signed).
    Handles prediction markets with institutional-grade security.
    """
    
    def __init__(self):
        super().__init__(
            name="Kalshi",
            base_url=settings.KALSHI_BASE_URL if settings.KALSHI_BASE_URL.endswith("/") else settings.KALSHI_BASE_URL + "/",
            timeout=30,
            max_retries=3
        )
        self.key_id = settings.KALSHI_KEY_ID
        self.private_key_str = settings.KALSHI_PRIVATE_KEY
        self._private_key = None
        self.enabled = bool(self.key_id and self.private_key_str)

    def _get_private_key(self):
        if self._private_key:
            return self._private_key
        
        try:
            # Standardized robust key loader
            b64_val = os.getenv("KALSHI_PRIVATE_KEY_B64")
            raw_val = self.private_key_str
            path_val = self.private_key_str # In KalshiClient, private_key_str might be a path

            # 1. Try Base64-specific variable first
            if b64_val:
                try:
                    clean_b64 = b64_val.strip().strip('"').strip("'").replace("\n", "").replace("\r", "")
                    key_bytes = base64.b64decode(clean_b64)
                    self._private_key = serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                    return self._private_key
                except Exception as e:
                    logger.error(f"[Kalshi] Failed to load B64 key: {e}")

            # 2. Try Raw PEM or Base64 in KALSHI_PRIVATE_KEY
            if raw_val:
                raw_val = raw_val.strip().strip('"').strip("'")
                # Case A: It's a raw PEM
                if "-----BEGIN" in raw_val:
                    try:
                        key_bytes = raw_val.replace("\\n", "\n").encode("utf-8")
                        self._private_key = serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                        return self._private_key
                    except Exception as e:
                        logger.error(f"[Kalshi] Failed to load raw PEM: {e}")
                # Case B: It's Base64 (likely single-line from Railway)
                else:
                    try:
                        clean_b64 = raw_val.replace("\n", "").replace("\r", "")
                        key_bytes = base64.b64decode(clean_b64)
                        self._private_key = serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                        return self._private_key
                    except Exception as e:
                        logger.error(f"[Kalshi] Failed to load potential B64 in KALSHI_PRIVATE_KEY: {e}")

            # 3. Try File Path
            if path_val and os.path.exists(path_val):
                try:
                    with open(path_val, "rb") as f:
                        self._private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
                        return self._private_key
                except Exception as e:
                    logger.error(f"[Kalshi] Failed to load key from file {path_val}: {e}")
            
            return None
        except Exception as e:
            logger.error(f"[Kalshi] Unexpected error loading private key: {str(e)}")
            return None

    def _sign_message(self, timestamp: str, method: str, path: str) -> str:
        """Sign the request as per Kalshi v2 spec: timestamp + method + path"""
        try:
            message = f"{timestamp}{method}{path}"
            private_key = self._get_private_key()
            if not private_key:
                return ""

            signature = private_key.sign(
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode()
        except Exception as e:
            logger.error(f"[Kalshi] RSA Signing failed: {str(e)}")
            return ""

    async def kalshi_request(self, method: str, path: str, **kwargs) -> Any:
        """RSA-PSS signed request for Kalshi v2 Trade API"""
        if not self.enabled:
            logger.debug("Kalshi client disabled: missing key id/private key")
            return {}
        # Ensure path is relative for proper base_url joining
        rel_path = path.lstrip('/')
        full_path = f"/trade-api/v2/{rel_path}".replace('//', '/')
        timestamp = str(int(time.time() * 1000))
        signature = self._sign_message(timestamp, method, full_path)
        
        headers = kwargs.get("headers", {})
        headers.update({
            "KALSHI-ACCESS-KEY": self.key_id,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
            "Content-Type": "application/json"
        })
        kwargs["headers"] = headers
        
        return await self.request(method, rel_path, **kwargs)

    async def get_exchange_status(self) -> Dict[str, Any]:
        return await self.kalshi_request("GET", "/exchange/status")

    async def get_markets(self, limit: int = 50, cursor: Optional[str] = None) -> Dict[str, Any]:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return await self.kalshi_request("GET", "/markets", params=params)

    async def get_market(self, ticker: str) -> Dict[str, Any]:
        return await self.kalshi_request("GET", f"/markets/{ticker}")

    async def get_orderbook(self, ticker: str) -> Dict[str, Any]:
        return await self.kalshi_request("GET", f"/markets/{ticker}/orderbook")

kalshi_client = KalshiClient()
