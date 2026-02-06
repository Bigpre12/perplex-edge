"""
2026 NHL Roster Updates - Major Trades and Lineup Changes

This file tracks significant roster moves in the 2026 NHL season,
particularly around the trade deadline and injury updates that impact prop lines.

Major Changes Summary:
1. Multiple injuries across the league affecting key players
2. Power play unit changes due to injuries
3. Goalie rotations and injuries

These moves significantly impact prop lines and team dynamics.
"""

# 2026 NHL Roster Updates - Current Slate 2/6/26
NHL_ROSTER_UPDATES_2026 = {
    "Pittsburgh Penguins": {
        "injuries": [
            {
                "player": "Noel Acciari",
                "position": "C",
                "status": "OUT",
                "impact": "Depth center lost"
            },
            {
                "player": "P. Kettles",
                "position": "D",
                "status": "OUT",
                "impact": "Defense depth lost"
            },
            {
                "player": "B. Lizotte",
                "position": "LW",
                "status": "OUT",
                "impact": "Forward depth lost"
            },
            {
                "player": "R. Rakell",
                "position": "C",
                "status": "OUT",
                "impact": "Top 6 forward lost"
            }
        ],
        "power_play_changes": [
            "PP1: S. Crosby - C, Y. Chinakhov - LW, E. Malkin - RW, Bryan Rust - LD, E. Karlsson - RD",
            "PP2: Ben Kindel - C, R. McGroarty - LW, J. Brazeau - RW, A. Mantha - LD, Ryan Shea - RD"
        ],
        "team_rating_change": "-8",  # Multiple injuries
        "playoff_odds": "60%"  # Injured roster
    },
    
    "Buffalo Sabres": {
        "injuries": [
            {
                "player": "Zach Benson",
                "position": "LW",
                "status": "OUT",
                "impact": "Top 9 forward lost"
            },
            {
                "player": "J. Greenway",
                "position": "LW",
                "status": "OUT",
                "impact": "Forward depth lost"
            },
            {
                "player": "J. Danforth",
                "position": "RW",
                "status": "IR",
                "impact": "Depth forward lost"
            },
            {
                "player": "Josh Dunne",
                "position": "C",
                "status": "IR",
                "impact": "Depth center lost"
            },
            {
                "player": "Jiri Kulich",
                "position": "C",
                "status": "IR",
                "impact": "Prospect depth lost"
            },
            {
                "player": "U. Luukkonen",
                "position": "G",
                "status": "IR",
                "impact": "Goalie depth lost"
            },
            {
                "player": "Josh Norris",
                "position": "C",
                "status": "IR",
                "impact": "Top 6 center lost"
            },
            {
                "player": "C. Timmins",
                "position": "D",
                "status": "IR",
                "impact": "Defense depth lost"
            }
        ],
        "power_play_changes": [
            "PP1: T. Thompson - C, Jason Zucker - LW, Jack Quinn - RW, Josh Doan - LD, R. Dahlin - RD",
            "PP2: Noah Ostlund - C, Alex Tuch - RW, Bowen Byram - LD, Ryan McLeod - RD"
        ],
        "team_rating_change": "-10",  # Significant injury impact
        "playoff_odds": "55%"  # Heavily injured
    },
    
    "New York Islanders": {
        "injuries": [
            {
                "player": "P. Engvall",
                "position": "LW",
                "status": "IR-LT",
                "impact": "Forward depth lost"
            },
            {
                "player": "K. Palmieri",
                "position": "RW",
                "status": "IR",
                "impact": "Top 6 forward lost"
            },
            {
                "player": "A. Romanov",
                "position": "D",
                "status": "IR",
                "impact": "Top 4 defenseman lost"
            },
            {
                "player": "S. Varlamov",
                "position": "G",
                "status": "IR",
                "impact": "Backup goalie lost"
            }
        ],
        "power_play_changes": [
            "PP1: Bo Horvat - C, M. Barzal - LW, C. Ritchie - RW, M. Schaefer - LD, S. Holmstrom - RD",
            "PP2: J. Drouin - C, Ondrej Palat - LW, Anders Lee - RW, E. Heineman - LD, T. DeAngelo - RD"
        ],
        "team_rating_change": "-6",  # Moderate injury impact
        "playoff_odds": "70%"  # Still competitive
    },
    
    "New Jersey Devils": {
        "injuries": [
            {
                "player": "Jack Hughes",
                "position": "C",
                "status": "OUT",
                "impact": "Star center lost"
            },
            {
                "player": "Luke Hughes",
                "position": "D",
                "status": "IR-LT",
                "impact": "Top 4 defenseman lost"
            },
            {
                "player": "Zack MacEwen",
                "position": "C",
                "status": "IR-LT",
                "impact": "Depth forward lost"
            },
            {
                "player": "M. McLaughlin",
                "position": "C",
                "status": "IR-LT",
                "impact": "Depth center lost"
            },
            {
                "player": "S. Noesen",
                "position": "RW",
                "status": "IR-LT",
                "impact": "Depth forward lost"
            }
        ],
        "power_play_changes": [
            "PP1: N. Hischier - C, Jesper Bratt - LW, D. Mercer - RW, Timo Meier - LD, D. Hamilton - RD",
            "PP2: Connor Brown - C, A. Gritsyuk - LW, E. Dadonov - RW, M. Tsyplakov - LD, Simon Nemec - RD"
        ],
        "team_rating_change": "-12",  # Major star injury
        "playoff_odds": "45%"  # Hughes injury hurts significantly
    },
    
    "Carolina Hurricanes": {
        "injuries": [
            {
                "player": "E. Robinson",
                "position": "LW",
                "status": "OUT",
                "impact": "Forward depth lost"
            },
            {
                "player": "P. Kochetkov",
                "position": "G",
                "status": "IR",
                "impact": "Backup goalie lost"
            }
        ],
        "power_play_changes": [
            "PP1: S. Aho - C, A. Svechnikov - LW, Seth Jarvis - RW, S. Gostisbehere - LD, N. Ehlers - RD",
            "PP2: L. Stankoven - C, Taylor Hall - LW, J. Blake - RW, M. Jankowski - LD, A. Nikishin - RD"
        ],
        "team_rating_change": "-3",  # Minor injury impact
        "playoff_odds": "85%"  # Still strong contender
    },
    
    "New York Rangers": {
        "injuries": [
            {
                "player": "Adam Edstrom",
                "position": "C",
                "status": "IR-LT",
                "impact": "Depth center lost"
            },
            {
                "player": "Adam Fox",
                "position": "D",
                "status": "IR-LT",
                "impact": "Star defenseman lost"
            },
            {
                "player": "Conor Sheary",
                "position": "LW",
                "status": "IR-LT",
                "impact": "Forward depth lost"
            },
            {
                "player": "I. Shesterkin",
                "position": "G",
                "status": "IR",
                "impact": "Star goalie lost"
            }
        ],
        "power_play_changes": [
            "PP1: V. Trocheck - C, J.T. Miller - LW, A. Lafreniere - RW, V. Gavrikov - LD, M. Zibanejad - RD",
            "PP2: Will Cuylle - C, J. Brodzinski - LW, G. Perreault - RW, B. Schneider - LD, T. Raddysh - RD"
        ],
        "team_rating_change": "-15",  # Major star injuries
        "playoff_odds": "40%"  # Fox and Shesterkin injuries hurt badly
    },
    
    "Ottawa Senators": {
        "injuries": [
            {
                "player": "L. Ullmark",
                "position": "G",
                "status": "OUT",
                "impact": "Starting goalie lost"
            },
            {
                "player": "David Perron",
                "position": "RW",
                "status": "IR",
                "impact": "Veteran forward lost"
            }
        ],
        "power_play_changes": [
            "PP1: Tim Stutzle - C, B. Tkachuk - LW, D. Batherson - RW, J. Sanderson - LD, Dylan Cozens - RD",
            "PP2: Shane Pinto - C, S. Halliday - LW, C. Giroux - RW, T. Chabot - LD, J. Spence - RD"
        ],
        "team_rating_change": "-5",  # Goalie injury hurts
        "playoff_odds": "65%"  # Still competitive
    },
    
    "Philadelphia Flyers": {
        "injuries": [
            {
                "player": "S. Ersson",
                "position": "G",
                "status": "OUT",
                "impact": "Starting goalie lost"
            },
            {
                "player": "Ty Murchison",
                "position": "D",
                "status": "OUT",
                "impact": "Defense depth lost"
            },
            {
                "player": "R. Abols",
                "position": "C",
                "status": "IR",
                "impact": "Depth forward lost"
            },
            {
                "player": "T. Foerster",
                "position": "RW",
                "status": "IR",
                "impact": "Top 9 forward lost"
            }
        ],
        "power_play_changes": [
            "PP1: C. Dvorak - C, Bobby Brink - LW, T. Konecny - RW, T. Zegras - LD, J. Drysdale - RD",
            "PP2: Noah Cates - C, M. Michkov - LW, Owen Tippett - RW, Cam York - LD, D. Barkey - RD"
        ],
        "team_rating_change": "-7",  # Goalie injury significant
        "playoff_odds": "50%"  # Goalie situation hurts
    },
    
    "Nashville Predators": {
        "injuries": [
            {
                "player": "None",
                "position": "N/A",
                "status": "N/A",
                "impact": "No major injuries"
            }
        ],
        "power_play_changes": [
            "PP1: R. O'Reilly - C, S. Stamkos - LW, J. Marchessault - RW, F. Forsberg - LD, Roman Josi - RD",
            "PP2: Erik Haula - C, M. Bunting - LW, L. Evangelista - RW, N. Hague - LD, Nick Perbix - RD"
        ],
        "team_rating_change": "+2",  # Healthy roster
        "playoff_odds": "75%"  # Good position
    },
    
    "Washington Capitals": {
        "injuries": [
            {
                "player": "John Carlson",
                "position": "D",
                "status": "DTD",
                "impact": "Top 4 defenseman questionable"
            },
            {
                "player": "E. Mateiko",
                "position": "LW",
                "status": "OUT",
                "impact": "Forward depth lost"
            },
            {
                "player": "Sonny Milano",
                "position": "LW",
                "status": "OUT",
                "impact": "Forward depth lost"
            },
            {
                "player": "C. Lindgren",
                "position": "G",
                "status": "IR",
                "impact": "Backup goalie lost"
            },
            {
                "player": "C. McMichael",
                "position": "C",
                "status": "IR",
                "impact": "Depth center lost"
            }
        ],
        "power_play_changes": [
            "PP1: Dylan Strome - C, A. Ovechkin - LW, Ryan Leonard - RW, J. Chychrun - LD, Tom Wilson - RD",
            "PP2: J. Sourdif - C, Ethen Frank - LW, A. Beauvillier - RW, P. Dubois - LD, John Carlson DTD - RD"
        ],
        "team_rating_change": "-4",  # Carlson DTD hurts
        "playoff_odds": "68%"  # Still in good position
    },
    
    "Florida Panthers": {
        "injuries": [
            {
                "player": "D. Tarasov",
                "position": "G",
                "status": "DTD",
                "impact": "Backup goalie questionable"
            },
            {
                "player": "Aaron Ekblad",
                "position": "D",
                "status": "OUT",
                "impact": "Top 4 defenseman lost"
            },
            {
                "player": "B. Marchand",
                "position": "LW",
                "status": "OUT",
                "impact": "Star forward lost"
            },
            {
                "player": "E. Rodrigues",
                "position": "C",
                "status": "OUT",
                "impact": "Depth center lost"
            },
            {
                "player": "A. Barkov",
                "position": "C",
                "status": "IR-LT",
                "impact": "Star captain lost"
            },
            {
                "player": "T. Bjornfot",
                "position": "D",
                "status": "IR",
                "impact": "Defense depth lost"
            },
            {
                "player": "Seth Jones",
                "position": "D",
                "status": "IR-LT",
                "impact": "Top defenseman lost"
            },
            {
                "player": "D. Kulikov",
                "position": "D",
                "status": "IR-LT",
                "impact": "Defense depth lost"
            },
            {
                "player": "Tomas Nosek",
                "position": "LW",
                "status": "IR-NR",
                "impact": "Depth forward lost"
            }
        ],
        "power_play_changes": [
            "PP1: Sam Bennett - C, Sam Reinhart - LW, M. Tkachuk - RW, A. Lundell - LD, U. Balinskis - RD",
            "PP2: M. Samoskevich - C, C. Verhaeghe - LW, A.J. Greer - RW, G. Forsling - LD, E. Luostarinen - RD"
        ],
        "team_rating_change": "-18",  # Massive injury impact
        "playoff_odds": "35%"  # Barkov injury devastating
    },
    
    "Tampa Bay Lightning": {
        "injuries": [
            {
                "player": "A. Cirelli",
                "position": "C",
                "status": "OUT",
                "impact": "Top 6 center lost"
            },
            {
                "player": "Nick Paul",
                "position": "RW",
                "status": "OUT",
                "impact": "Forward depth lost"
            },
            {
                "player": "C. D'Astous",
                "position": "D",
                "status": "IR",
                "impact": "Defense depth lost"
            },
            {
                "player": "E. Lilleberg",
                "position": "D",
                "status": "IR",
                "impact": "Defense depth lost"
            },
            {
                "player": "B. Point",
                "position": "C",
                "status": "IR-LT",
                "impact": "Star center lost"
            }
        ],
        "power_play_changes": [
            "PP1: J. Guentzel - C, B. Hagel - LW, N. Kucherov - RW, O. Bjorkstrand - LD, D. Raddysh - RD",
            "PP2: Yanni Gourde - C, D. James - LW, G. Goncalves - RW, V. Hedman - LD, J.J. Moser - RD"
        ],
        "team_rating_change": "-10",  # Point injury hurts
        "playoff_odds": "55%"  # Still dangerous but hurt
    },
    
    "Los Angeles Kings": {
        "injuries": [
            {
                "player": "A. Kuzmenko",
                "position": "LW",
                "status": "DTD",
                "impact": "Forward questionable"
            },
            {
                "player": "A. Panarin",
                "position": "LW",
                "status": "OUT",
                "impact": "Star forward lost"
            },
            {
                "player": "M. Anderson",
                "position": "D",
                "status": "IR",
                "impact": "Defense depth lost"
            },
            {
                "player": "A. Turcotte",
                "position": "C",
                "status": "IR",
                "impact": "Depth center lost"
            }
        ],
        "power_play_changes": [
            "PP1: A. Kuzmenko DTD - C, Corey Perry - LW, Adrian Kempe - RW, Kevin Fiala - LD, B. Clarke - RD",
            "PP2: Anze Kopitar - C, Q. Byfield - LW, Taylor Ward - RW, A. Laferriere - LD, Drew Doughty - RD"
        ],
        "team_rating_change": "-8",  # Panarin injury hurts
        "playoff_odds": "60%"  # Still competitive
    },
    
    "Vegas Golden Knights": {
        "injuries": [
            {
                "player": "C. Sissons",
                "position": "RW",
                "status": "OUT",
                "impact": "Forward depth lost"
            },
            {
                "player": "Carter Hart",
                "position": "G",
                "status": "IR",
                "impact": "Backup goalie lost"
            },
            {
                "player": "Brett Howden",
                "position": "C",
                "status": "IR",
                "impact": "Depth center lost"
            },
            {
                "player": "W. Karlsson",
                "position": "C",
                "status": "IR-LT",
                "impact": "Depth center lost"
            },
            {
                "player": "B. McNabb",
                "position": "D",
                "status": "IR",
                "impact": "Defense depth lost"
            },
            {
                "player": "A. Pietrangelo",
                "position": "D",
                "status": "IR-LT",
                "impact": "Star defenseman lost"
            },
            {
                "player": "J. Rondbjerg",
                "position": "RW",
                "status": "IR",
                "impact": "Forward depth lost"
            },
            {
                "player": "Brandon Saad",
                "position": "LW",
                "status": "IR",
                "impact": "Veteran forward lost"
            }
        ],
        "power_play_changes": [
            "PP1: Jack Eichel - C, P. Dorofeyev - LW, Mark Stone - RW, Mitch Marner - LD, Tomas Hertl - RD",
            "PP2: Kai Uchacz - C, C. Reinhardt - LW, B. Bowman - RW, Noah Hanifin - LD, R. Andersson - RD"
        ],
        "team_rating_change": "-12",  # Pietrangelo injury hurts
        "playoff_odds": "65%"  # Still strong but hurt
    }
}

