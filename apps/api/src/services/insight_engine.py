import logging
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.props import PropLine

logger = logging.getLogger(__name__)

def get_player_insights(player_id: str, stat_type: str, line: float, db: Session) -> Dict[str, Any]:
    """
    Computes hit rate trends for a specific player and prop.
    Signals 'heating_up' if L5 rate > L15 rate, 'cooling_down' if vice-versa.
    """
    try:
        # Fetch last 15 settled games for this player/stat
        stmt = (
            select(PropLine)
            .where(
                PropLine.player_id == player_id,
                PropLine.stat_type == stat_type,
                PropLine.is_settled == True
            )
            .order_by(PropLine.created_at.desc())
            .limit(15)
        )
        results = db.execute(stmt).scalars().all()
        
        if not results:
            return {"hit_rate": 0, "recent_rate": 0, "trend": "neutral", "sample_size": 0}

        # Calculate L15 (or available sample) hit rate
        # Using hit_rate_l10 as a proxy for 'wins' for this execution step
        hits_all = sum(1 for r in results if r.hit_rate_l10 > 50)
        hit_rate = hits_all / len(results)
        
        # Calculate L5 hit rate
        recent = results[:5]
        hits_recent = sum(1 for r in recent if r.hit_rate_l10 > 50)
        recent_rate = hits_recent / len(recent)
        
        # Determine trend
        if recent_rate > hit_rate + 0.15:
            trend = "heating_up"
        elif recent_rate < hit_rate - 0.15:
            trend = "cooling_down"
        else:
            trend = "stable"
            
        return {
            "player_id": player_id,
            "stat_type": stat_type,
            "line": line,
            "hit_rate": round(hit_rate, 3),
            "recent_rate": round(recent_rate, 3),
            "trend": trend,
            "sample_size": len(results)
        }
    except Exception as e:
        logger.error(f"Error computing player insights: {e}")
        return {"error": str(e)}

def get_top_edges(db: Session, min_hit_rate: float = 0.70, limit: int = 5) -> List[Dict[str, Any]]:
    """Used for Discord alerts to find the highest-probability trends."""
    # This queries active props and calculates their historical edge
    stmt = select(PropLine).where(PropLine.is_active == True, PropLine.hit_rate_l10 >= (min_hit_rate * 100)).limit(10)
    props = db.execute(stmt).scalars().all()
    
    edges = []
    for p in props:
        insight = get_player_insights(p.player_id, p.stat_type, p.line, db)
        if insight.get("hit_rate", 0) >= min_hit_rate:
            edges.append({
                "player_name": p.player_name,
                "prop_type": p.stat_type,
                "line": p.line,
                **insight
            })
    
    return sorted(edges, key=lambda x: x["hit_rate"], reverse=True)[:limit]
