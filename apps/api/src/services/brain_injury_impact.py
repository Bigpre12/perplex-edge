import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy import select, insert
from db.session import async_session_maker
from models.signals import InjuryImpact
from services.injury_service import injury_service

logger = logging.getLogger(__name__)

class InjuryImpactBrain:
    """
    Layer 2: Injury Impact Brain
    Quantifies how player status changes affect team performance and betting lines.
    """

    async def analyze_impacts(self, sport: str):
        """
        Fetches live injuries and calculates quantified impacts.
        """
        # 1. Fetch live injury data
        # 'basketball_nba' -> 'nba'
        sport_short = sport.split("_")[-1] if "_" in sport else sport
        team_groups = await injury_service.get_injuries(sport)
        
        # Flatten team groups into a single injury list
        injuries = []
        for tg in team_groups:
            team_name = tg.get("displayName", "Unknown")
            for inj_raw in tg.get("injuries", []):
                athlete = inj_raw.get("athlete", {})
                injuries.append({
                    "player": athlete.get("displayName", "Unknown"),
                    "team": team_name,
                    "status": inj_raw.get("status", "Unknown"),
                    "impact": inj_raw.get("impact", "low"),
                    "description": inj_raw.get("shortComment", "No description")
                })

        async with async_session_maker() as session:
            try:
                impacts_to_save = []
                
                for inj in injuries:
                    if inj['impact'].lower() not in ['high', 'medium', 'critical']:
                        continue
                    
                    # 2. Quantification Logic (Heuristics for now)
                    # In a production system, this would use a usage-transfer model
                    affected_markets = []
                    teammate_boosts = []
                    
                    if sport_short == 'nba':
                        if inj['impact'] == 'high':
                            affected_markets.append({"market": "points", "adjustment": -4.5})
                            teammate_boosts.append({"player": "Usage Leader B", "boost": 0.18})
                        else:
                            affected_markets.append({"market": "points", "adjustment": -1.5})
                            teammate_boosts.append({"player": "Backup X", "boost": 0.08})
                    
                    elif sport_short == 'nfl':
                        if inj['position'] in ['QB']:
                            affected_markets.append({"market": "team_total", "adjustment": -6.5})
                        elif inj['position'] in ['WR', 'RB'] and inj['impact'] == 'high':
                            affected_markets.append({"market": "passing_yards", "adjustment": -25.0})

                    # 3. Build Impact Record
                    impact_record = {
                        "sport": sport,
                        "player_name": inj['player'],
                        "team": inj['team'],
                        "status": inj['status'],
                        "impact_description": inj['description'],
                        "affected_markets": affected_markets,
                        "teammate_boosts": teammate_boosts
                    }
                    impacts_to_save.append(impact_record)

                # 4. Save to DB
                if impacts_to_save:
                    # Clear old impacts for this sport to keep it fresh
                    # In real app, might want to keep history but for UI we want current
                    # For now, just append
                    await session.execute(insert(InjuryImpact).values(impacts_to_save))
                    await session.commit()
                    logger.info(f"InjuryBrain: Quantified {len(impacts_to_save)} impacts for {sport}")

            except Exception as e:
                await session.rollback()
                logger.error(f"InjuryBrain: Analysis failed: {e}")

injury_impact_brain = InjuryImpactBrain()
