# routers/props_history.py
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Query
from services.db import db
from routers.schemas.props_history import PropLineSnapshot

router = APIRouter(prefix="/props", tags=["props-history"])

@router.get("/history", response_model=List[PropLineSnapshot])
async def get_prop_history(
    sport: str = Query(...),
    player_id: Optional[str] = Query(None),
    player_name: Optional[str] = Query(None),
    market_key: str = Query(...),
    book: str = Query(...),
    hours: int = Query(24, ge=1, le=168),
):
    """
    Time-series of line/odds snapshots for a single prop+book over a time window.
    Use either player_id or player_name (player_id preferred).
    """
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    filters = ["sport = :sport", "market_key = :market_key", "book = :book", "snapshot_at >= :since"]
    params = {
        "sport": sport,
        "market_key": market_key,
        "book": book,
        "since": since,
    }

    if player_id:
        filters.append("player_id = :player_id")
        params["player_id"] = player_id
    elif player_name:
        filters.append("player_name = :player_name")
        params["player_name"] = player_name

    where_clause = " and ".join(filters)

    query = f"""
    select
      snapshot_at,
      sport,
      league,
      game_id,
      player_id,
      player_name,
      team,
      market_key,
      market_label,
      line,
      book,
      odds_over,
      odds_under
    from public.props_history
    where {where_clause}
    order by snapshot_at asc;
    """

    rows = await db.fetch_all(query, params)
    return [PropLineSnapshot(**dict(r)) for r in rows]
