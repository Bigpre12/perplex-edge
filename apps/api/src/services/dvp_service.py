from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
"""
Defense vs Position (DvP) Service
Provides real mapping of how well an opposing team defends a specific player position.
"""
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import select, func
from models.prop import PropLine

logger = logging.getLogger(__name__)

# Positional maps for relevant stats per sport
NBA_POSITION_MAP = {
    "PG": ["player_assists", "player_threes", "player_points"],
    "SG": ["player_points", "player_threes"],
    "SF": ["player_points", "player_rebounds"],
    "PF": ["player_rebounds", "player_points"],
    "C":  ["player_rebounds", "player_blocks"],
}

class DvpService:
    def __init__(self):
        self.nba_position_map = NBA_POSITION_MAP

    async def get_dvp_rating(self, team: str, position: str, prop_type: str, db: AsyncSession, last_n: int = 15) -> Dict[str, Any]:
        """Calculate real DvP rating based on historical hit rates against this team/position."""
        if not db:
            logger.warning(f"No DB session provided to get_dvp_rating for {team} {position} {prop_type}")
            return {"rating": "Neutral", "rank": "neutral", "label": "🟡 Matchup Data Pending", "sample": 0}

        try:
            stmt = (
                select(PropLine)
                .where(
                    PropLine.opponent == team,
                    PropLine.position == position,
                    PropLine.stat_type == prop_type,
                    PropLine.is_settled == True
                )
                .order_by(PropLine.created_at.desc())
                .limit(last_n)
            )
            
            res = await db.execute(stmt)
            results = res.scalars().all()
            
            if not results:
                return {"rating": "Neutral", "rank": "neutral", "label": "🟡 Matchup Data Pending", "sample": 0}

            hits = sum(1 for r in results if (r.hit_rate_l10 or 0) > 50) 
            allow_rate = hits / len(results)

            if allow_rate >= 0.65:
                rank = "favorable"
                label = "🟢 Favorable Matchup"
                rating = "Favorable"
            elif allow_rate >= 0.45:
                rank = "neutral"
                label = "🟡 Neutral Matchup"
                rating = "Neutral"
            else:
                rank = "tough"
                label = "🔴 Tough Matchup"
                rating = "Tough"

            return {
                "team": team,
                "position": position,
                "prop_type": prop_type,
                "allow_rate": round(allow_rate, 3),
                "rank": rank,
                "label": label,
                "rating": rating,
                "sample": len(results),
            }
        except Exception as e:
            logger.error(f"Error calculating real DvP: {e}")
            return {"error": str(e)}

    async def get_dvp_for_prop_card(self, player_id: str, db: AsyncSession) -> Dict[str, Any]:
        """Get DvP context ready for a prop card."""
        stmt = select(PropLine).where(PropLine.player_id == player_id, PropLine.is_settled == False).limit(1)
        res = await db.execute(stmt)
        prop = res.scalar_one_or_none()

        if not prop:
            return {}

        dvp_results = {}
        relevant_props = self.nba_position_map.get(prop.position, ["player_points"])
        
        for pt in relevant_props:
            dvp_results[pt] = await self.get_dvp_rating(prop.opponent, prop.position, pt, db)

        return {
            "player": prop.player_name,
            "opponent": prop.opponent,
            "position": prop.position,
            "dvp": dvp_results
        }

dvp_service = DvpService()
get_dvp_rating = dvp_service.get_dvp_rating
get_dvp_for_prop_card = dvp_service.get_dvp_for_prop_card
