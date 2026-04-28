import httpx
from services.api_telemetry import InstrumentedAsyncClient
import logging
import os
from typing import Dict, List, Optional, Any
from core.config import settings
from services.cache import cache

logger = logging.getLogger(__name__)

class ProviderUnavailableError(Exception):
    """Custom exception for unified error handling in waterfall."""
    pass

class ISportsClient:
    """
    Twin-Key Authentication Client for iSports API.
    Uses account + secret query parameters.

    If TLS verification fails against this host (hostname mismatch), set
    ``ISPORTS_VERIFY_TLS=false`` in Railway and redeploy.

    Environment variables (Railway): ``ISPORTS_ACCOUNT``, ``ISPORTS_SECRET``;
    optional ``ISPORTS_VERIFY_TLS`` (default true).
    """
    BASE_URL = "https://api.isportsapi.com"

    def __init__(self):
        # We assume ISPORTS_ACCOUNT and ISPORTS_SECRET are configured in core/config
        self.account = os.getenv("ISPORTS_ACCOUNT", "")
        self.secret = os.getenv("ISPORTS_SECRET", "")
        self.timeout = 10.0
        self._verify_tls = os.getenv("ISPORTS_VERIFY_TLS", "true").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        self._logged_insecure_tls = False

    async def _fetch(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Unified fetch with twin-key query parameters."""
        if not self.account or not self.secret:
            raise ProviderUnavailableError("ISPORTS credentials not configured")

        url = f"{self.BASE_URL}{endpoint}"
        query_params = params or {}
        query_params["account"] = self.account
        query_params["secret"] = self.secret
        
        try:
            if not self._verify_tls and not self._logged_insecure_tls:
                logger.warning(
                    "iSports: TLS certificate verification disabled (ISPORTS_VERIFY_TLS=false); "
                    "use only if upstream has a broken chain."
                )
                self._logged_insecure_tls = True
            async with InstrumentedAsyncClient(provider="isports", timeout=self.timeout, verify=self._verify_tls) as client:
                logger.info(f"🌐 iSports: Fetching {endpoint} (params={list(query_params.keys())})")
                resp = await client.get(url, params=query_params)
                
                if resp.status_code == 200:
                    return resp.json().get("data", [])
                elif resp.status_code in [401, 429]:
                    raise ProviderUnavailableError(f"iSports auth/rate failure: {resp.status_code}")
                else:
                    return []
        except httpx.HTTPError as e:
            raise ProviderUnavailableError(f"iSports connection failed: {e}")

    async def get_games(self, sport: str, date: Optional[str] = None) -> List[Dict]:
        """Fetch games for a specific sport and date."""
        path = f"/sport/{sport}/schedule"
        params = {"date": date} if date else {}
        return await self._fetch(path, params=params)

    async def get_odds(self, sport: str, fixture_id: int) -> List[Dict]:
        """Fetch odds for a fixture."""
        return await self._fetch(f"/sport/{sport}/odds", params={"fixtureId": fixture_id})

    async def get_historical_odds(self, sport: str, date: str) -> List[Dict]:
        """Fetch historical odds."""
        return await self._fetch(f"/historical/{sport}/odds", params={"date": date})

isports_client = ISportsClient()
