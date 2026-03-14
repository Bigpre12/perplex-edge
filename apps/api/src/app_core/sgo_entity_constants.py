"""
SportsGameOdds Entity Constants
Centralized registry for statEntityID values and their logic.
Data source: SportsGameOdds API Documentation.
"""

# Base entity mappings
SGO_ENTITIES = {
    "all": "All / Combined",
    "home": "Home Team",
    "away": "Away Team",
    "side1": "Side 1",
    "side2": "Side 2",
}

# Fixed statEntityID values based on (betTypeID, sideID)
# Format: (betTypeID, sideID) -> statEntityID
SGO_FIXED_ENTITIES = {
    ("ml", "home"): "home",
    ("ml", "away"): "away",
    ("sp", "home"): "home",
    ("sp", "away"): "away",
    ("ml3way", "home"): "home",
    ("ml3way", "away"): "away",
    ("ml3way", "draw"): "all",
    ("ml3way", "home+draw"): "home",
    ("ml3way", "away+draw"): "away",
    ("ml3way", "not_draw"): "all",
    ("prop", "side1"): "side1",
    ("prop", "side2"): "side2",
}

def get_sgo_entity_display(entity_id: str) -> str:
    """Get display name for an SGO statEntityID."""
    lowered = entity_id.lower()
    if lowered in SGO_ENTITIES:
        return SGO_ENTITIES[lowered]
        
    # If it's a player or team ID, return it as-is or cleaned
    return entity_id.replace("_", " ").title()

def get_fixed_sgo_entity(bet_type_id: str, side_id: str) -> str:
    """Get the fixed statEntityID for a given bet type and side."""
    return SGO_FIXED_ENTITIES.get((bet_type_id.lower(), side_id.lower()), "unknown")

def is_sgo_player_entity(entity_id: str) -> bool:
    """Check if the entityID likely represents a specific player/team."""
    return entity_id.lower() not in SGO_ENTITIES
