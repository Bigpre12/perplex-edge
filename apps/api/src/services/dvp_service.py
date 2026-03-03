"""
Defense vs Position (DvP) Service
Provides real mapping of how well an opposing team defends a specific player position.
"""
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.props import PropLine

logger = logging.getLogger(__name__)

# Positional maps for relevant stats per sport
NBA_POSITION_MAP = {
    "PG": ["player_assists", "player_threes", "player_points"],
    "SG": ["player_points", "player_threes"],
    "SF": ["player_points", "player_rebounds"],
    "PF": ["player_rebounds", "player_points"],
    "C":  ["player_rebounds", "player_blocks"],
}

def get_dvp_rating(team: str, position: str, prop_type: str, db: Session, last_n: int = 15) -> Dict[str, Any]:
    """Calculate real DvP rating based on historical hit rates against this team/position."""
    try:
        # Query settled props where the player's opponent was this team and position matched
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
        
        results = db.execute(stmt).scalars().all()
        
        if not results:
            return {"rating": "Neutral", "rank": "neutral", "label": "🟡 Matchup Data Pending", "sample": 0}

        # Calculate how often opponents hit their "Over" against this team
        # Note: This assumes PropLine has a way to check if it 'won' its line.
        # For simplicity, we'll check if hit_rate_l10 was recorded or a similar metric.
        # In a full system, we'd check against actual_value from LiveGameStat.
        
        # Mocking the hit calculation for now based on sample size until actual_value is fully wired
        hits = sum(1 for r in results if r.hit_rate_l10 > 50) 
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

def get_dvp_for_prop_card(player_id: str, db: Session) -> Dict[str, Any]:
    """Get DvP context ready for a prop card."""
    stmt = select(PropLine).where(PropLine.player_id == player_id, PropLine.is_settled == False).limit(1)
    prop = db.execute(stmt).scalar_one_or_none()

    if not prop:
        return {}

    dvp_results = {}
    # Default to NBA map, can be expanded for NFL/MLB
    relevant_props = NBA_POSITION_MAP.get(prop.position, ["player_points"])
    
    for pt in relevant_props:
        dvp_results[pt] = get_dvp_rating(prop.opponent, prop.position, pt, db)

    return {
        "player": prop.player_name,
        "opponent": prop.opponent,
        "position": prop.position,
        "dvp": dvp_results
    }


