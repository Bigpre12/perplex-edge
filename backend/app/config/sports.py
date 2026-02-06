"""
Shared sport and stat-type configuration.

This module provides the single source of truth for sport keys, stat types,
and the mapping of which stat types are valid for each sport.

Keep this file in sync with frontend/src/config/sports.ts
"""

from enum import Enum
from typing import Dict, List, Set


# =============================================================================
# Sport Key Enum
# =============================================================================

class SportKey(str, Enum):
    """
    Enumeration of all supported sport keys.
    
    Values match The Odds API sport key format.
    """
    # Basketball
    BASKETBALL_NBA = "basketball_nba"
    BASKETBALL_NCAAB = "basketball_ncaab"
    BASKETBALL_WNBA = "basketball_wnba"
    
    # Football
    AMERICANFOOTBALL_NFL = "americanfootball_nfl"
    AMERICANFOOTBALL_NCAAF = "americanfootball_ncaaf"
    
    # Baseball
    BASEBALL_MLB = "baseball_mlb"
    
    # Hockey
    ICEHOCKEY_NHL = "icehockey_nhl"
    
    # Tennis
    TENNIS_ATP = "tennis_atp"
    TENNIS_WTA = "tennis_wta"
    
    # Golf
    GOLF_PGA_TOUR = "golf_pga_tour"
    
    # Soccer
    SOCCER_EPL = "soccer_epl"
    SOCCER_UEFA_CHAMPS_LEAGUE = "soccer_uefa_champs_league"
    SOCCER_UEFA_EUROPA = "soccer_uefa_europa"
    SOCCER_UEFA_CONFERENCE = "soccer_uefa_conference"
    SOCCER_USA_MLS = "soccer_usa_mls"
    
    # MMA
    MMA_MIXED_MARTIAL_ARTS = "mma_mixed_martial_arts"


# =============================================================================
# Stat Type Enum
# =============================================================================

class StatType(str, Enum):
    """
    Enumeration of all supported stat types across all sports.
    
    Values are the internal stat type identifiers used in the database.
    """
    # -------------------------------------------------------------------------
    # Basketball Stats
    # -------------------------------------------------------------------------
    POINTS = "PTS"
    REBOUNDS = "REB"
    ASSISTS = "AST"
    THREES_MADE = "3PM"
    POINTS_REBOUNDS_ASSISTS = "PRA"
    POINTS_REBOUNDS = "PR"
    POINTS_ASSISTS = "PA"
    REBOUNDS_ASSISTS = "RA"
    STEALS = "STL"
    BLOCKS = "BLK"
    TURNOVERS = "TO"
    DOUBLE_DOUBLE = "DD"
    TRIPLE_DOUBLE = "TD"
    
    # -------------------------------------------------------------------------
    # Football Stats
    # -------------------------------------------------------------------------
    PASS_YARDS = "PASS_YDS"
    PASS_TDS = "PASS_TDS"
    PASS_ATTEMPTS = "PASS_ATT"
    PASS_COMPLETIONS = "PASS_COMP"
    INTERCEPTIONS = "INT"
    RUSH_YARDS = "RUSH_YDS"
    RUSH_ATTEMPTS = "RUSH_ATT"
    RUSH_TDS = "RUSH_TDS"
    RECEPTION_YARDS = "REC_YDS"
    RECEPTIONS = "REC"
    RECEPTION_TDS = "REC_TDS"
    RUSH_RECEPTION_YARDS = "RUSH_REC_YDS"
    ANYTIME_TD = "ANYTIME_TD"
    
    # -------------------------------------------------------------------------
    # Baseball Stats
    # -------------------------------------------------------------------------
    HITS = "H"
    RUNS = "R"
    RBIS = "RBI"
    TOTAL_BASES = "TB"
    HITS_RUNS_RBIS = "HRR"
    STRIKEOUTS_PITCHER = "K"
    OUTS_RECORDED = "OUTS"
    HOME_RUNS = "HR"
    
    # -------------------------------------------------------------------------
    # Hockey Stats
    # -------------------------------------------------------------------------
    GOALS = "GOALS"
    ASSISTS_HOCKEY = "AST_H"
    POINTS_HOCKEY = "PTS_H"
    SHOTS_ON_GOAL = "SOG"
    BLOCKED_SHOTS = "BLK_SHOTS"
    SAVES_GOALIE = "SAVES"
    POWER_PLAY_POINTS = "PPP"
    PENALTY_MINUTES = "PIM"
    
    # -------------------------------------------------------------------------
    # Tennis Stats
    # -------------------------------------------------------------------------
    ACES = "ACES"
    DOUBLE_FAULTS = "DF"
    GAMES_WON = "GAMES"
    SETS_WON = "SETS"
    TOTAL_GAMES = "TOTAL_GAMES"
    
    # -------------------------------------------------------------------------
    # Golf Stats
    # -------------------------------------------------------------------------
    FINISH_POSITION = "FINISH_POS"
    MAKE_CUT = "MAKE_CUT"
    TOP_5 = "TOP_5"
    TOP_10 = "TOP_10"
    TOP_20 = "TOP_20"
    FIRST_ROUND_LEADER = "FRL"
    MATCHUP = "MATCHUP"
    BIRDIES_OR_BETTER = "BIRDIES"
    BOGEYS_OR_WORSE = "BOGEYS"
    STROKES = "STROKES"
    
    # -------------------------------------------------------------------------
    # Soccer Stats
    # -------------------------------------------------------------------------
    ANYTIME_GOAL = "ANYTIME_GOAL"
    SHOTS = "SHOTS"
    SHOTS_ON_TARGET = "SOT"
    FOULS_COMMITTED = "FOULS"
    CARDS = "CARDS"
    TACKLES = "TACKLES"
    PASSES = "PASSES"
    
    # -------------------------------------------------------------------------
    # MMA/UFC Stats
    # -------------------------------------------------------------------------
    WINNER = "WINNER"
    METHOD = "METHOD"
    TOTAL_ROUNDS = "TOTAL_ROUNDS"
    SIGNIFICANT_STRIKES = "SIG_STRIKES"
    TAKEDOWNS = "TAKEDOWNS"
    GOES_DISTANCE = "GOES_DISTANCE"
    FIGHT_TIME = "FIGHT_TIME"


