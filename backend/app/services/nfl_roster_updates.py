"""
2026 NFL Roster Updates - Major Trades and Lineup Changes

This file tracks significant roster moves in the 2026 NFL season,
particularly around the trade deadline and free agency that impact prop lines.

Major Trades Summary:
1. Chiefs acquire WR from Raiders for draft picks
2. Patriots get new QB1 from Bears
3. Cowboys add veteran pass rusher

These moves significantly impact prop lines and team dynamics.
"""

# 2026 NFL Roster Updates - Post Trade Deadline
NFL_ROSTER_UPDATES_2026 = {
    "Kansas City Chiefs": {
        "acquisitions": [
            {
                "player": "Davante Adams",
                "from": "Las Vegas Raiders",
                "position": "WR",
                "prop_impact": {
                    "receiving_yards": "+85.0",
                    "receptions": "+5.0",
                    "touchdowns": "+1.0"
                },
                "usage_increase": 0.20,  # 20% higher target share
                "team_impact": "Elite #1 WR, transforms Chiefs offense"
            }
        ],
        "departures": [
            {
                "player": "Kadarius Toney",
                "to": "Free Agency",
                "impact": "Slot receiver depth lost"
            }
        ],
        "new_starting_five": [
            "Patrick Mahomes (QB)",
            "Davante Adams (WR)",
            "Travis Kelce (TE)",
            "Rashee Rice (WR)",
            "Isiah Pacheco (RB)"
        ],
        "team_rating_change": "+15",  # Significant improvement
        "playoff_odds": "95%"  # Super Bowl favorites
    },
    
    "New England Patriots": {
        "acquisitions": [
            {
                "player": "Justin Fields",
                "from": "Chicago Bears",
                "position": "QB",
                "prop_impact": {
                    "passing_yards": "+150.0",
                    "rushing_yards": "+45.0",
                    "touchdowns": "+1.5"
                },
                "usage_increase": 0.25,  # 25% higher usage as new QB1
                "team_impact": "Franchise QB, transforms offense"
            }
        ],
        "departures": [
            {
                "player": "Mac Jones",
                "to": "Free Agency",
                "impact": "Backup QB lost"
            }
        ],
        "new_starting_offense": [
            "Justin Fields (QB)",
            "Rhamondre Stevenson (RB)",
            "Kendrick Bourne (WR)",
            "DeVante Parker (WR)",
            "Hunter Henry (TE)"
        ],
        "team_rating_change": "+12",  # Major improvement
        "playoff_odds": "75%"  # Playoff contenders
    },
    
    "Dallas Cowboys": {
        "acquisitions": [
            {
                "player": "Myles Garrett",
                "from": "Cleveland Browns",
                "position": "DE",
                "prop_impact": {
                    "sacks": "+8.0",
                    "tackles": "+15.0",
                    "forced_fumbles": "+2.0"
                },
                "usage_increase": 0.15,  # 15% more snaps
                "team_impact": "Elite pass rusher, transforms defense"
            }
        ],
        "departures": [
            {
                "player": "Dorance Armstrong",
                "to": "Free Agency",
                "impact": "Edge depth lost"
            }
        ],
        "team_rating_change": "+10",  # Significant improvement
        "playoff_odds": "85%"  # Super Bowl contenders
    }
}

# Prop Line Adjustments Based on Trades
NFL_PROP_LINE_ADJUSTMENTS = {
    # Chiefs players get boost with new WR
    "Patrick Mahomes": {
        "passing_yards": "+200.0",  # Elite target to throw to
        "touchdowns": "+4.0",
        "completion_pct": "+3.0%"
    },
    "Davante Adams": {
        "receiving_yards": "+100.0",  # Mahomes connection
        "receptions": "+6.0",
        "touchdowns": "+2.0"
    },
    "Travis Kelce": {
        "receiving_yards": "+50.0",  # Less double coverage
        "receptions": "+3.0"
    },
    
    # Patriots players with new QB
    "Justin Fields": {
        "passing_yards": "+180.0",  # New system boost
        "rushing_yards": "+60.0",
        "total_touchdowns": "+2.0"
    },
    "Rhamondre Stevenson": {
        "rushing_yards": "+80.0",  # QB run threat opens lanes
        "receptions": "+10.0"
    },
    
    # Cowboys players with elite pass rusher
    "Micah Parsons": {
        "sacks": "+5.0",  # Garrett draws double teams
        "tackles": "+10.0"
    },
    "Myles Garrett": {
        "sacks": "+10.0",  # Cowboys system boost
        "tackles": "+20.0",
        "forced_fumbles": "+3.0"
    }
}

# Injury Impact Multipliers
NFL_INJURY_IMPACT_MULTIPLIERS = {
    "star_player": 2.5,      # QBs have massive impact
    "starter": 1.8,           # Starters have high impact  
    "bench_player": 1.0,      # Bench players have normal impact
    "role_player": 0.8        # Role players have reduced impact
}

# Player Categories for Impact Calculation
NFL_PLAYER_CATEGORIES = {
    # Superstar tier
    "Patrick Mahomes": "star_player",
    "Justin Fields": "star_player",
    "Davante Adams": "star_player",
    "Myles Garrett": "star_player",
    
    # Starter tier
    "Travis Kelce": "starter",
    "Rhamondre Stevenson": "starter",
    "Micah Parsons": "starter",
    "Rashee Rice": "starter",
    
    # Role player tier
    "Kadarius Toney": "role_player",
    "Hunter Henry": "role_player",
    "DeVante Parker": "role_player"
}
