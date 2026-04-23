# apps/api/src/core/sports_config.py
"""Sport keys and scheduling. Ingest intervals are minimum spacing for quota safety (FIX 16)."""

SPORT_MAP = {
    "basketball_nba": "NBA",
    "basketball_wnba": "WNBA",
    "basketball_ncaab": "NCAAB",
    "americanfootball_nfl": "NFL",
    "americanfootball_ncaaf": "NCAAF",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "soccer_epl": "EPL",
    "soccer_uefa_champs_league": "UCL",
    "mma_mixed_martial_arts": "UFC",
    "golf_pga_tour": "PGA"
}

SPORT_DISPLAY = SPORT_MAP
ALL_SPORTS = list(SPORT_MAP.keys())
VALID_SPORTS = ALL_SPORTS
SPORT_KEYS = ALL_SPORTS

# --- Minimum minutes between scheduled odds ingests per sport (FIX 16 / quota) ---
_INGEST_MINUTES_BY_SPORT = {
    "basketball_nba": 8,
    "americanfootball_nfl": 15,
    "baseball_mlb": 10,
}
_DEFAULT_INGEST_MINUTES = 20


def ingest_interval_minutes_for_sport(sport_key: str) -> int:
    """Minimum minutes between scheduled ingest jobs for this sport."""
    return int(_INGEST_MINUTES_BY_SPORT.get(sport_key, _DEFAULT_INGEST_MINUTES))


def ingest_interval_seconds_for_sport(sport_key: str) -> float:
    return float(ingest_interval_minutes_for_sport(sport_key) * 60)

# Market Definitions
PROP_MARKETS = ["points", "rebounds", "assists", "threes", "blocks", "steals", "turnovers"]
H2H_MARKETS = ["h2h", "spreads", "totals"]