# =============================================================================
# Sport ID to Key Mapping
# =============================================================================

SPORT_ID_TO_KEY: Dict[int, SportKey] = {
    # Basketball
    30: SportKey.BASKETBALL_NBA,
    32: SportKey.BASKETBALL_NCAAB,
    34: SportKey.BASKETBALL_WNBA,
    
    # Football
    31: SportKey.AMERICANFOOTBALL_NFL,
    41: SportKey.AMERICANFOOTBALL_NCAAF,
    
    # Baseball
    40: SportKey.BASEBALL_MLB,
    
    # Hockey
    44: SportKey.ICEHOCKEY_NHL,  # Legacy mapping (kept for compatibility)
    53: SportKey.ICEHOCKEY_NHL,  # Actual database ID
    
    # Tennis
    42: SportKey.TENNIS_ATP,
    43: SportKey.TENNIS_WTA,
    
    # Golf
    60: SportKey.GOLF_PGA_TOUR,
    
    # Soccer
    70: SportKey.SOCCER_EPL,
    71: SportKey.SOCCER_UEFA_CHAMPS_LEAGUE,
    72: SportKey.SOCCER_USA_MLS,
    73: SportKey.SOCCER_UEFA_EUROPA,
    74: SportKey.SOCCER_UEFA_CONFERENCE,
    
    # MMA/UFC
    80: SportKey.MMA_MIXED_MARTIAL_ARTS,
}

# Reverse mapping: sport key to primary database ID
SPORT_KEY_TO_ID: Dict[SportKey, int] = {
    SportKey.BASKETBALL_NBA: 30,
    SportKey.BASKETBALL_NCAAB: 32,
    SportKey.BASKETBALL_WNBA: 34,
    SportKey.AMERICANFOOTBALL_NFL: 31,
    SportKey.AMERICANFOOTBALL_NCAAF: 41,
    SportKey.BASEBALL_MLB: 40,
    SportKey.ICEHOCKEY_NHL: 53,
    SportKey.TENNIS_ATP: 42,
    SportKey.TENNIS_WTA: 43,
    SportKey.GOLF_PGA_TOUR: 60,
    SportKey.SOCCER_EPL: 70,
    SportKey.SOCCER_UEFA_CHAMPS_LEAGUE: 71,
    SportKey.SOCCER_USA_MLS: 72,
    SportKey.SOCCER_UEFA_EUROPA: 73,
    SportKey.SOCCER_UEFA_CONFERENCE: 74,
    SportKey.MMA_MIXED_MARTIAL_ARTS: 80,
}


# =============================================================================
# Stat Types by Sport Mapping
# =============================================================================