# Prop Line Adjustments Based on Injuries and Roster Changes
NHL_PROP_LINE_ADJUSTMENTS = {
    # Penguins - injuries reduce production
    "Sidney Crosby": {
        "assists": "-1.0",  # Less scoring options
        "points": "-1.5",
        "shots": "-0.5"
    },
    "Evgeni Malkin": {
        "points": "-1.0",  # Increased responsibility but fewer options
        "assists": "-0.5",
        "shots": "-0.5"
    },
    
    # Sabres - massive injury impact
    "Tage Thompson": {
        "goals": "-1.0",  # Less support
        "assists": "-1.5",
        "points": "-2.5",
        "shots": "-1.0"
    },
    "Jack Quinn": {
        "points": "+1.0",  # Increased opportunity
        "shots": "+0.5",
        "assists": "+0.5"
    },
    
    # Devils - Hughes injury hurts
    "Nico Hischier": {
        "assists": "+1.0",  # More responsibility
        "points": "+1.5",
        "shots": "+0.5"
    },
    "Jesper Bratt": {
        "assists": "-1.0",  # No Hughes to feed
        "points": "-1.5",
        "shots": "-0.5"
    },
    
    # Rangers - major star injuries
    "Vincent Trocheck": {
        "assists": "+1.5",  # More responsibility
        "points": "+2.0",
        "shots": "+0.5"
    },
    "Mika Zibanejad": {
        "points": "+1.0",  # Increased role
        "assists": "+0.5"
    },
    
    # Panthers - Barkov injury devastating
    "Sam Reinhart": {
        "assists": "-2.0",  # No Barkov to play with
        "points": "-2.5",
        "shots": "-1.0"
    },
    "Matthew Tkachuk": {
        "assists": "-1.5",  # Less playmaking support
        "points": "-2.0",
        "shots": "-0.5"
    },
    
    # Lightning - Point injury hurts
    "Nikita Kucherov": {
        "assists": "-1.5",  # Less center support
        "points": "-2.0",
        "shots": "-0.5"
    },
    "Brandon Hagel": {
        "points": "-1.0",  # Reduced opportunities
        "assists": "-0.5"
    },
    
    # Golden Knights - Pietrangelo injury hurts
    "Jack Eichel": {
        "assists": "-1.0",  # Less quarterback from defense
        "points": "-1.5",
        "shots": "-0.5"
    },
    "Mark Stone": {
        "assists": "-0.5",  # Less defensive support
        "points": "-1.0"
    }
}

