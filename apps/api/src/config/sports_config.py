# apps/api/src/config/sports_config.py

# Mapping frontend sport keys to The Odds API keys
SPORT_MAP = {
    "basketball_nba": "basketball_nba",
    "americanfootball_nfl": "americanfootball_nfl",
    "baseball_mlb": "baseball_mlb",
    "icehockey_nhl": "icehockey_nhl",
    "basketball_ncaab": "basketball_ncaab",
    "basketball_wnba": "basketball_wnba",
    "mma_mixed_martial_arts": "mma_mixed_martial_arts",
    "tennis_atp": "tennis_atp_french_open",
    "boxing_boxing": "boxing_boxing",
    "soccer_epl": "soccer_epl",
    "soccer_mls": "soccer_usa_mls",
}

# Mapping frontend sport keys to ESPN API paths
ESPN_MAP = {
    "basketball_nba": "basketball/nba",
    "americanfootball_nfl": "football/nfl",
    "baseball_mlb": "baseball/mlb",
    "icehockey_nhl": "hockey/nhl",
    "basketball_ncaab": "basketball/mens-college-basketball",
    "basketball_wnba": "basketball/wnba",
    "mma_mixed_martial_arts": "mma/ufc",
    "soccer_mls": "soccer/usa.1",
    "soccer_epl": "soccer/eng.1",
}

# Supported prop markets per sport as requested by user
PROP_MARKETS = {
    "basketball_nba": "player_points,player_rebounds,player_assists,player_threes,player_blocks,player_steals",
    "americanfootball_nfl": "player_pass_yds,player_rush_yds,player_reception_yds,player_tds,player_receptions",
    "baseball_mlb": "player_hits,player_home_runs,player_rbis,player_strikeouts,player_walks",
    "icehockey_nhl": "player_points,player_goals,player_assists,player_shots_on_goal",
    "basketball_ncaab": "player_points,player_rebounds,player_assists",
    "basketball_wnba": "player_points,player_rebounds,player_assists",
    "mma_mixed_martial_arts": "fighter_method_of_victory",
    "tennis_atp": "player_games_won",
    "boxing_boxing": "method_of_victory,total_rounds",
    "soccer_mls": "h2h,total_goals,both_teams_to_score",
    "soccer_epl": "h2h,total_goals,both_teams_to_score",
}

SPORT_DISPLAY = {
    "basketball_nba": "NBA",
    "americanfootball_nfl": "NFL",
    "baseball_mlb": "MLB",
    "icehockey_nhl": "NHL",
    "basketball_ncaab": "NCAAB",
    "basketball_wnba": "WNBA",
    "mma_mixed_martial_arts": "MMA/UFC",
    "tennis_atp": "Tennis",
    "boxing_boxing": "Boxing",
    "soccer_mls": "MLS",
    "soccer_epl": "EPL",
}

# ── Tiered polling intervals by sport priority ──
HIGH_FREQUENCY = [
    "basketball_nba",
    "americanfootball_nfl",
    "baseball_mlb",
    "icehockey_nhl",
    "basketball_ncaab",
    "americanfootball_ncaaf",
]

MEDIUM_FREQUENCY = [
    "soccer_usa_mls",
    "soccer_epl",
    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "mma_mixed_martial_arts",
    "tennis_atp_french_open",
    "tennis_wta_french_open",
    "tennis_atp_wimbledon",
    "tennis_wta_wimbledon",
    "tennis_atp_us_open",
    "tennis_wta_us_open",
    "tennis_atp_aus_open",
    "tennis_wta_aus_open",
]

LOW_FREQUENCY = [
    "golf_pga_championship",
    "golf_the_masters",
    "golf_us_open",
    "golf_the_open_championship",
    "boxing_boxing",
    "motorsport_formula_1",
    "aussierules_afl",
    "rugbyleague_nrl",
    "cricket_icc_world_cup",
]

ALL_SPORTS = list(set(HIGH_FREQUENCY + MEDIUM_FREQUENCY + LOW_FREQUENCY + list(SPORT_MAP.keys())))
