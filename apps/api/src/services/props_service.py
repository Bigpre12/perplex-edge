"""
Props Service - Shared logic for player props, combos, and parlay builders.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import text, select, and_

from models.brain import ModelPick
from app.antigravity_engine import apply_antigravity_filter

logger = logging.getLogger(__name__)

def serialize_pick(p: ModelPick) -> Dict[str, Any]:
    """Helper to transform ModelPick into the standard API prop format."""
    return {
        "id": p.id,
        "player": {
            "id": getattr(p, 'player_id', hash(p.player_name) % 1000000),
            "name": p.player_name,
            "position": "N/A",
            "team": getattr(p, 'team', 'TBD')
        },
        "player_name": p.player_name,
        "market": {"stat_type": p.stat_type.replace('player_', '')},
        "stat_type": p.stat_type.replace('player_', ''),
        "line_value": p.line,
        "line": p.line,
        "side": "over",
        "odds": p.odds or -110,
        "sportsbook": p.sportsbook or "Sharp Model",
        "display_edge": round(p.ev_percentage / 100, 4) if p.ev_percentage else 0.0,
        "edge": round(p.ev_percentage / 100, 4) if p.ev_percentage else 0.0,
        "confidence_score": round(p.confidence / 100, 4) if p.confidence else 0.5,
        "model_probability": p.model_probability or 0.5,
        "sport_id": p.sport_id,
        "sport_key": p.sport_key,
        "sharp_money": getattr(p, 'sharp_money', False),
        "created_at": p.created_at.isoformat() if hasattr(p.created_at, 'isoformat') else str(p.created_at)
    }

def strip_premium_fields(props: List[Dict[str, Any]], tier: str) -> List[Dict[str, Any]]:
    """Monetization Engine: Removes premium data for free users."""
    if tier == "free":
        for p in props:
            p.pop("kelly_units", None)
            p.pop("sharp_money", None)
            p.pop("steam_score", None)
            p.pop("display_edge", None)
            p.pop("edge", None)
            p["is_locked"] = True
        return props[:3]
    return props

async def get_props_by_sport(sport_id: int, limit: int, db: Session, tier: str = "pro"):
    """Fetch and filter standard player props for a specific sport."""
    try:
        stmt = select(ModelPick).where(
            and_(
                ModelPick.sport_id == sport_id,
                ModelPick.ev_percentage > 0,
                ModelPick.confidence >= 50
            )
        ).order_by(ModelPick.ev_percentage.desc()).limit(limit if tier != "free" else 10)
        
        result = db.execute(stmt)
        picks = result.scalars().all()
        
        raw = [serialize_pick(p) for p in picks]
        filtered = await apply_antigravity_filter(raw)
        
        # Apply Gating
        gated = strip_premium_fields(filtered, tier)
        
        return {"items": gated, "total": len(gated), "sport_id": sport_id, "tier": tier}
    except Exception as e:
        logger.error(f"Error in get_props_by_sport: {e}")
        return {"items": [], "total": 0, "sport_id": sport_id, "error": str(e)}

async def get_combos_by_sport(sport_id: int, limit: int, db: Session, tier: str = "pro"):
    """Get same-player multi-prop combos (e.g. PTS+REB+AST)"""
    props_res = await get_props_by_sport(sport_id=sport_id, limit=100, db=db, tier="pro") # Fetch full data for engine
    items = props_res.get("items", [])

    # Group by player
    player_props = {}
    for prop in items:
        pid = prop.get("player", {}).get("id", prop.get("player_name"))
        if pid not in player_props:
            player_props[pid] = []
        player_props[pid].append(prop)

    # Only players with 2+ props = combo candidate
    combos = []
    for pid, props_list in player_props.items():
        if len(props_list) >= 2:
            combined_ev = sum(p.get("display_edge", 0) for p in props_list)
            combos.append({
                "player": props_list[0].get("player"),
                "props": props_list[:3],  # max 3-leg combo
                "combined_ev": round(combined_ev, 4),
                "leg_count": min(len(props_list), 3),
                "sharp": any(p.get("sharp_money") for p in props_list),
            })

    combos.sort(key=lambda x: x["combined_ev"], reverse=True)
    if tier == "free":
        return {"items": combos[:1] if combos else [], "total": len(combos), "sport_id": sport_id, "tier": tier, "is_locked": True}
    return {"items": combos[:limit], "total": len(combos), "sport_id": sport_id, "tier": tier}

async def get_fight_combos(sport_id: int, limit: int, db: Session, tier: str = "pro"):
    """
    MMA/Boxing combos = multiple fight winners on same card.
    Groups by event (game_id), picks best moneyline per fight.
    """
    props_res = await get_props_by_sport(sport_id=sport_id, limit=100, db=db, tier="pro")
    items = props_res.get("items", [])

    # Group by event/card (game_id)
    by_event = {}
    for prop in items:
        gid = prop.get("game_id") or "unknown_event"
        if gid not in by_event:
            by_event[gid] = []
        by_event[gid].append(prop)

    combos = []
    for gid, fights in by_event.items():
        # Only moneyline picks for fight combos
        ml_picks = [f for f in fights if f.get("market", {}).get("stat_type") == "fight_result"]
        if len(ml_picks) >= 2:
            combined_ev = sum(p.get("display_edge", 0) for p in ml_picks)
            combos.append({
                "event_id": gid,
                "fights": ml_picks[:4],  # max 4-fight parlay
                "combined_ev": round(combined_ev, 4),
                "leg_count": min(len(ml_picks), 4),
                "sharp": any(p.get("sharp_money") for p in ml_picks),
                "player": {"name": f"Event: {gid}"} # UI Compatibility fallback
            })

    combos.sort(key=lambda x: x["combined_ev"], reverse=True)
    if tier == "free":
        return {"items": combos[:1] if combos else [], "total": len(combos), "sport_id": sport_id, "tier": tier, "is_locked": True}

    return {"items": combos[:limit], "total": len(combos), "sport_id": sport_id, "tier": tier}

async def build_parlay_by_sport(sport_id: int, legs: int, db: Session, tier: str = "pro"):
    """Build top-EV parlay from available props"""
    props_res = await get_props_by_sport(sport_id=sport_id, limit=50, db=db, tier="pro")
    items = props_res.get("items", [])

    # Take top N by EV, one prop per player (no same-player correlation)
    seen_players = set()
    parlay_legs = []
    for prop in items:
        pid = prop.get("player", {}).get("id", prop.get("player_name"))
        if pid not in seen_players:
            seen_players.add(pid)
            parlay_legs.append(prop)
        if len(parlay_legs) >= legs:
            break


    # Calculate combined parlay odds
    combined_prob = 1.0
    for leg in parlay_legs:
        combined_prob *= leg.get("model_probability", 0.5)

    combined_odds = round((combined_prob / (max(0.0001, 1 - combined_prob))) * -100, 0) if combined_prob > 0.5 else round((1 - combined_prob) / max(0.0001, combined_prob) * 100, 0)

    result = {
        "legs": parlay_legs,
        "leg_count": len(parlay_legs),
        "combined_probability": round(combined_prob, 4),
        "combined_odds": combined_odds,
        "sport_id": sport_id,
        "tier": tier,
        "sharp_count": sum(1 for l in parlay_legs if l.get("sharp_money")),
    }
    
    if tier == "free":
        result["is_locked"] = True
        # Strip fields from legs
        strip_premium_fields(result["legs"], tier)
        
    return result
