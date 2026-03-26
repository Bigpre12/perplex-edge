# apps/api/src/core/sports_config.py

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

# Frequency Constants (in seconds)
HIGH_FREQUENCY = 60
MEDIUM_FREQUENCY = 300
LOW_FREQUENCY = 3600

# Sport Lists for Scheduling
HIGH_FREQUENCY_SPORTS = ["basketball_nba", "americanfootball_nfl"]
MEDIUM_FREQUENCY_SPORTS = ["soccer_epl", "mma_mixed_martial_arts", "baseball_mlb"]
LOW_FREQUENCY_SPORTS = [s for s in ALL_SPORTS if s not in HIGH_FREQUENCY_SPORTS + MEDIUM_FREQUENCY_SPORTS]

# Market Definitions
PROP_MARKETS = ["points", "rebounds", "assists", "threes", "blocks", "steals", "turnovers"]
H2H_MARKETS = ["h2h", "spreads", "totals"]
