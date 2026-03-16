# apps/api/src/services/injury_service.py
import os
import logging
from typing import List, Dict, Any
from clients.espn_client import espn_client
from models.signals import InjuryImpact
from sqlalchemy import select
from database import async_session_maker

logger = logging.getLogger(__name__)

class InjuryService:
    async def get_injuries(self, sport: str) -> List[Dict]:
        """Fetch injuries using the resilient ESPN client with local fallback."""
        try:
            # Map sport key if needed
            sport_map = {"basketball_nba": "nba", "football_nfl": "nfl", "baseball_mlb": "mlb", "hockey_nhl": "nhl"}
            espn_sport = sport_map.get(sport, sport).split("_")[-1]
            
            # Check for local data provided by user first
            local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", f"espn_injuries_{espn_sport}.json"))
            logger.info(f"InjuryService: Checking local path: {local_path}")
            if os.path.exists(local_path):
                import json
                with open(local_path, 'r') as f:
                    data = json.load(f)
                    injuries = data.get("injuries", [])
                    logger.info(f"InjuryService: Found {len(injuries)} teams in local data.")
                    return injuries
            
            logger.info(f"InjuryService: No local file, falling back to ESPN API for {espn_sport}")
            return await espn_client.get_injuries(espn_sport)
        except Exception as e:
            logger.error(f"InjuryService: Fetch failed for {sport}: {e}")
            return []

    async def filter_injured_players(self, props: List[Dict], sport: str, name_key: str = "player_name") -> List[Dict]:
        """Filter out players with high-impact injuries."""
        raw_data = await self.get_injuries(sport)
        
        # Flatten ESPN structure: injuries is typically a list of team objects
        # Each team object has its own 'injuries' list of athlete objects
        injured_players = []
        if isinstance(raw_data, list):
            for team in raw_data:
                team_injuries = team.get("injuries", [])
                if not isinstance(team_injuries, list): continue
                for inj in team_injuries:
                    athlete = inj.get("athlete", {})
                    player_name = athlete.get("displayName", inj.get("player", ""))
                    status = inj.get("status", "").lower()
                    
                    if player_name:
                        injured_players.append({
                            "player": player_name,
                            "status": status,
                            "comment": inj.get("shortComment", "")
                        })

        injured_names = set()
        for inj in injured_players:
            status = inj.get("status", "").lower()
            if any(s in status for s in ["out", "doubtful", "suspension", "injury reserve", "day-to-day"]):
                injured_names.add(inj.get("player", "").lower())
        
        if not injured_names:
            return props
            
        return [p for p in props if p.get(name_key, "").lower() not in injured_names]

    async def get_impact_signals(self, sport: str) -> List[Dict]:
        """Fetch processed injury impact signals from the database."""
        async with async_session_maker() as session:
            stmt = select(InjuryImpact).where(InjuryImpact.sport == sport)
            result = await session.execute(stmt)
            return [
                {
                    "player": row.player_name,
                    "impact_score": row.impact_score,
                    "affected_market": row.affected_market,
                    "adjustment": row.adjustment
                } for row in result.scalars().all()
            ]

injury_service = InjuryService()
