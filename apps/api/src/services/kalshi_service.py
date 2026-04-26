import os
import httpx
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
        self.client = httpx.AsyncClient(base_url=self.base_url)
        self._private_key = None
        self._missing_credentials_warned = False

        # Prefer inline PEM (KALSHI_PRIVATE_KEY), then file path (KALSHI_PRIVATE_KEY_PATH)
        raw = (self.private_key_content or "").strip()
        if not raw and self.private_key_path and os.path.exists(str(self.private_key_path)):
            try:
                with open(str(self.private_key_path), encoding="utf-8") as f:
                    raw = f.read()
            except OSError:
                try:
                    with open(str(self.private_key_path), "rb") as f:
                        raw = f.read().decode("utf-8", errors="replace")
                except OSError as e:
                    logger.error("KalshiService: Could not read private key file: %s", e)

        if self.private_key_b64:
            try:
                key_bytes = base64.b64decode(self.private_key_b64)
                self._private_key = serialization.load_pem_private_key(
                    key_bytes,
                    password=None,
                    backend=default_backend(),
                )
                logger.info("KalshiService: RSA private key loaded from base64 env")
            except Exception as e:
                logger.error("KalshiService: Failed to load base64 private key: %s", e)
        elif raw:
            try:
                key_bytes = raw.replace("\\n", "\n").encode("utf-8")
                self._private_key = serialization.load_pem_private_key(
                    key_bytes,
                    password=None,
                    backend=default_backend(),
                )
                logger.info("KalshiService: RSA private key loaded")
            except Exception as e:
                logger.error("KalshiService: Failed to load private key: %s", e)

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
        
        pk = self._private_key
        if pk is not None:
            signature = pk.sign(
                payload.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
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
        full_path = parsed_base.path + path if not path.startswith('/') else parsed_base.path + path
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
        path = "/markets"
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
        path = f"/markets/{ticker}/orderbook"
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
        path = "/events"
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
        path = "/portfolio/orders"
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
            balance_path = "/portfolio/balance"
            balance_headers = await self._get_auth_headers("GET", balance_path)
            
            positions_path = "/portfolio/positions"
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
        path = f"/markets/{ticker}/history"
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
