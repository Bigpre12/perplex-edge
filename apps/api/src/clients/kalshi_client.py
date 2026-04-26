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
            base_url=settings.KALSHI_BASE_URL,
            timeout=20,
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
            # Handle both file paths and raw keys
            b64_key = (os.getenv("KALSHI_PRIVATE_KEY_B64") or "").strip()
            if b64_key:
                key_data = base64.b64decode(b64_key)
            elif "-----BEGIN" in self.private_key_str:
                key_data = self.private_key_str.encode()
            else:
                with open(self.private_key_str, 'rb') as f:
                    key_data = f.read()
            
            self._private_key = serialization.load_pem_private_key(
                key_data,
                password=None
            )
            return self._private_key
        except Exception as e:
            logger.error(f"[Kalshi] Failed to load private key: {str(e)}")
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
                    salt_length=padding.PSS.MAX_LENGTH
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
        full_path = f"/trade-api/v2{path}"
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
        
        return await self.request(method, full_path, **kwargs)

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
