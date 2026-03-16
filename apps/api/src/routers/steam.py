class AsyncSession: pass
# apps/api/src/routers/steam.py
from fastapi import APIRouter, Query, Depends
from typing import Optional
from db.session import get_async_db
from services.steam_service import steam_service
from datetime import datetime, timedelta, timezone

router = APIRouter(tags=["steam"])

# In-memory store for deduplication across requests
steam_log: list = []

@router.get("")
@router.get("/alerts")
async def steam_alerts(
    sport: Optional[str] = Query("basketball_nba"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Returns live steam and sharp money alerts with server-side deduplication.
    """
    global steam_log
    new_alerts = await steam_service.detect_and_persist_steam(sport, db)
    
    # 1. Update in-memory log with new alerts
    now = datetime.now(timezone.utc)
    for alert in new_alerts:
        alert["detected_at"] = now
        steam_log.append(alert)
        
    # 2. Cleanup: Only keep last 30 minutes of history
    cutoff = now - timedelta(minutes=30)
    steam_log = [a for a in steam_log if a.get("detected_at", now) > cutoff]
    
    # 3. Server-side dedupe by fingerprint (player-line-side-minute)
    seen = set()
    unique = []
    # Process newest first to keep latest metadata if any
    for alert in sorted(steam_log, key=lambda x: x.get("detected_at", now), reverse=True):
        time_key = alert.get("detected_at").strftime("%H:%M")
        fingerprint = f"{alert.get('player_name', 'Unknown')}-{alert.get('line', '0')}-{alert.get('side', 'over')}-{time_key}"
        if fingerprint not in seen:
            seen.add(fingerprint)
            unique.append(alert)

    return {
        "alerts": unique[:20],  # Return last 20 unique alerts
        "total": len(unique),
        "tracked_props": len(steam_service.line_history),
        "sport": sport,
    }

@router.get("/history/{player_key}")
async def line_history_for_player(player_key: str):
    """
    Returns the snapshot history for a specific player/prop key.
    """
    return steam_service.line_history.get(player_key, [])