# Injury Impact Multipliers
NHL_INJURY_IMPACT_MULTIPLIERS = {
    "star_player": 2.5,      # Star players have massive impact
    "starter": 1.8,           # Starters have high impact  
    "bench_player": 1.0,      # Bench players have normal impact
    "role_player": 0.8        # Role players have reduced impact
}

# Player Categories for Impact Calculation
NHL_PLAYER_CATEGORIES = {
    # Superstar tier
    "Sidney Crosby": "star_player",
    "Evgeni Malkin": "star_player",
    "Jack Hughes": "star_player",
    "Adam Fox": "star_player",
    "Ilya Shesterkin": "star_player",
    "Aleksander Barkov": "star_player",
    "Brayden Point": "star_player",
    "Nikita Kucherov": "star_player",
    "Alex Ovechkin": "star_player",
    "Jack Eichel": "star_player",
    "Roman Josi": "star_player",
    "Auston Matthews": "star_player",
    "Connor McDavid": "star_player",
    "Leon Draisaitl": "star_player",
    "Nathan MacKinnon": "star_player",
    "Cale Makar": "star_player",
    
    # Starter tier
    "Tage Thompson": "starter",
    "Nico Hischier": "starter",
    "Vincent Trocheck": "starter",
    "Mika Zibanejad": "starter",
    "Sam Reinhart": "starter",
    "Matthew Tkachuk": "starter",
    "Brandon Hagel": "starter",
    "Mark Stone": "starter",
    "Sebastian Aho": "starter",
    "Tim Stutzle": "starter",
    "Travis Konecny": "starter",
    "Bo Horvat": "starter",
    "Mathew Barzal": "starter",
    "Timo Meier": "starter",
    "Jesper Bratt": "starter",
    "Mitch Marner": "starter",
    "Anze Kopitar": "starter",
    "Adrian Kempe": "starter",
    
    # Role player tier
    "Bryan Rust": "role_player",
    "Jack Quinn": "role_player",
    "Dawson Mercer": "role_player",
    "Alexis Lafreniere": "role_player",
    "Shane Pinto": "role_player",
    "Noah Cates": "role_player",
    "Erik Haula": "role_player",
    "Sam Bennett": "role_player",
    "Yanni Gourde": "role_player",
    "Corey Perry": "role_player",
    "Taylor Ward": "role_player"
}
