"""
Quota thresholds for the ingest governor (complements odds_quota_store header sync).
"""
from __future__ import annotations

import os

# Block HTTP when used/limit >= this (reserve tail of monthly budget).
HARD_STOP_PCT = float(os.getenv("ODDS_API_HARD_STOP_PCT", "0.95"))
# Above this fraction used, prefer skipping redundant fetches when cache is still fresh.
CONSERVATIVE_PCT = float(os.getenv("ODDS_API_QUOTA_CONSERVATIVE_PCT", "0.60"))
WARNING_PCT = float(os.getenv("ODDS_API_QUOTA_WARNING_PCT", "0.80"))


def scale_interval_seconds(base_seconds: int, quota_pct: float) -> int:
    """Extend poll spacing as quota burns (for schedulers that read this)."""
    b = max(60, int(base_seconds))
    if quota_pct >= HARD_STOP_PCT:
        return 999_999
    if quota_pct >= WARNING_PCT:
        return b * 4
    if quota_pct >= CONSERVATIVE_PCT:
        return b * 2
    return b
