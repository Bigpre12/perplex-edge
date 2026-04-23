"""
TheOddsAPI — single backend entry point (FIX 16).

All production HTTP calls to api.the-odds-api.com must go through `OddsApiClient`
in `services.odds_api_client` (singleton `odds_api_client` / `odds_api`).

This module documents that contract and re-exports the client for imports that
prefer `services.odds_service`.

Do not add parallel httpx clients to TheOddsAPI elsewhere; extend `OddsApiClient` instead
so quota, caching, and DB persistence stay centralized.
"""

from services.odds_api_client import OddsApiClient, odds_api, odds_api_client

__all__ = ["OddsApiClient", "odds_api", "odds_api_client"]
