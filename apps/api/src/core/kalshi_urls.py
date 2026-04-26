"""Kalshi REST ↔ WebSocket URL helpers (demo vs production must match or handshake returns 401)."""
from __future__ import annotations

import os
from typing import Optional

DEMO_REST = "https://demo-api.kalshi.co/trade-api/v2"
DEMO_WS = "wss://demo-api.kalshi.co/trade-api/ws/v2"
PROD_REST = "https://api.elections.kalshi.com/trade-api/v2"
PROD_WS = "wss://api.elections.kalshi.com/trade-api/ws/v2"


def kalshi_rest_to_ws_url(rest_url: str) -> str:
    """Map Kalshi Trade API v2 REST base to the matching WebSocket URL."""
    r = (rest_url or "").strip().rstrip("/")
    if not r:
        return DEMO_WS
    ws = r.replace("https://", "wss://").replace("http://", "ws://")
    if ws.endswith("/trade-api/v2"):
        return ws[: -len("/trade-api/v2")] + "/trade-api/ws/v2"
    if "/trade-api/v2" in ws:
        return ws.replace("/trade-api/v2", "/trade-api/ws/v2", 1)
    return DEMO_WS


def resolve_kalshi_ws_url(
    ws_url_override: Optional[str],
    rest_base_url: Optional[str],
) -> str:
    """
    Prefer explicit KALSHI_WS_URL; otherwise derive from KALSHI_BASE_URL;
    else infer from KALSHI_ENV=production; else demo.
    """
    if ws_url_override and ws_url_override.strip():
        return ws_url_override.strip().rstrip("/")

    rest = (rest_base_url or "").strip().rstrip("/")
    if rest:
        return kalshi_rest_to_ws_url(rest)

    if os.getenv("KALSHI_ENV", "").strip().lower() in ("prod", "production", "live"):
        return PROD_WS

    return DEMO_WS


def sanitize_kalshi_base_url(raw_url: Optional[str]) -> str:
    """
    Normalize malformed env values and enforce trade-api/v2 path.
    """
    cleaned = (raw_url or "").strip().strip("`").rstrip("/")
    if not cleaned:
        return default_kalshi_rest_url()
    if "/trade-api/v2" not in cleaned:
        cleaned = cleaned + "/trade-api/v2"
    return cleaned


def default_kalshi_rest_url() -> str:
    if os.getenv("KALSHI_ENV", "").strip().lower() in ("prod", "production", "live"):
        return PROD_REST
    return DEMO_REST
