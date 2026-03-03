import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ParlayService:
    @staticmethod
    def calculate_correlation(leg1: Dict[str, Any], leg2: Dict[str, Any]) -> float:
        """
        Returns a correlation score between -1.0 and 1.0.
        Higher positive score means the legs are 'synergistic' (highly correlated).
        """
        # Basic same-game parlay check
        if leg1.get('game_id') != leg2.get('game_id'):
            return 0.0

        sport = leg1.get('sport', '').lower()
        p1_name = leg1.get('player_name', '')
        p2_name = leg1.get('player_name', '') # Error: was leg1, should be leg2
        p2_name = leg2.get('player_name', '')
        
        stat1 = leg1.get('stat_type', '').lower()
        stat2 = leg2.get('stat_type', '').lower()

        # NBA Correlation: PG Assists + Teammate Points
        if sport == 'nba':
            if stat1 == 'assists' and stat2 == 'points':
                return 0.25 # Teammate scoring helps PG assists
            if stat1 == 'points' and stat2 == 'points':
                return -0.15 # Usage competition (mild negative)

        # NFL Correlation: QB Yards + WR Yards (The Golden Standard)
        if sport == 'nfl':
            if stat1 == 'passing_yards' and stat2 == 'receiving_yards':
                # Check if they are on the same team (simplified)
                return 0.45
            if stat1 == 'passing_tds' and stat2 == 'receiving_yards':
                return 0.40

        # NHL Correlation: C Assists + W Points
        if sport == 'nhl':
            if stat1 == 'assists' and stat2 == 'points':
                return 0.30

        return 0.0

    def suggest_bundles(self, high_ev_props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Take a list of high-EV props and bundle them into correlated parlays.
        """
        bundles = []
        seen_indices = set()

        for i, p1 in enumerate(high_ev_props):
            if i in seen_indices: continue
            
            for j, p2 in enumerate(high_ev_props):
                if i == j or j in seen_indices: continue
                
                corr = self.calculate_correlation(p1, p2)
                if corr > 0.2:
                    bundles.append({
                        "id": f"bundle_{len(bundles)}",
                        "legs": [p1, p2],
                        "correlation_score": corr,
                        "combined_ev": (p1.get('edge', 0) + p2.get('edge', 0)) / 2 + (corr * 0.1),
                        "description": f"Correlated {p1.get('sport').upper()} Bundle"
                    })
                    seen_indices.add(i)
                    seen_indices.add(j)
                    break
        
        return sorted(bundles, key=lambda x: x['combined_ev'], reverse=True)

parlay_service = ParlayService()