STAT_TYPES_BY_SPORT: Dict[SportKey, List[StatType]] = {
    # -------------------------------------------------------------------------
    # Basketball
    # -------------------------------------------------------------------------
    SportKey.BASKETBALL_NBA: [
        StatType.POINTS,
        StatType.REBOUNDS,
        StatType.ASSISTS,
        StatType.THREES_MADE,
        StatType.POINTS_REBOUNDS_ASSISTS,
        StatType.POINTS_REBOUNDS,
        StatType.POINTS_ASSISTS,
        StatType.REBOUNDS_ASSISTS,
        StatType.STEALS,
        StatType.BLOCKS,
        StatType.TURNOVERS,
        StatType.DOUBLE_DOUBLE,
        StatType.TRIPLE_DOUBLE,
    ],
    SportKey.BASKETBALL_NCAAB: [
        StatType.POINTS,
        StatType.REBOUNDS,
        StatType.ASSISTS,
        StatType.THREES_MADE,
        StatType.POINTS_REBOUNDS_ASSISTS,
    ],
    SportKey.BASKETBALL_WNBA: [
        StatType.POINTS,
        StatType.REBOUNDS,
        StatType.ASSISTS,
        StatType.THREES_MADE,
        StatType.POINTS_REBOUNDS_ASSISTS,
        StatType.STEALS,
        StatType.BLOCKS,
    ],
    
    # -------------------------------------------------------------------------
    # Football
    # -------------------------------------------------------------------------
    SportKey.AMERICANFOOTBALL_NFL: [
        StatType.PASS_YARDS,
        StatType.PASS_TDS,
        StatType.PASS_ATTEMPTS,
        StatType.PASS_COMPLETIONS,
        StatType.INTERCEPTIONS,
        StatType.RUSH_YARDS,
        StatType.RUSH_ATTEMPTS,
        StatType.RUSH_TDS,
        StatType.RECEPTION_YARDS,
        StatType.RECEPTIONS,
        StatType.RECEPTION_TDS,
        StatType.RUSH_RECEPTION_YARDS,
        StatType.ANYTIME_TD,
    ],
    SportKey.AMERICANFOOTBALL_NCAAF: [
        StatType.PASS_YARDS,
        StatType.PASS_TDS,
        StatType.INTERCEPTIONS,
        StatType.RUSH_YARDS,
        StatType.RECEPTION_YARDS,
        StatType.RECEPTIONS,
        StatType.ANYTIME_TD,
    ],
    
    # -------------------------------------------------------------------------
    # Baseball
    # -------------------------------------------------------------------------
    SportKey.BASEBALL_MLB: [
        StatType.HITS,
        StatType.RUNS,
        StatType.RBIS,
        StatType.TOTAL_BASES,
        StatType.HITS_RUNS_RBIS,
        StatType.STRIKEOUTS_PITCHER,
        StatType.OUTS_RECORDED,
        StatType.HOME_RUNS,
    ],
    
    # -------------------------------------------------------------------------
    # Hockey
    # -------------------------------------------------------------------------
    SportKey.ICEHOCKEY_NHL: [
        StatType.GOALS,
        StatType.ASSISTS_HOCKEY,
        StatType.POINTS_HOCKEY,
        StatType.SHOTS_ON_GOAL,
        StatType.BLOCKED_SHOTS,
        StatType.SAVES_GOALIE,
        StatType.POWER_PLAY_POINTS,
        StatType.PENALTY_MINUTES,
    ],
    
    # -------------------------------------------------------------------------
    # Tennis
    # -------------------------------------------------------------------------
    SportKey.TENNIS_ATP: [
        StatType.ACES,
        StatType.DOUBLE_FAULTS,
        StatType.GAMES_WON,
        StatType.SETS_WON,
        StatType.TOTAL_GAMES,
    ],
    SportKey.TENNIS_WTA: [
        StatType.ACES,
        StatType.DOUBLE_FAULTS,
        StatType.GAMES_WON,
        StatType.SETS_WON,
        StatType.TOTAL_GAMES,
    ],
    
    # -------------------------------------------------------------------------
    # Golf
    # -------------------------------------------------------------------------
    SportKey.GOLF_PGA_TOUR: [
        StatType.FINISH_POSITION,
        StatType.MAKE_CUT,
        StatType.TOP_5,
        StatType.TOP_10,
        StatType.TOP_20,
        StatType.FIRST_ROUND_LEADER,
        StatType.MATCHUP,
        StatType.BIRDIES_OR_BETTER,
        StatType.BOGEYS_OR_WORSE,
        StatType.STROKES,
    ],
    
    # -------------------------------------------------------------------------
    # Soccer
    # -------------------------------------------------------------------------
    SportKey.SOCCER_EPL: [
        StatType.GOALS,
        StatType.ANYTIME_GOAL,
        StatType.SHOTS,
        StatType.SHOTS_ON_TARGET,
        StatType.FOULS_COMMITTED,
        StatType.CARDS,
        StatType.TACKLES,
        StatType.PASSES,
    ],
    SportKey.SOCCER_UEFA_CHAMPS_LEAGUE: [
        StatType.GOALS,
        StatType.ANYTIME_GOAL,
        StatType.SHOTS,
        StatType.SHOTS_ON_TARGET,
    ],
    SportKey.SOCCER_USA_MLS: [
        StatType.GOALS,
        StatType.ANYTIME_GOAL,
        StatType.SHOTS,
        StatType.SHOTS_ON_TARGET,
    ],
    SportKey.SOCCER_UEFA_EUROPA: [
        StatType.GOALS,
        StatType.ANYTIME_GOAL,
        StatType.SHOTS,
        StatType.SHOTS_ON_TARGET,
    ],
    SportKey.SOCCER_UEFA_CONFERENCE: [
        StatType.GOALS,
        StatType.ANYTIME_GOAL,
        StatType.SHOTS,
        StatType.SHOTS_ON_TARGET,
    ],
    
    # -------------------------------------------------------------------------
    # MMA/UFC
    # -------------------------------------------------------------------------
    SportKey.MMA_MIXED_MARTIAL_ARTS: [
        StatType.WINNER,
        StatType.METHOD,
        StatType.TOTAL_ROUNDS,
        StatType.SIGNIFICANT_STRIKES,
        StatType.TAKEDOWNS,
        StatType.GOES_DISTANCE,
        StatType.FIGHT_TIME,
    ],
}

