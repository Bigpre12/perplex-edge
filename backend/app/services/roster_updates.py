"""
2026 NBA Roster Updates - Major Trades and Lineup Changes

This file tracks the significant roster moves that occurred in the 2026 season,
particularly around the trade deadline that reshaped several teams.

Major Trades Summary:
1. Lakers acquire Luka Doncic from Mavericks
2. Wizards acquire Anthony Davis from Lakers  
3. Suns acquire Jalen Green from Rockets
4. Wizards acquire Cade Cunningham from Pistons
5. Lakers acquire Deandre Ayton from Suns

These moves significantly impact prop lines and team dynamics.
"""

# 2026 NBA Roster Updates - Post Trade Deadline
NBA_ROSTER_UPDATES_2026 = {
    "Washington Wizards": {
        "acquisitions": [
            {
                "player": "Anthony Davis",
                "from": "Los Angeles Lakers",
                "position": "C",
                "prop_impact": {
                    "pts": 26.5,
                    "reb": 12.5,
                    "ast": 3.5,
                    "blk": 2.5,
                    "pra": 42.5
                },
                "usage_increase": 0.15,  # 15% higher usage than with Lakers
                "team_impact": "Superstar centerpiece, transforms Wizards into playoff contender"
            },
            {
                "player": "Cade Cunningham", 
                "from": "Detroit Pistons",
                "position": "PG",
                "prop_impact": {
                    "pts": 22.5,
                    "reb": 5.5,
                    "ast": 7.5,
                    "pra": 35.5
                },
                "usage_increase": 0.20,  # 20% higher usage as primary ballhandler
                "team_impact": "Elite playmaker, takes over primary PG duties"
            }
        ],
        "departures": [
            {
                "player": "Kyle Kuzma",
                "to": "Sacramento Kings",
                "impact": "Veteran scoring lost"
            },
            {
                "player": "Jordan Poole", 
                "to": "Free Agency",
                "impact": "Bench scoring lost"
            }
        ],
        "new_starting_five": [
            "Anthony Davis (C)",
            "Cade Cunningham (PG)", 
            "Kobe Bufkin (SG)",
            "Bilal Coulibaly (SF)",
            "Alex Sarr (PF)"
        ],
        "team_rating_change": "+25",  # Significant improvement
        "playoff_odds": "85%"  # Now playoff contenders
    },
    
    "Los Angeles Lakers": {
        "acquisitions": [
            {
                "player": "Luka Doncic",
                "from": "Dallas Mavericks", 
                "position": "PG",
                "prop_impact": {
                    "pts": 33.5,
                    "reb": 9.5,
                    "ast": 9.5,
                    "pra": 52.5
                },
                "usage_increase": 0.05,  # Slight increase, sharing with LeBron
                "team_impact": "Generational talent, forms new superstar duo with LeBron"
            },
            {
                "player": "Deandre Ayton",
                "from": "Phoenix Suns",
                "position": "C", 
                "prop_impact": {
                    "pts": 18.5,
                    "reb": 12.5,
                    "ast": 2.5,
                    "blk": 1.5
                },
                "usage_increase": 0.10,  # Increased role as starting center
                "team_impact": "Elite rim protector, solves interior defense issues"
            }
        ],
        "departures": [
            {
                "player": "Anthony Davis",
                "to": "Washington Wizards", 
                "impact": "Superstar center lost, major blow"
            },
            {
                "player": "D'Angelo Russell",
                "to": "Free Agency",
                "impact": "Starting PG lost"
            }
        ],
        "new_starting_five": [
            "Luka Doncic (PG)",
            "LeBron James (SF)",
            "Deandre Ayton (C)",
            "Austin Reaves (SG)",
            "Rui Hachimura (PF)"
        ],
        "team_rating_change": "+5",  # Slight improvement despite AD loss
        "championship_odds": "40%"  # Still contenders with Luka-LeBron duo
    },
    
    "Phoenix Suns": {
        "acquisitions": [
            {
                "player": "Jalen Green",
                "from": "Houston Rockets",
                "position": "SG",
                "prop_impact": {
                    "pts": 24.5,
                    "reb": 5.5,
                    "ast": 4.5,
                    "3pm": 3.5
                },
                "usage_increase": 0.12,  # Increased role as secondary scorer
                "team_impact": "Elite scorer, provides youth and athleticism"
            }
        ],
        "departures": [
            {
                "player": "Deandre Ayton",
                "to": "Los Angeles Lakers",
                "impact": "Starting center lost"
            },
            {
                "player": "Bradley Beal",
                "to": "Buyout",
                "impact": "Veteran scoring lost"
            }
        ],
        "new_starting_five": [
            "Devin Booker (SG)",
            "Kevin Durant (SF)",
            "Jalen Green (SG)",
            "Royce O'Neale (SF)",
            "Jusuf Nurkic (C)"
        ],
        "team_rating_change": "+8",  # Good improvement with Green
        "playoff_odds": "75%"
    },
    
    "Dallas Mavericks": {
        "departures": [
            {
                "player": "Luka Doncic",
                "to": "Los Angeles Lakers",
                "impact": "Franchise player lost, devastating blow"
            }
        ],
        "remaining_core": [
            "Kyrie Irving (PG)",
            "PJ Washington (PF)",
            "Dereck Lively II (C)"
        ],
        "team_rating_change": "-30",  # Major decline
        "playoff_odds": "25%"  # Long shot without Luka
    },
    
    "Houston Rockets": {
        "departures": [
            {
                "player": "Jalen Green",
                "to": "Phoenix Suns", 
                "impact": "Star scorer lost"
            }
        ],
        "new_focus": [
            "Alperen Sengun (C) - Now primary option",
            "Fred VanVleet (PG) - Veteran leader",
            "Jabari Smith Jr. (PF) - Increased role"
        ],
        "team_rating_change": "-15",  # Significant decline
        "playoff_odds": "40%"
    },
    
    "Detroit Pistons": {
        "departures": [
            {
                "player": "Cade Cunningham",
                "to": "Washington Wizards",
                "impact": "Franchise PG lost"
            }
        ],
        "rebuilding_core": [
            "Jaden Ivey (SG)",
            "Jalen Duren (C)",
            "Ausar Thompson (SF)"
        ],
        "team_rating_change": "-20",  # Major decline
        "playoff_odds": "5%"  # Full rebuild mode
    }
}

