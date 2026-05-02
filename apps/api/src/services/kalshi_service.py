import os
import httpx
from services.api_telemetry import InstrumentedAsyncClient
import datetime
import base64
import logging
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse
from services.cache import cache
from api_utils.http import build_headers
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from core.kalshi_urls import default_kalshi_rest_url
from core.kalshi_urls import sanitize_kalshi_base_url

logger = logging.getLogger(__name__)

# Railway / production: set KALSHI_API_KEY_ID plus KALSHI_PRIVATE_KEY (PEM, use \n for newlines)
# or KALSHI_PRIVATE_KEY_PATH. Optional: KALSHI_BASE_URL. iSports TLS: ISPORTS_VERIFY_TLS=false if
# the provider cert chain mismatches in your region.

class KalshiService:
    def __init__(self):
        self.api_key_id = os.getenv("KALSHI_API_KEY_ID") or os.getenv("KALSHI_API_KEY")
        self.private_key_path = os.getenv("KALSHI_PRIVATE_KEY_PATH")
        self.private_key_content = os.getenv("KALSHI_PRIVATE_KEY")
        self.private_key_b64 = (os.getenv("KALSHI_PRIVATE_KEY_B64") or "").strip()
        self.base_url = sanitize_kalshi_base_url(os.getenv("KALSHI_BASE_URL", default_kalshi_rest_url()))
        if not self.base_url.endswith("/"):
            self.base_url += "/"
        self.client = InstrumentedAsyncClient(
            provider="kalshi", 
            base_url=self.base_url, 
            purpose="kalshi_sync",
            timeout=30.0
        )
        self._private_key = None
        self._missing_credentials_warned = False

        # Standardized robust key loader
        def load_key(b64_val, raw_val, path_val):
            # 1. Try Base64-specific variable first
            if b64_val:
                try:
                    clean_b64 = b64_val.strip().strip('"').strip("'").replace("\n", "").replace("\r", "")
                    key_bytes = base64.b64decode(clean_b64)
                    return serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                except Exception as e:
                    logger.error(f"KalshiService: Failed to load B64 key: {e}")

            # 2. Try Raw PEM or Base64 in KALSHI_PRIVATE_KEY
            if raw_val:
                raw_val = raw_val.strip().strip('"').strip("'")
                # Case A: It's a raw PEM
                if "-----BEGIN" in raw_val:
                    try:
                        key_bytes = raw_val.replace("\\n", "\n").encode("utf-8")
                        return serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                    except Exception as e:
                        logger.error(f"KalshiService: Failed to load raw PEM: {e}")
                # Case B: It's Base64 (likely single-line from Railway)
                else:
                    try:
                        clean_b64 = raw_val.replace("\n", "").replace("\r", "")
                        key_bytes = base64.b64decode(clean_b64)
                        return serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
                    except Exception as e:
                        logger.error(f"KalshiService: Failed to load potential B64 in KALSHI_PRIVATE_KEY: {e}")

            # 3. Try File Path
            if path_val and os.path.exists(str(path_val)):
                try:
                    with open(str(path_val), "rb") as f:
                        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())
                except Exception as e:
                    logger.error(f"KalshiService: Failed to load key from file {path_val}: {e}")
            
            return None

        self._private_key = load_key(
            self.private_key_b64,
            self.private_key_content,
            self.private_key_path
        )

        # Diagnostic logging for Railway debugging
        logger.info(f"KalshiService Config: KEY_ID={bool(self.api_key_id)} (len={len(self.api_key_id) if self.api_key_id else 0}), PRIV_KEY={bool(self._private_key)}")
        if self.private_key_content:
            pk_raw = self.private_key_content.strip()
            logger.info(f"KalshiService Debug: Raw Key starts with '{pk_raw[:15]}...' and ends with '...{pk_raw[-15:]}' (len={len(pk_raw)})")

        self.available = bool(self.api_key_id and self._private_key)
        if not self.available:
            logger.warning(
                "Kalshi: no private key configured (KALSHI_PRIVATE_KEY or KALSHI_PRIVATE_KEY_PATH) "
                "and/or key id (KALSHI_API_KEY_ID or KALSHI_API_KEY)"
            )

    def _warn_missing_credentials_once(self, context: str) -> None:
        if self._missing_credentials_warned:
            logger.debug("KalshiService: %s skipped - credentials not configured", context)
            return
        logger.warning("KalshiService: %s skipped - credentials not configured", context)
        self._missing_credentials_warned = True

    def _create_signature(self, timestamp: str, method: str, path: str) -> str:
        """Create RSA-PSS signature for Kalshi v2 auth"""
        if not self._private_key:
            return ""
        path_without_query = path.split('?')[0]
        payload = f"{timestamp}{method}{path_without_query}" # Renamed 'message' to 'payload'
        logger.debug(f"Kalshi signing payload: {payload}")
        
        pk = self._private_key
        if pk is not None:
            signature = pk.sign(
                payload.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        return ""

    async def _get_auth_headers(self, method: str, path: str) -> Optional[Dict[str, str]]:
        """Generate mandatory Kalshi v2 authenticated headers"""
        if not self.api_key_id or not self._private_key:
            return None
            
        timestamp = str(int(datetime.datetime.now().timestamp() * 1000))
        
        # Kalshi requires the full path including /trade-api/v2 for signing
        # We need to ensure the path starts with the base_url path part if not absolute
        parsed_base = urlparse(self.base_url)
        # Ensure path is relative (no leading slash) for proper base_url joining
        relative_path = path.lstrip('/')
        full_path = parsed_base.path + relative_path
        # Normalize to avoid double slashes if base_url ends with / or path starts with /
        full_path = full_path.replace('//', '/')
        
        signature = self._create_signature(timestamp, method, full_path)
        
        return build_headers({
            "Content-Type": "application/json",
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestamp
        })

    async def get_kalshi_sports_markets(self, sport: str) -> List[Dict[str, Any]]:
        """Fetch open markets filtered by sport keyword"""
        path = "markets"
        headers = await self._get_auth_headers("GET", path)
        if not headers:
            self._warn_missing_credentials_once("fetch_markets")
            return []
            
        params = {"status": "open", "series_ticker": sport}
        try:
            response = await self.client.get(path, headers=headers, params=params)
            response.raise_for_status()
            return response.json().get("markets", [])
        except Exception as e:
            logger.error(f"Error fetching Kalshi sports markets: {e}")
            return []

    async def get_kalshi_market_orderbook(self, ticker: str) -> Dict[str, Any]:
        """Return full bid/ask orderbook"""
        path = f"markets/{ticker}/orderbook"
        headers = await self._get_auth_headers("GET", path)
        if not headers:
            return {}
            
        try:
            response = await self.client.get(path, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching Kalshi orderbook for {ticker}: {e}")
            return {}

    async def get_kalshi_events(self, series: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch open Kalshi events (sports + politics + economics)"""
        path = "events"
        headers = await self._get_auth_headers("GET", path)
        if not headers:
            return []
            
        params = {"status": "open"}
        if series:
            params["series_ticker"] = series
        try:
            response = await self.client.get(path, headers=headers, params=params)
            response.raise_for_status()
            return response.json().get("events", [])
        except Exception as e:
            logger.error(f"Error fetching Kalshi events: {e}")
            return []

    async def place_kalshi_order(self, ticker: str, side: str, count: int, price: int) -> Dict[str, Any]:
        """POST to /portfolio/orders with limit order payload"""
        path = "portfolio/orders"
        headers = await self._get_auth_headers("POST", path)
        if not headers:
            return {"error": "Missing credentials"}
            
        payload = {
            "ticker": ticker,
            "side": side,
            "count": count,
            "type": "limit",
            "price": price,
            "expiration_time": 0 # Default GTC
        }
        try:
            # Note: Kalshi v2 POST requests require signing the path BEFORE query params.
            # Our _get_auth_headers already handles path.split('?')[0].
            response = await self.client.post(path, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error placing Kalshi order on {ticker}: {e}")
            return {"error": str(e)}

    async def get_kalshi_portfolio(self) -> Dict[str, Any]:
        """GET /portfolio/balance and /portfolio/positions"""
        try:
            balance_path = "portfolio/balance"
            balance_headers = await self._get_auth_headers("GET", balance_path)
            
            positions_path = "portfolio/positions"
            positions_headers = await self._get_auth_headers("GET", positions_path)
            
            if not balance_headers or not positions_headers:
                return {"error": "Missing credentials"}
                
            balance_resp = await self.client.get(balance_path, headers=balance_headers)
            positions_resp = await self.client.get(positions_path, headers=positions_headers)
            balance_resp.raise_for_status()
            positions_resp.raise_for_status()
            return {
                "balance": balance_resp.json().get("balance", 0),
                "positions": positions_resp.json().get("positions", [])
            }
        except Exception as e:
            logger.error(f"Error fetching Kalshi portfolio: {e}")
            return {"error": str(e)}

    async def get_kalshi_market_history(self, ticker: str) -> List[Dict[str, Any]]:
        """GET market price history for chart rendering"""
        path = f"markets/{ticker}/history"
        headers = await self._get_auth_headers("GET", path)
        if not headers:
            return []
            
        try:
            # Assuming history endpoint exists in v2 context or similar
            response = await self.client.get(path, headers=headers)
            response.raise_for_status()
            return response.json().get("history", [])
        except Exception as e:
            logger.error(f"Error fetching Kalshi market history for {ticker}: {e}")
            return []

# Global instance
kalshi_service = KalshiService()

def get_kalshi_service() -> Optional[KalshiService]:
    """Factory function for safe service access."""
    if not kalshi_service.available:
        kalshi_service._warn_missing_credentials_once("service_access")
        return None
    return kalshi_service