# Pre-compute sets for O(1) lookup
_STAT_TYPES_SETS_BY_SPORT: Dict[SportKey, Set[StatType]] = {
    sport: set(stats) for sport, stats in STAT_TYPES_BY_SPORT.items()
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_stat_types_for_sport(sport_key: SportKey | str) -> List[StatType]:
    """
    Get the list of valid stat types for a sport.
    
    Args:
        sport_key: Sport key (enum or string)
    
    Returns:
        List of valid StatType enums for the sport
    """
    if isinstance(sport_key, str):
        try:
            sport_key = SportKey(sport_key)
        except ValueError:
            return []
    
    return STAT_TYPES_BY_SPORT.get(sport_key, [])


def is_valid_stat_for_sport(sport_key: SportKey | str, stat_type: StatType | str) -> bool:
    """
    Check if a stat type is valid for a given sport.
    
    Args:
        sport_key: Sport key (enum or string)
        stat_type: Stat type to validate (enum or string)
    
    Returns:
        True if the stat type is valid for the sport, False otherwise
    """
    # Convert sport_key to enum if string
    if isinstance(sport_key, str):
        try:
            sport_key = SportKey(sport_key)
        except ValueError:
            return False
    
    # Convert stat_type to enum if string
    if isinstance(stat_type, str):
        try:
            stat_type = StatType(stat_type)
        except ValueError:
            return False
    
    # Check against pre-computed set for O(1) lookup
    valid_stats = _STAT_TYPES_SETS_BY_SPORT.get(sport_key)
    if valid_stats is None:
        return False
    
    return stat_type in valid_stats


def get_sport_key_from_id(sport_id: int) -> SportKey | None:
    """
    Get sport key enum from database ID.
    
    Args:
        sport_id: Database sport ID
    
    Returns:
        SportKey enum or None if not found
    """
    return SPORT_ID_TO_KEY.get(sport_id)


def get_sport_id_from_key(sport_key: SportKey | str) -> int | None:
    """
    Get database ID from sport key.
    
    Args:
        sport_key: Sport key (enum or string)
    
    Returns:
        Database sport ID or None if not found
    """
    if isinstance(sport_key, str):
        try:
            sport_key = SportKey(sport_key)
        except ValueError:
            return None
    
    return SPORT_KEY_TO_ID.get(sport_key)


# =============================================================================
# API Market Key to StatType Mapping
# =============================================================================

# Maps The Odds API market keys to internal StatType values
API_MARKET_TO_STAT_TYPE: Dict[str, StatType] = {
    # Basketball
    "player_points": StatType.POINTS,
    "player_rebounds": StatType.REBOUNDS,
    "player_assists": StatType.ASSISTS,
    "player_threes": StatType.THREES_MADE,
    "player_points_rebounds_assists": StatType.POINTS_REBOUNDS_ASSISTS,
    "player_points_rebounds": StatType.POINTS_REBOUNDS,
    "player_points_assists": StatType.POINTS_ASSISTS,
    "player_rebounds_assists": StatType.REBOUNDS_ASSISTS,
    "player_steals": StatType.STEALS,
    "player_blocks": StatType.BLOCKS,
    "player_turnovers": StatType.TURNOVERS,
    "player_double_double": StatType.DOUBLE_DOUBLE,
    "player_triple_double": StatType.TRIPLE_DOUBLE,
    
    # Football
    "player_pass_yds": StatType.PASS_YARDS,
    "player_pass_tds": StatType.PASS_TDS,
    "player_pass_attempts": StatType.PASS_ATTEMPTS,
    "player_pass_completions": StatType.PASS_COMPLETIONS,
    "player_pass_interceptions": StatType.INTERCEPTIONS,
    "player_rush_yds": StatType.RUSH_YARDS,
    "player_rush_attempts": StatType.RUSH_ATTEMPTS,
    "player_rush_tds": StatType.RUSH_TDS,
    "player_reception_yds": StatType.RECEPTION_YARDS,
    "player_receptions": StatType.RECEPTIONS,
    "player_reception_tds": StatType.RECEPTION_TDS,
    "player_anytime_td": StatType.ANYTIME_TD,
    
    # Baseball
    "batter_hits": StatType.HITS,
    "batter_runs": StatType.RUNS,
    "batter_rbis": StatType.RBIS,
    "batter_total_bases": StatType.TOTAL_BASES,
    "batter_home_runs": StatType.HOME_RUNS,
    "pitcher_strikeouts": StatType.STRIKEOUTS_PITCHER,
    "pitcher_outs": StatType.OUTS_RECORDED,
    
    # Hockey
    "player_goals": StatType.GOALS,
    "player_assists": StatType.ASSISTS_HOCKEY,
    "player_points": StatType.POINTS_HOCKEY,
    "player_shots_on_goal": StatType.SHOTS_ON_GOAL,
    "player_blocked_shots": StatType.BLOCKED_SHOTS,
    "player_saves": StatType.SAVES_GOALIE,
    "player_power_play_points": StatType.POWER_PLAY_POINTS,
    "player_penalty_minutes": StatType.PENALTY_MINUTES,
    
    # Tennis
    "player_aces": StatType.ACES,
    "player_double_faults": StatType.DOUBLE_FAULTS,
    "player_games_won": StatType.GAMES_WON,
    "player_sets_won": StatType.SETS_WON,
    "player_total_games": StatType.TOTAL_GAMES,
    
    # Golf
    "golfer_finish_position": StatType.FINISH_POSITION,
    "golfer_make_cut": StatType.MAKE_CUT,
    "golfer_top_5": StatType.TOP_5,
    "golfer_top_10": StatType.TOP_10,
    "golfer_top_20": StatType.TOP_20,
    "golfer_first_round_leader": StatType.FIRST_ROUND_LEADER,
    "golfer_matchup": StatType.MATCHUP,
    
    # Soccer
    "player_anytime_goalscorer": StatType.ANYTIME_GOAL,
    "player_shots": StatType.SHOTS,
    "player_shots_on_target": StatType.SHOTS_ON_TARGET,
    "player_fouls_committed": StatType.FOULS_COMMITTED,
    "player_cards": StatType.CARDS,
    "player_tackles": StatType.TACKLES,
    "player_passes": StatType.PASSES,
    
    # MMA/UFC
    "fighter_to_win": StatType.WINNER,
    "fight_method": StatType.METHOD,
    "fight_total_rounds": StatType.TOTAL_ROUNDS,
    "fighter_significant_strikes": StatType.SIGNIFICANT_STRIKES,
    "fighter_takedowns": StatType.TAKEDOWNS,
    "fight_goes_distance": StatType.GOES_DISTANCE,
}


def get_stat_type_from_api_market(market_key: str) -> StatType | None:
    """
    Convert an API market key to internal StatType.
    
    Args:
        market_key: The Odds API market key (e.g., "player_points")
    
    Returns:
        StatType enum or None if not recognized
    """
    return API_MARKET_TO_STAT_TYPE.get(market_key)