# Prop Line Adjustments Based on Trades
PROP_LINE_ADJUSTMENTS = {
    # Wizards players get boost with new roles
    "Anthony Davis": {
        "rebounds": "+2.5",  # More opportunities as #1 option
        "blocks": "+0.5",
        "points": "+3.0"
    },
    "Cade Cunningham": {
        "assists": "+2.0",  # Primary ballhandler
        "points": "+3.0",
        "rebounds": "+1.0"
    },
    
    # Lakers players adjust to new roles
    "Luka Doncic": {
        "assists": "-1.0",  # Sharing with LeBron
        "rebounds": "+1.0",  # More rebounds without AD
        "points": "+2.0"
    },
    "LeBron James": {
        "assists": "+1.0",  # More playmaking with Luka
        "points": "-2.0"   # Less scoring responsibility
    },
    
    # Suns players adjust to Green's presence
    "Jalen Green": {
        "points": "+2.0",  # Increased role
        "rebounds": "+1.0"
    },
    "Devin Booker": {
        "points": "-2.0",  # Less shots with Green
        "assists": "+1.0"
    },
    
    # Players on teams that lost stars
    "Kyrie Irving": {
        "points": "+5.0",  # Now #1 option
        "assists": "+3.0",
        "usage": "+25%"
    },
    "Alperen Sengun": {
        "points": "+4.0",  # Now primary option
        "rebounds": "+2.0",
        "assists": "+1.0"
    }
}

# Injury Impact Multipliers
INJURY_IMPACT_MULTIPLIERS = {
    "star_player": 2.0,      # Star players have 2x impact
    "starter": 1.5,           # Starters have 1.5x impact  
    "bench_player": 1.0,      # Bench players have normal impact
    "role_player": 0.8        # Role players have reduced impact
}

# Player Categories for Impact Calculation
PLAYER_CATEGORIES = {
    # Superstar tier
    "Anthony Davis": "star_player",
    "Luka Doncic": "star_player", 
    "LeBron James": "star_player",
    "Kevin Durant": "star_player",
    
    # Starter tier
    "Cade Cunningham": "starter",
    "Jalen Green": "starter",
    "Devin Booker": "starter",
    "Kyrie Irving": "starter",
    "Alperen Sengun": "starter",
    
    # Role player tier
    "Kobe Bufkin": "role_player",
    "Bilal Coulibaly": "role_player",
    "Alex Sarr": "role_player",
    "Austin Reaves": "role_player"
}

def get_prop_adjustment(player_name: str, stat_type: str) -> float:
    """Get prop line adjustment for a player based on trades."""
    adjustments = PROP_LINE_ADJUSTMENTS.get(player_name, {})
    
    if stat_type in adjustments:
        # Parse adjustment like "+2.5" or "-1.0"
        adj_str = adjustments[stat_type]
        try:
            return float(adj_str)
        except ValueError:
            return 0.0
    
    return 0.0

def get_injury_impact(player_name: str, base_impact: float) -> float:
    """Calculate injury impact based on player category."""
    category = PLAYER_CATEGORIES.get(player_name, "role_player")
    multiplier = INJURY_IMPACT_MULTIPLIERS.get(category, 1.0)
    
    return base_impact * multiplier

def get_team_rating_change(team_name: str) -> int:
    """Get team rating change from trades."""
    team_data = NBA_ROSTER_UPDATES_2026.get(team_name)
    if team_data:
        return int(team_data.get("team_rating_change", 0))
    return 0

def get_new_starting_five(team_name: str) -> list:
    """Get new starting five for a team after trades."""
    team_data = NBA_ROSTER_UPDATES_2026.get(team_name)
    if team_data:
        return team_data.get("new_starting_five", [])
    return []

# Export for use in other modules
__all__ = [
    'NBA_ROSTER_UPDATES_2026',
    'PROP_LINE_ADJUSTMENTS', 
    'INJURY_IMPACT_MULTIPLIERS',
    'PLAYER_CATEGORIES',
    'get_prop_adjustment',
    'get_injury_impact',
    'get_team_rating_change',
    'get_new_starting_five'
]
