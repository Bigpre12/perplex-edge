"""
Quota thresholds for the ingest governor (complements odds_quota_store header sync).
"""
from __future__ import annotations

import os

# Block HTTP when used/limit >= this (reserve tail of monthly budget).
HARD_STOP_PCT = float(os.getenv("ODDS_API_HARD_STOP_PCT", "0.85"))
# Above this fraction used, prefer skipping redundant fetches when cache is still fresh.
CONSERVATIVE_PCT = float(os.getenv("ODDS_API_QUOTA_CONSERVATIVE_PCT", "0.60"))
WARNING_PCT = float(
    os.getenv("ODDS_API_WARN_PCT")
    or os.getenv("ODDS_API_USAGE_WARN_PCT")
    or os.getenv("ODDS_API_QUOTA_WARNING_PCT", "0.80")
)
# Mirrors odds_quota_store.monthly_limit() for operators reading quota_guard only.
_ml_raw = os.getenv("ODDS_API_MONTHLY_LIMIT") or os.getenv("THE_ODDS_API_MAX_CALLS_PER_MONTH", "20000")
try:
    MONTHLY_LIMIT = max(0, int(_ml_raw))
except (TypeError, ValueError):
    MONTHLY_LIMIT = 20_000


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
