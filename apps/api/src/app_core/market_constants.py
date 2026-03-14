"""
SportsGameOdds Market Constants
Centralized registry for stat IDs, periods, and bet types.
Data source: SportsGameOdds API Documentation.
"""

# statID mapping
SGO_STAT_IDS = {
    "points": "points",
    "rebounds": "rebounds",
    "assists": "assists",
    "threePointersMade": "three_pointers_made",
    "points+rebounds+assists": "pra",
    "points+assists": "pa",
    "points+rebounds": "pr",
    "rebounds+assists": "ra",
}

# periodID mapping
SGO_PERIOD_IDS = {
    "game": "Full Game",
    "1h": "1st Half",
    "2h": "2nd Half",
    "1q": "1st Quarter",
    "2q": "2nd Quarter",
    "3q": "3rd Quarter",
    "4q": "4th Quarter",
    "1i": "1st Inning",
    "1ix3": "1st 3 Innings",
    "1ix5": "1st 5 Innings", # Deprecated but still documented
}

# betTypeID mapping
SGO_BET_TYPES = {
    "ml": "Moneyline",
    "sp": "Spread",
    "ou": "Over/Under",
    "ml3way": "3-Way Moneyline",
}

# sideID mapping
SGO_SIDES = {
    "home": "Home",
    "away": "Away",
    "over": "Over",
    "under": "Under",
    "draw": "Draw",
    "all": "All",
}

def get_stat_display(stat_id: str) -> str:
    return SGO_STAT_IDS.get(stat_id, stat_id.replace("_", " ").title())

def get_period_display(period_id: str) -> str:
    return SGO_PERIOD_IDS.get(period_id, period_id.upper())

def get_bet_type_display(bet_type_id: str) -> str:
    return SGO_BET_TYPES.get(bet_type_id, bet_type_id.upper())
