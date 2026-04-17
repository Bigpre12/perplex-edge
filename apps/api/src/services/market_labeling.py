"""
Human-readable market labels for persistence (edges_ev_history, etc.).
Ensures NOT NULL / display constraints even when upstream omits market_label.
"""
from __future__ import annotations

from typing import Any, Dict

# Odds API canonical market keys -> display label
MARKET_LABELS: Dict[str, str] = {
    "h2h": "Moneyline",
    "spreads": "Spread",
    "totals": "Total",
    "outrights": "Outright",
    "player_points": "Player Points",
    "player_rebounds": "Player Rebounds",
    "player_assists": "Player Assists",
    "player_threes": "Player Threes",
    "player_blocks": "Player Blocks",
    "player_steals": "Player Steals",
    "player_points_rebounds_assists": "Player PRA",
    "player_points_rebounds": "Player Points + Rebounds",
    "player_points_assists": "Player Points + Assists",
    "player_shots_on_goal": "Player Shots on Goal",
    "player_power_play_points": "Player Power Play Points",
    "player_pass_yds": "Player Pass Yards",
    "player_rush_yds": "Player Rush Yards",
    "player_reception_yds": "Player Reception Yards",
    "player_receptions": "Player Receptions",
    "pitcher_strikeouts": "Pitcher Strikeouts",
    "batter_hits": "Batter Hits",
    "batter_home_runs": "Batter Home Runs",
    "batter_rbis": "Batter RBIs",
}


def _title_from_snake(key: str) -> str:
    s = key.replace("_", " ").strip()
    return s.title() if s else "Unknown Market"


def derive_market_label(row: Dict[str, Any]) -> str:
    """
    Resolve a non-empty display label from a row dict (supports marketlabel / market_label / market_key).
    """
    raw = (
        row.get("marketlabel")
        or row.get("market_label")
        or row.get("marketLabel")
    )
    if isinstance(raw, str) and raw.strip():
        return raw.strip()[:512]

    mk = row.get("market_key") or row.get("marketkey") or ""
    key = str(mk).strip().lower()
    if not key:
        return "Unknown Market"

    if key in MARKET_LABELS:
        return MARKET_LABELS[key]

    if key.startswith("player"):
        inner = key[len("player") :].lstrip("_")
        if inner:
            return "Player " + _title_from_snake(inner)
        return "Player Prop"

    if key.startswith("batter_") or key.startswith("pitcher_"):
        return _title_from_snake(key)

    return _title_from_snake(key)[:512]
