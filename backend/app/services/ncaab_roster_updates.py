"""
2026 NCAAB Roster Updates - Major Transfers and Portal Activity

This file tracks significant roster moves in the 2026 NCAAB season,
particularly around transfer portal and NBA draft decisions that impact prop lines.

Major Transfers Summary:
1. Duke gets elite transfer from Kentucky
2. Kansas adds graduate transfer guard
3. UNC lands 5-star freshman

These moves significantly impact prop lines and team dynamics.
"""

# 2026 NCAAB Roster Updates - Post Transfer Portal
NCAAB_ROSTER_UPDATES_2026 = {
    "Duke Blue Devils": {
        "acquisitions": [
            {
                "player": "DJ Wagner",
                "from": "Kentucky Wildcats (Transfer)",
                "position": "SG",
                "prop_impact": {
                    "points": "+18.0",
                    "assists": "+4.0",
                    "rebounds": "+3.0"
                },
                "usage_increase": 0.25,  # 25% usage as transfer
                "team_impact": "Elite scoring guard, transforms offense"
            }
        ],
        "departures": [
            {
                "player": "Jared McCain",
                "to": "NBA Draft",
                "impact": "Starting guard lost to draft"
            }
        ],
        "new_starting_five": [
            "Caleb Foster (PG)",
            "DJ Wagner (SG)",
            "Dame Sarr (SF)",
            "Cameron Boozer (PF)",
            "Patrick Ngongba (C)"
        ],
        "team_rating_change": "+12",  # Significant improvement
        "march_madness_odds": "90%"  # #1 seed contender
    },
    
    "Kansas Jayhawks": {
        "acquisitions": [
            {
                "player": "Jamison Battle",
                "from": "Ohio State Buckeyes (Grad Transfer)",
                "position": "SF",
                "prop_impact": {
                    "points": "+15.0",
                    "rebounds": "+6.0",
                    "3pm": "+2.5"
                },
                "usage_increase": 0.20,  # 20% usage as grad transfer
                "team_impact": "Experienced scorer, veteran leadership"
            }
        ],
        "departures": [
            {
                "player": "Kevin McCullar",
                "to": "NBA Draft",
                "impact": "Starting forward lost to draft"
            }
        ],
        "team_rating_change": "+8",  # Moderate improvement
        "march_madness_odds": "85%"  # High seed contender
    },
    
    "North Carolina Tar Heels": {
        "acquisitions": [
            {
                "player": "Cooper Flagg",
                "from": "High School (5-Star Freshman)",
                "position": "SF",
                "prop_impact": {
                    "points": "+16.0",
                    "rebounds": "+8.0",
                    "blocks": "+2.5"
                },
                "usage_increase": 0.30,  # 30% usage as 5-star freshman
                "team_impact": "Elite freshman, one-and-done potential"
            }
        ],
        "departures": [
            {
                "player": "Armando Bacot",
                "to": "Graduation",
                "impact": "All-time great center lost"
            }
        ],
        "team_rating_change": "+10",  # Significant improvement
        "march_madness_odds": "80%"  # High seed contender
    }
}

# Prop Line Adjustments Based on Transfers
NCAAB_PROP_LINE_ADJUSTMENTS = {
    # Duke players with new transfer
    "Caleb Foster": {
        "assists": "+3.0",  # Elite scorer to pass to
        "points": "+12.0",
        "3pm": "+1.5"
    },
    "DJ Wagner": {
        "points": "+20.0",  # Duke system boost
        "assists": "+5.0",
        "rebounds": "+4.0"
    },
    "Cameron Boozer": {
        "rebounds": "+8.0",  # Less defensive attention
        "points": "+15.0",
        "blocks": "+1.5"
    },
    
    # Kansas players with grad transfer
    "Jamison Battle": {
        "points": "+18.0",  # Kansas system boost
        "rebounds": "+7.0",
        "3pm": "+3.0"
    },
    "Darryn Peterson": {
        "assists": "+4.0",  # Veteran scorer helps
        "points": "+14.0"
    },
    
    # UNC players with elite freshman
    "Cooper Flagg": {
        "points": "+18.0",  # UNC system boost
        "rebounds": "+9.0",
        "blocks": "+3.0"
    },
    "RJ Davis": {
        "assists": "+5.0",  # Elite freshman to pass to
        "points": "+16.0"
    }
}

# Injury Impact Multipliers
NCAAB_INJURY_IMPACT_MULTIPLIERS = {
    "star_player": 2.0,      # Stars have high impact
    "starter": 1.5,           # Starters have moderate impact  
    "bench_player": 1.0,      # Bench players have normal impact
    "role_player": 0.8        # Role players have reduced impact
}

# Player Categories for Impact Calculation
NCAAB_PLAYER_CATEGORIES = {
    # Superstar tier
    "DJ Wagner": "star_player",
    "Cooper Flagg": "star_player",
    "Jamison Battle": "star_player",
    "Caleb Foster": "star_player",
    
    # Starter tier
    "Dame Sarr": "starter",
    "Cameron Boozer": "starter",
    "Patrick Ngongba": "starter",
    "RJ Davis": "starter",
    "Darryn Peterson": "starter",
    
    # Role player tier
    "Jared McCain": "role_player",
    "Kevin McCullar": "role_player",
    "Armando Bacot": "role_player"
}
