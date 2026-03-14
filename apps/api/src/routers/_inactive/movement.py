from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.snapshots import LineSnapshot
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/movement", tags=["movement"])

@router.get("/")
def line_movement_feed(
    sport: str = Query(None),
    min_move: float = Query(0.5),
    hours: int = Query(6),
    db: Session = Depends(get_db),
):
    since = datetime.utcnow() - timedelta(hours=hours)

    snaps = (
        db.query(LineSnapshot)
        .filter(LineSnapshot.timestamp >= since)
        .order_by(LineSnapshot.player_name, LineSnapshot.timestamp.asc())
        .all()
    )

    # Group and find movement
    grouped: dict = {}
    for s in snaps:
        key = f"{s.player_name}||{s.stat_type}||{s.sportsbook}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(s)

    movements = []
    for key, snaps_list in grouped.items():
        if len(snaps_list) < 2:
            continue
        first = snaps_list[0]
        last = snaps_list[-1]
        if first.line is None or last.line is None: continue
        
        move = round(last.line - first.line, 1)

        if abs(move) < min_move:
            continue

        movements.append({
            "player_name": first.player_name,
            "prop_type": first.stat_type,
            "bookmaker": first.sportsbook,
            "open_line": first.line,
            "current_line": last.line,
            "move": move,
            "direction": "down" if move < 0 else "up",
            "is_steam": abs(move) >= 1.5,
            "open_price": first.over_odds,
            "current_price": last.over_odds,
            "first_seen": first.timestamp.isoformat() if first.timestamp else None,
            "last_updated": last.timestamp.isoformat() if last.timestamp else None,
        })

    movements.sort(key=lambda x: abs(x["move"]), reverse=True)
    return {"movements": movements, "total": len(movements)}
