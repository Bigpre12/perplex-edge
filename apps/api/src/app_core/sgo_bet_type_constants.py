"""
SportsGameOdds Bet Type and Side Constants
Centralized registry for all supported bet types and their outcome sides.
Data source: SportsGameOdds API Documentation.
"""

# Bet Type display names
SGO_BET_TYPES = {
    "ml": "Moneyline",
    "sp": "Spread",
    "ou": "Over/Under",
    "eo": "Even/Odd",
    "yn": "Yes/No",
    "ml3way": "3-Way Moneyline",
    "prop": "Prop Bet",
}

# Side display names per bet type
# Format: betTypeID -> sideID -> Display Name
SGO_SIDES = {
    "ml": {
        "home": "Home",
        "away": "Away",
    },
    "sp": {
        "home": "Home",
        "away": "Away",
    },
    "ou": {
        "over": "Over",
        "under": "Under",
    },
    "eo": {
        "even": "Even",
        "odd": "Odd",
    },
    "yn": {
        "yes": "Yes",
        "no": "No",
    },
    "ml3way": {
        "home": "Home",
        "away": "Away",
        "draw": "Draw",
        "away+draw": "Away/Draw",
        "home+draw": "Home/Draw",
        "not_draw": "Home/Away",
    },
    "prop": {
        "side1": "Option 1",
        "side2": "Option 2",
    }
}

def get_sgo_bet_type_name(bet_type_id: str) -> str:
    """Get display name for an SGO betTypeID."""
    return SGO_BET_TYPES.get(bet_type_id.lower(), bet_type_id.upper())

def get_sgo_side_name(bet_type_id: str, side_id: str) -> str:
    """Get display name for an SGO sideID based on the betTypeID."""
    bt_id = bet_type_id.lower()
    s_id = side_id.lower()
    
    if bt_id in SGO_SIDES and s_id in SGO_SIDES[bt_id]:
        return SGO_SIDES[bt_id][s_id]
        
    return side_id.replace("_", " ").title()
