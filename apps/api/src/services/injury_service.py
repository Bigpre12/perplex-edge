# apps/api/src/services/injury_service.py
import os
import logging
from typing import List, Dict, Any
from clients.espn_client import espn_client # type: ignore
from models import InjuryImpact
from sqlalchemy import select # type: ignore
from db.session import async_session_maker # type: ignore

logger = logging.getLogger(__name__)

class InjuryService:
    async def get_injuries(self, sport: str) -> List[Dict]:
        """Fetch injuries using the resilient ESPN client with known error corrections."""
        try:
            # Standardizing on the long-form key "basketball_nba" etc.
            if not sport.startswith("basketball_") and not sport.startswith("americanfootball_"):
                 sport_map = {"nba": "basketball_nba", "nfl": "americanfootball_nfl", "mlb": "baseball_mlb", "nhl": "icehockey_nhl"}
                 sport = sport_map.get(sport, sport)

            logger.info(f"InjuryService: Fetching live ESPN API data for {sport}")
            raw_injuries = await espn_client.fetch_injuries(sport)
            
            # KNOWN ERROR CORRECTION LAYER
            # Upstream ESPN feed sometimes scrambles player->team associations (e.g. Vucevic on Celtics)
            corrected_injuries = []
            if isinstance(raw_injuries, list):
                for team_group in raw_injuries:
                    team_display_name = team_group.get("displayName", "Unknown Team")
                    
                    filtered_injs = []
                    for inj in team_group.get("injuries", []):
                        athlete = inj.get("athlete", {})
                        player_name = athlete.get("displayName", "")
                        
                        # Fix Nikola Vucevic (Chicago Bulls, not Boston Celtics)
                        if "Nikola Vucevic" in player_name and "Celtics" in team_display_name:
                            logger.warning(f"InjuryService: Correcting team association for {player_name}")
                            # Skip him in the wrong team group; a more robust system would 're-home' him.
                            continue 
                        
                        filtered_injs.append(inj)
                    
                    if filtered_injs:
                        team_group["injuries"] = filtered_injs
                        corrected_injuries.append(team_group)
                
            # PERSIST to DB for historical tracking and analytical access
            from services.persistence_helpers import upsert_injuries
            db_rows = []
            if isinstance(corrected_injuries, list):
                for team_group in corrected_injuries:
                    team_display_name = team_group.get("displayName", "Unknown Team")
                    for inj in team_group.get("injuries", []):
                        athlete = inj.get("athlete", {})
                        db_rows.append({
                            "sport": sport,
                            "player": athlete.get("displayName", "Unknown"),
                            "team": team_display_name,
                            "status": inj.get("status", "Unknown"),
                            "note": inj.get("shortComment", "")
                        })
            
            if db_rows:
                await upsert_injuries(sport, db_rows)
                
            return corrected_injuries
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

    async def get_impact_signals(self, sport: str) -> List[Dict[str, Any]]:
        """Fetch processed injury impact signals from the database."""
        try:
            async with async_session_maker() as session:
                stmt = select(InjuryImpact).where(InjuryImpact.sport == sport)
                result = await session.execute(stmt)
                rows = result.scalars().all()
                return [
                    {
                        "player": row.player_name,
                        "impact_score": row.impact_score,
                        "affected_market": row.affected_market,
                        "adjustment": row.adjustment
                    } for row in rows
                ]
        except Exception as e:
            logger.error(f"InjuryService: Failed to fetch impact signals: {e}")
            return []
        
        return [] # Explicit final return to satisfy analyzer


injury_service = InjuryService()
