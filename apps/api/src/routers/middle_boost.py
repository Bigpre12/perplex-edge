from fastapi import APIRouter, Query, Depends
from typing import Optional, List, Dict, Any
from services.props_service import props_service
from common_deps import get_user_tier, require_elite

router = APIRouter(tags=["middle-boost"])

@router.get("")
async def get_middle_boost(
    sport: Optional[str] = Query(None),
    tier: str = Depends(get_user_tier)
):
    """
    Identifies Middle opportunities where lines differ across sportsbooks.
    Example: Book A has Over 22.5, Book B has Under 24.5.
    """
    if tier != "elite":
        return {
            "items": [],
            "message": "Elite subscription required for Middle & Boost Analysis",
            "tier_required": "elite"
        }

    # Pull all live props (already grouped by player/stat)
    props = await props_service.get_all_props(sport_filter=sport)
    
    middles = []
    
    for p in props:
        overs = p.get("over", [])
        unders = p.get("under", [])
        
        if not overs or not unders:
            continue
            
        # We want to find the LOWEST Over line and the HIGHEST Under line
        # to maximize the middle window.
        # But wait, to WIN both, we need to bet:
        # 1. Over on the LOW line
        # 2. Under on the HIGH line
        
        # Best Over for a middle = lowest line with best price
        # actually, lowest line is what we want to bet Over on.
        best_over_for_mid = min(overs, key=lambda x: x["line"])
        # Best Under for a middle = highest line
        best_under_for_mid = max(unders, key=lambda x: x["line"])
        
        width = best_under_for_mid["line"] - best_over_for_mid["line"]
        
        if width > 0:
            # We found a middle!
            # Calculate a pseudo-EV based on width and average juice
            # Higher width = Higher "Premium" value
            ev_percent = round(width * 5.0, 1) # Heuristic: each point of width is ~5% EV in NBA/NFL
            
            middles.append({
                "id": f"mid_{p['player_name']}_{p['market_key']}_{width}".replace(" ", "_"),
                "status": "VULNERABLE" if width >= 1.5 else "ACTIVE",
                "match": f"{p['player_name']} ({p['stat_type']})",
                "ev_percent": ev_percent,
                "book_a": {
                    "name": best_over_for_mid["book"],
                    "line": f"Over {best_over_for_mid['line']}",
                    "odds": f"{best_over_for_mid['odds']}" if best_over_for_mid['odds'] < 0 else f"+{best_over_for_mid['odds']}"
                },
                "book_b": {
                    "name": best_under_for_mid["book"],
                    "line": f"Under {best_under_for_mid['line']}",
                    "odds": f"{best_under_for_mid['odds']}" if best_under_for_mid['odds'] < 0 else f"+{best_under_for_mid['odds']}"
                },
                "middle_width": width,
                "sport": p.get("sport_key")
            })

    # Sort by widest middle first
    middles.sort(key=lambda x: x["middle_width"], reverse=True)
    
    return {
        "items": middles,
        "count": len(middles)
    }
