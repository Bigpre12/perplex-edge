"""
Defense vs Position (DvP) Service
Provides categorical rankings of how well an opposing team defends a specific player position.
Powers the Matchup Badge (Favorable / Neutral / Tough) on the frontend.
"""
import random
from typing import Dict, Any

# Mock positional rankings for 30 NBA teams and 32 NFL teams based on
# 1 = easiest matchup (allows most points/yards to the position) -> Favorable
# 30/32 = hardest matchup (allows least points/yards to the position) -> Tough

def _get_nba_dvp() -> Dict[str, Dict[str, int]]:
    """Generates mock rankings 1-30 for NBA teams against positions."""
    teams = [
        "Hawks", "Celtics", "Nets", "Hornets", "Bulls", "Cavaliers", "Mavericks", "Nuggets",
        "Pistons", "Warriors", "Rockets", "Pacers", "Clippers", "Lakers", "Grizzlies",
        "Heat", "Bucks", "Timberwolves", "Pelicans", "Knicks", "Thunder", "Magic",
        "76ers", "Suns", "Trail Blazers", "Kings", "Spurs", "Raptors", "Jazz", "Wizards"
    ]
    positions = ["PG", "SG", "SF", "PF", "C"]
    
    dvp = {}
    for team in teams:
        dvp[team] = {}
        for pos in positions:
            seed = sum(ord(c) for c in team) + sum(ord(c) for c in pos)
            random.seed(seed)
            dvp[team][pos] = random.randint(1, 30)
    
    random.seed()
    return dvp

def _get_nfl_dvp() -> Dict[str, Dict[str, int]]:
    """Generates mock rankings 1-32 for NFL teams against positions."""
    teams = [
        "Cardinals", "Falcons", "Ravens", "Bills", "Panthers", "Bears", "Bengals", "Browns",
        "Cowboys", "Broncos", "Lions", "Packers", "Texans", "Colts", "Jaguars", "Chiefs",
        "Raiders", "Chargers", "Rams", "Dolphins", "Vikings", "Patriots", "Saints", "Giants",
        "Jets", "Eagles", "Steelers", "49ers", "Seahawks", "Buccaneers", "Titans", "Commanders"
    ]
    positions = ["QB", "RB", "WR", "TE"]
    
    dvp = {}
    for team in teams:
        dvp[team] = {}
        for pos in positions:
            seed = sum(ord(c) for c in team) + sum(ord(c) for c in pos)
            random.seed(seed)
            dvp[team][pos] = random.randint(1, 32)
            
    random.seed()
    return dvp

def _get_mlb_dvp() -> Dict[str, Dict[str, int]]:
    """Generates mock rankings 1-30 for MLB teams against positions."""
    teams = [
        "Diamondbacks", "Braves", "Orioles", "Red Sox", "Cubs", "White Sox", "Reds", "Guardians",
        "Rockies", "Tigers", "Astros", "Royals", "Angels", "Dodgers", "Marlins", "Brewers",
        "Twins", "Mets", "Yankees", "Athletics", "Phillies", "Pirates", "Padres", "Giants",
        "Mariners", "Cardinals", "Rays", "Rangers", "Blue Jays", "Nationals"
    ]
    positions = ["P", "C", "1B", "2B", "3B", "SS", "OF"]
    
    dvp = {}
    for team in teams:
        dvp[team] = {}
        for pos in positions:
            seed = sum(ord(c) for c in team) + sum(ord(c) for c in pos)
            random.seed(seed)
            dvp[team][pos] = random.randint(1, 30)
            
    random.seed()
    return dvp

def _get_nhl_dvp() -> Dict[str, Dict[str, int]]:
    """Generates mock rankings 1-32 for NHL teams against positions."""
    teams = [
        "Ducks", "Coyotes", "Bruins", "Sabres", "Flames", "Hurricanes", "Blackhawks", "Avalanche",
        "Blue Jackets", "Stars", "Red Wings", "Oilers", "Panthers", "Kings", "Wild", "Canadiens",
        "Predators", "Devils", "Islanders", "Rangers", "Senators", "Flyers", "Penguins", "Sharks",
        "Kraken", "Blues", "Lightning", "Maple Leafs", "Canucks", "Golden Knights", "Capitals", "Jets"
    ]
    positions = ["G", "D", "LW", "RW", "C"]
    
    dvp = {}
    for team in teams:
        dvp[team] = {}
        for pos in positions:
            seed = sum(ord(c) for c in team) + sum(ord(c) for c in pos)
            random.seed(seed)
            dvp[team][pos] = random.randint(1, 32)
            
    random.seed()
    return dvp

# Cache the dataset
NBA_DVP = _get_nba_dvp()
NFL_DVP = _get_nfl_dvp()
MLB_DVP = _get_mlb_dvp()
NHL_DVP = _get_nhl_dvp()

def get_dvp_rating(sport: str, opponent: str, position: str) -> Dict[str, Any]:
    """
    Returns the DvP rank and categorical rating.
    Lower rank = More favorable (Green) for offensive player (defense is weak)
    Higher rank = Tougher (Red) for offensive player (defense is strong)
    """
    sport = sport.upper().split("_")[-1]
    opponent = opponent.title()
    position = position.upper()
    
    # Determine which dataset to use
    if sport == "NBA":
        lookup_ds = NBA_DVP
        max_teams = 30
    elif sport == "NFL":
        lookup_ds = NFL_DVP
        max_teams = 32
    elif sport == "MLB":
        lookup_ds = MLB_DVP
        max_teams = 30
    elif sport == "NHL":
        lookup_ds = NHL_DVP
        max_teams = 32
    else:
        lookup_ds = {}
        max_teams = 30
    
    matched_team = None
    if lookup_ds:
        for team in lookup_ds.keys():
            if team.lower() in opponent.lower():
                matched_team = team
                break
                
    if not matched_team or position not in (lookup_ds.get(matched_team, {})):
        return {
            "rank": max_teams // 2,
            "total_teams": max_teams,
            "rating": "Neutral",
            "color": "yellow",
            "opponent": opponent,
            "position": position,
            "sport": sport
        }
        
    rank = lookup_ds[matched_team][position]
    
    # Common boundaries for 30/32 team leagues:
    # 1-10: Favorable (Green)
    # 11-20/22: Neutral (Yellow)
    # 21/23+: Tough (Red)
    if rank <= 10:
        rating = "Favorable"
        color = "green"
    elif rank > (max_teams - 10):
        rating = "Tough"
        color = "red"
    else:
        rating = "Neutral"
        color = "yellow"
        
    return {
        "rank": rank,
        "total_teams": max_teams,
        "rating": rating,
        "color": color,
        "opponent": matched_team,
        "position": position,
        "sport": sport,
        "description": f"{matched_team} rank #{rank}/{max_teams} against {position}s"
    }


