class AsyncSession: pass
from fastapi import APIRouter, Query, Depends
from database import get_async_db
from api.immediate_working import get_working_player_props_immediate
import asyncio

router = APIRouter(prefix="/api/top-edges", tags=["top-edges"])

@router.get("/")
async def top_edges_feed(
    sport: str = Query(None),
    min_hit_rate: float = Query(0.65),
    trend: str = Query(None),
    limit: int = Query(25),
    db: AsyncSession = Depends(get_async_db),
):
    try:
        sports_to_scan = [sport] if sport else [
            "basketball_nba", "americanfootball_nfl",
            "icehockey_nhl", "baseball_mlb"
        ]
        results = []
        for s in sports_to_scan:
            res = await get_working_player_props_immediate(sport=s, limit=limit)
            items = res.get("items", []) if isinstance(res, dict) else []
            for item in items:
                item["trend"] = "heating_up" if item.get("edge", 0) > 0.05 else "stable"
                item["sample_size"] = 10
                item["is_steam"] = item.get("steam_score", 0) > 0
                results.append(item)

        if trend:
            results = [e for e in results if e.get("trend") == trend]
        results.sort(key=lambda x: x.get("edge", 0), reverse=True)
        return {"edges": results[:limit], "total": len(results)}
    except Exception as e:
        import traceback; traceback.print_exc()
        return {"edges": [], "total": 0, "error": str(e)}
