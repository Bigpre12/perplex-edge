"""
SportsGameOdds League Constants
Centralized registry for all supported league IDs and their parent sports.
Data source: SportsGameOdds API Documentation.
"""

SGO_LEAGUES = {
    "AHL": {"name": "AHL", "sport_id": "HOCKEY"},
    "ATP": {"name": "ATP", "sport_id": "TENNIS"},
    "BR_SERIE_A": {"name": "Brasileiro Série A", "sport_id": "SOCCER"},
    "BUNDESLIGA": {"name": "Bundesliga", "sport_id": "SOCCER"},
    "CELEBRITY": {"name": "Celebrities", "sport_id": "NON_SPORTS"},
    "CFL": {"name": "CFL", "sport_id": "FOOTBALL"},
    "UEFA_CHAMPIONS_LEAGUE": {"name": "Champions League", "sport_id": "SOCCER"},
    "NCAAB": {"name": "College Basketball", "sport_id": "BASKETBALL"},
    "NCAAF": {"name": "College Football", "sport_id": "FOOTBALL"},
    "CPBL": {"name": "CPBL", "sport_id": "BASEBALL"},
    "EHF_EURO_CUP": {"name": "EHF European Cup", "sport_id": "HANDBALL"},
    "EHF_EURO": {"name": "EHF European League", "sport_id": "HANDBALL"},
    "EVENTS": {"name": "Events", "sport_id": "NON_SPORTS"},
    "FUN": {"name": "Fun", "sport_id": "NON_SPORTS"},
    "IHF_SUPER_GLOBE": {"name": "IHF Super Globe", "sport_id": "HANDBALL"},
    "INTERNATIONAL_SOCCER": {"name": "International Soccer", "sport_id": "SOCCER"},
    "ITF": {"name": "ITF", "sport_id": "TENNIS"},
    "KBO": {"name": "KBO", "sport_id": "BASEBALL"},
    "KHL": {"name": "KHL", "sport_id": "HOCKEY"},
    "LA_LIGA": {"name": "La Liga", "sport_id": "SOCCER"},
    "LBPRC": {"name": "LBPRC", "sport_id": "BASEBALL"},
    "LIDOM": {"name": "LIDOM", "sport_id": "BASEBALL"},
    "ASOBAL": {"name": "Liga ASOBAL", "sport_id": "HANDBALL"},
    "LIGA_MX": {"name": "Liga MX", "sport_id": "SOCCER"},
    "FR_LIGUE_1": {"name": "Ligue 1", "sport_id": "SOCCER"},
    "LIV_TOUR": {"name": "LIV Golf", "sport_id": "GOLF"},
    "LMP": {"name": "LMP", "sport_id": "BASEBALL"},
    "LVBP": {"name": "LVBP", "sport_id": "BASEBALL"},
    "MARKETS": {"name": "Markets", "sport_id": "NON_SPORTS"},
    "MLB": {"name": "MLB", "sport_id": "BASEBALL"},
    "MLB_MINORS": {"name": "MLB Minors", "sport_id": "BASEBALL"},
    "MLS": {"name": "MLS", "sport_id": "SOCCER"},
    "MOVIES": {"name": "Movies", "sport_id": "NON_SPORTS"},
    "MUSIC": {"name": "Music", "sport_id": "NON_SPORTS"},
    "NBA": {"name": "NBA", "sport_id": "BASKETBALL"},
    "NBA_G_LEAGUE": {"name": "NBA G-League", "sport_id": "BASKETBALL"},
    "NFL": {"name": "NFL", "sport_id": "FOOTBALL"},
    "NHL": {"name": "NHL", "sport_id": "HOCKEY"},
    "NPB": {"name": "NPB", "sport_id": "BASEBALL"},
    "PGA_MEN": {"name": "PGA Men", "sport_id": "GOLF"},
    "PGA_WOMEN": {"name": "PGA Women", "sport_id": "GOLF"},
    "POLITICS": {"name": "Politics", "sport_id": "NON_SPORTS"},
    "EPL": {"name": "Premier League", "sport_id": "SOCCER"},
    "SEHA": {"name": "SEHA Liga", "sport_id": "HANDBALL"},
    "IT_SERIE_A": {"name": "Serie A Italy", "sport_id": "SOCCER"},
    "SHL": {"name": "SHL", "sport_id": "HOCKEY"},
    "TV": {"name": "TV", "sport_id": "NON_SPORTS"},
    "UEFA_EUROPA_LEAGUE": {"name": "UEFA Europa League", "sport_id": "SOCCER"},
    "UFC": {"name": "UFC", "sport_id": "MMA"},
    "USFL": {"name": "USFL", "sport_id": "FOOTBALL"},
    "WBC": {"name": "WBC", "sport_id": "BASEBALL"},
    "WEATHER": {"name": "Weather", "sport_id": "NON_SPORTS"},
    "WNBA": {"name": "WNBA", "sport_id": "BASKETBALL"},
    "WTA": {"name": "Women's Tennis", "sport_id": "TENNIS"},
    "XFL": {"name": "XFL", "sport_id": "FOOTBALL"},
}

def get_sgo_league_name(league_id: str) -> str:
    """Get display name for an SGO league ID."""
    return SGO_LEAGUES.get(league_id.upper(), {}).get("name", league_id.upper())

def get_sgo_league_sport(league_id: str) -> str:
    """Get parent sport ID for an SGO league ID."""
    return SGO_LEAGUES.get(league_id.upper(), {}).get("sport_id", "UNKNOWN")
