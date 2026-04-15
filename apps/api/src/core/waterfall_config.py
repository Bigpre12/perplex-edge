"""
Single source of truth for multi-provider waterfall chains.

Chains are ordered provider IDs per (sport_key, data_type). Callers map
`data_type` aliases (e.g. ``stats``) to canonical types via ``resolve_data_type``.

Env:
    WATERFALL_CONFIG_VERSION — ``1`` preserves legacy router chains; ``2`` (default)
    uses the unified matrix-aligned ordering.
"""
from __future__ import annotations

import os
from typing import Dict, List, Sequence

# Canonical data types (enum-like strings)
ODDS_PREGAME = "odds_pregame"
ODDS_LIVE = "odds_live"
PLAYER_PROPS = "player_props"
SCHEDULE = "schedule"  # games / scoreboard-adjacent schedule fetch via stats path (alias: stats)
INJURIES = "injuries"
SCORES = "scores"
TEAM_STATS = "team_stats"
METADATA = "metadata"
KALSHI = "kalshi"
CONSENSUS_LINES = "consensus_lines"

# Aliases from legacy callers → canonical
_DATA_TYPE_ALIASES: Dict[str, str] = {
    "odds": ODDS_PREGAME,
    "stats": SCHEDULE,
    "games": SCHEDULE,
    "schedule": SCHEDULE,
    "live": ODDS_LIVE,
}

US_SPORTS_PREFIXES = (
    "basketball_nba",
    "americanfootball_nfl",
    "baseball_mlb",
    "icehockey_nhl",
    "basketball_ncaab",
    "americanfootball_ncaaf",
    "basketball_wnba",
    "basketball_ncaaw",
)
SOCCER_MARKERS = ("soccer_", "epl", "mls", "uefa", "la_liga", "bundesliga", "serie_a", "ligue_1")
MMA_MARKERS = ("mma_", "ufc", "mixed_martial")

SHORT_TO_CANONICAL: Dict[str, str] = {
    "nba": "basketball_nba",
    "nfl": "americanfootball_nfl",
    "mlb": "baseball_mlb",
    "nhl": "icehockey_nhl",
    "ncaab": "basketball_ncaab",
    "ncaaf": "americanfootball_ncaaf",
    "wnba": "basketball_wnba",
    "epl": "soccer_epl",
    "mls": "soccer_usa_mls",
}


def canonical_sport_key(sport: str) -> str:
    s = (sport or "").strip().lower()
    if s in SHORT_TO_CANONICAL:
        return SHORT_TO_CANONICAL[s]
    return s


def resolve_data_type(data_type: str) -> str:
    dt = (data_type or SCHEDULE).strip().lower()
    return _DATA_TYPE_ALIASES.get(dt, dt)


def _is_us_sport(sport: str) -> bool:
    sk = canonical_sport_key(sport)
    return sk.startswith(US_SPORTS_PREFIXES) or "basketball" in sk or "americanfootball" in sk


def _is_soccer(sport: str) -> bool:
    sk = canonical_sport_key(sport)
    return any(m in sk for m in SOCCER_MARKERS) or "soccer" in sk


def _is_mma(sport: str) -> bool:
    sk = canonical_sport_key(sport)
    return any(m in sk for m in MMA_MARKERS)


def _chain_schedule_v2(sport: str) -> List[str]:
    if _is_us_sport(sport):
        return ["balldontlie", "api_sports", "thesportsdb", "espn"]
    if _is_soccer(sport):
        return ["api_sports", "sportmonks", "thesportsdb", "espn"]
    if _is_mma(sport):
        return ["api_sports", "thesportsdb", "espn"]
    return ["thesportsdb", "espn"]


def _chain_odds_pregame_v2(sport: str) -> List[str]:
    sk = canonical_sport_key(sport)
    # MMA: free UFC-heavy path first when keys exist
    if _is_mma(sk):
        return ["sportsgameodds", "the_odds_api", "betstack", "therundown", "isports", "api_sports"]
    if sk.startswith("tennis_") or sk.startswith("golf_"):
        return ["the_odds_api", "betstack", "sportsgameodds"]
    if _is_soccer(sk):
        return [
            "the_odds_api",
            "sportmonks",
            "betstack",
            "isports",
            "therundown",
            "sportsgameodds",
            "api_sports",
        ]
    # Default US + global major leagues
    return [
        "the_odds_api",
        "betstack",
        "therundown",
        "sportsgameodds",
        "isports",
        "api_sports",
    ]


