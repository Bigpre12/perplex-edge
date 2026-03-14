"""
SportsGameOdds Sport Constants
Centralized registry for all supported sport IDs.
Data source: SportsGameOdds API Documentation.
"""

SGO_SPORTS = {
    "AUSSIE_RULES_FOOTBALL": "Aussie Rules",
    "BADMINTON": "Badminton",
    "BANDY": "Bandy",
    "BASEBALL": "Baseball",
    "BASKETBALL": "Basketball",
    "BEACH_VOLLEYBALL": "Beach Volleyball",
    "BOXING": "Boxing",
    "CRICKET": "Cricket",
    "DARTS": "Darts",
    "ESPORTS": "ESports",
    "FLOORBALL": "Floorball",
    "FOOTBALL": "Football",
    "FUTSAL": "Futsal",
    "GOLF": "Golf",
    "HANDBALL": "Handball",
    "HOCKEY": "Hockey",
    "HORSE_RACING": "Horse Racing",
    "LACROSSE": "Lacrosse",
    "MMA": "MMA",
    "MOTORSPORTS": "Motorsports",
    "NON_SPORTS": "Non-Sports",
    "RUGBY": "Rugby",
    "SNOOKER": "Snooker",
    "SOCCER": "Soccer",
    "TABLE_TENNIS": "Table Tennis",
    "TENNIS": "Tennis",
    "VOLLEYBALL": "Volleyball",
    "WATER_POLO": "Water Polo",
}

def get_sgo_sport_display(sport_id: str) -> str:
    """Get display name for an SGO sport ID."""
    return SGO_SPORTS.get(sport_id.upper(), sport_id.replace("_", " ").title())
