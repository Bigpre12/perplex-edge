"""
SportsGameOdds Market Service
Unifies all SGO constants to parse oddID strings into human-readable descriptions.
"""

from app_core.sgo_stat_constants import get_sgo_stat_display
from app_core.sgo_entity_constants import get_sgo_entity_display, get_fixed_sgo_entity
from app_core.sgo_period_constants import get_sgo_period_display
from app_core.sgo_bet_type_constants import get_sgo_bet_type_name, get_sgo_side_name

class SGOMarketService:
    @staticmethod
    def parse_odd_id(odd_id: str, sport_id: str = "UNKNOWN"):
        """
        Decomposes an SGO oddID into its constituent parts and resolves display names.
        Format: {statID}-{statEntityID}-{periodID}-{betTypeID}-{sideID}
        """
        parts = odd_id.split("-")
        
        # Handle malformed IDs
        if len(parts) < 5:
            return {
                "stat": parts[0] if len(parts) > 0 else "Unknown",
                "entity": parts[1] if len(parts) > 1 else "Unknown",
                "period": parts[2] if len(parts) > 2 else "Unknown",
                "bet_type": parts[3] if len(parts) > 3 else "Unknown",
                "side": parts[4] if len(parts) > 4 else "Unknown",
                "display": odd_id
            }
            
        stat_id, entity_id, period_id, bet_type_id, side_id = parts[0], parts[1], parts[2], parts[3], parts[4]
        
        stat_display = get_sgo_stat_display(sport_id, stat_id)
        entity_display = get_sgo_entity_display(entity_id)
        period_display = get_sgo_period_display(period_id)
        bet_type_display = get_sgo_bet_type_name(bet_type_id)
        side_display = get_sgo_side_name(bet_type_id, side_id)
        
        return {
            "stat_id": stat_id,
            "stat_display": stat_display,
            "entity_id": entity_id,
            "entity_display": entity_display,
            "period_id": period_id,
            "period_display": period_display,
            "bet_type_id": bet_type_id,
            "bet_type_display": bet_type_display,
            "side_id": side_id,
            "side_display": side_display
        }

    @classmethod
    def get_market_description(cls, odd_id: str, sport_id: str = "UNKNOWN") -> str:
        """
        Generates a full human-readable description for an oddID.
        Example: 'Home Team Moneyline (1st Half)'
        """
        parsed = cls.parse_odd_id(odd_id, sport_id)
        
        # Format: Stat Entity - Bet Type (Period)
        # e.g., Home Team Moneyline (Full Event)
        # e.g., Over 214.5 Total Points (Full Event) - handled slightly differently for O/U
        
        if parsed["bet_type_id"].lower() == "ou":
            return f"{parsed['side_display']} {parsed['stat_display']} - {parsed['entity_display']} ({parsed['period_display']})"
        
        if parsed["bet_type_id"].lower() in ["ml", "sp", "ml3way"]:
            return f"{parsed['entity_display']} {parsed['bet_type_display']} ({parsed['period_display']})"
            
        return f"{parsed['entity_display']} {parsed['stat_display']} {parsed['side_display']} ({parsed['period_display']})"

    @classmethod
    def get_market_label(cls, odd_id: str, sport_id: str = "UNKNOWN") -> str:
        """
        Returns a shorter label for UI components.
        Example: 'Home ML'
        """
        parsed = cls.parse_odd_id(odd_id, sport_id)
        
        if parsed["bet_type_id"].lower() == "ml":
            return f"{parsed['entity_display']} ML"
        if parsed["bet_type_id"].lower() == "sp":
            return f"{parsed['entity_display']} Spread"
        if parsed["bet_type_id"].lower() == "ou":
            return f"Total {parsed['stat_display']} {parsed['side_display']}"
            
        return f"{parsed['entity_display']} {parsed['stat_display']}"