def _chain_odds_pregame_v1(sport: str) -> List[str]:
    """Legacy chains from pre-unification router."""
    sk = canonical_sport_key(sport)
    if _is_soccer(sk):
        return ["the_odds_api", "isports", "sportmonks"]
    return ["the_odds_api", "isports", "api_sports"]


def _chain_schedule_v1(sport: str) -> List[str]:
    sk = canonical_sport_key(sport)
    us_short = ["nba", "nfl", "mlb", "nhl", "wnba", "ncaaf", "ncaab", "ncaaw"]
    if sk in us_short or "basketball" in sk or "americanfootball" in sk:
        return ["balldontlie", "api_sports", "thesportsdb", "espn"]
    soccer_short = ["epl", "uefa", "mls", "la_liga", "bundesliga", "serie_a", "ligue_1"]
    if sk in soccer_short or "soccer" in sk:
        return ["api_sports", "sportmonks", "thesportsdb", "espn"]
    if "ufc" in sk or "mma" in sk:
        return ["api_sports", "thesportsdb", "espn"]
    return ["thesportsdb", "espn"]


def _config_version() -> str:
    return os.getenv("WATERFALL_CONFIG_VERSION", "2").strip()


def get_provider_chain(sport_key: str, data_type: str = SCHEDULE) -> List[str]:
    """
    Return ordered provider IDs for ``sport_key`` and ``data_type``.
    ``data_type`` may be an alias (``odds``, ``stats``).
    """
    canonical_dt = resolve_data_type(data_type)
    ver = _config_version()

    if canonical_dt == SCHEDULE:
        return _chain_schedule_v1(sport_key) if ver == "1" else _chain_schedule_v2(sport_key)

    if canonical_dt in (ODDS_PREGAME, ODDS_LIVE):
        if ver == "1":
            return _chain_odds_pregame_v1(sport_key)
        if canonical_dt == ODDS_LIVE:
            # No separate live client tier in repo v1 — same as pregame
            return _chain_odds_pregame_v2(sport_key)
        return _chain_odds_pregame_v2(sport_key)

    if canonical_dt == CONSENSUS_LINES:
        return ["betstack", "the_odds_api"]

    if canonical_dt == PLAYER_PROPS:
        return ["the_odds_api", "oddspapi"]

    if canonical_dt == INJURIES:
        return ["espn", "api_sports", "thesportsdb"]

    if canonical_dt == SCORES:
        return ["espn", "api_sports", "sportmonks", "thesportsdb"]

    if canonical_dt == TEAM_STATS:
        return ["api_sports", "balldontlie", "sportmonks", "thesportsdb"]

    if canonical_dt == METADATA:
        return ["thesportsdb", "espn", "api_sports"]

    if canonical_dt == KALSHI:
        return ["kalshi"]

    return _chain_schedule_v2(sport_key)


# Sports that appear in product mappings / routers (extend as new leagues ship)
_REGISTRY_SPORT_KEYS: Sequence[str] = (
    "basketball_nba",
    "americanfootball_nfl",
    "baseball_mlb",
    "icehockey_nhl",
    "basketball_ncaab",
    "americanfootball_ncaaf",
    "basketball_wnba",
    "basketball_ncaaw",
    "tennis_atp",
    "tennis_wta",
    "golf_pga",
    "mma_mixed_martial_arts",
    "boxing_boxing",
    "soccer_epl",
    "soccer_usa_mls",
    "soccer_uefa_champions_league",
)


def all_registry_sport_keys() -> List[str]:
    return list(_REGISTRY_SPORT_KEYS)


# For meta / observability — not every ID has a live client yet
KNOWN_PROVIDER_IDS: List[str] = [
    "the_odds_api",
    "betstack",
    "therundown",
    "sportsgameodds",
    "isports",
    "api_sports",
    "sportmonks",
    "balldontlie",
    "thesportsdb",
    "espn",
    "kalshi",
    "oddspapi",
    "statsbomb",
    "sportradar",
    "sportsdataio",
]
