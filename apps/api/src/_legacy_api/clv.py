from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from database import SessionLocal
from models.props import PropLine

router = APIRouter(prefix="/clv", tags=["clv"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def get_clv_history(db: Session = Depends(get_db)):
    """Return historical CLV entries for the dashboard."""
    # Fetch from PropLine where we track CLV
    stmt = select(PropLine).order_by(PropLine.game_time.desc()).limit(100)
    entries = db.execute(stmt).scalars().all()
    
    clv_list = []
    for e in entries:
        clv_list.append({
            "id": str(e.id),
            "player_name": e.player_name,
            "sport": e.sport_key,
            "stat_type": e.stat_type,
            "line": e.line,
            "pick": e.side or "OVER",
            "open_odds": e.odds or -110,
            "close_odds": e.closing_odds or -115,
            "clv": e.clv_percent or 0.0,
            "ev_at_close": (e.clv_percent or 0.0) * 0.8,
            "result": "win" if e.is_win else "loss" if e.is_settled else None,
            "game_time": e.game_time.isoformat() if e.game_time else None
        })
    
    return {"clv": clv_list}

@router.get("/leaderboard")
def clv_leaderboard(db: Session = Depends(get_db)):
    """Return platform-wide CLV stats — public proof of edge."""
    # Fetch all settled props to calculate aggregate beat rate
    stmt = select(PropLine).where(PropLine.is_settled == True)
    settled = db.execute(stmt).scalars().all()

    if not settled:
        return {"beat_closing_line_pct": 0, "total_tracked": 0, "by_sport": []}

    # Calculate overall beat rate
    beat_clv = sum(1 for p in settled if p.beat_closing_line == True)
    total = len(settled)

    # Group by sport
    by_sport_data = {}
    for p in settled:
        sport = p.sport_key or "unknown"
        if sport not in by_sport_data:
            by_sport_data[sport] = {"beat": 0, "total": 0}
        by_sport_data[sport]["total"] += 1
        if p.beat_closing_line == True:
            by_sport_data[sport]["beat"] += 1

    sport_breakdown = [
        {
            "sport": k,
            "beat_clv_pct": round(v["beat"] / v["total"] * 100, 1),
            "total": v["total"]
        }
        for k, v in by_sport_data.items()
    ]

    return {
        "beat_closing_line_pct": round(beat_clv / total * 100, 1),
        "total_tracked": total,
        "by_sport": sorted(sport_breakdown, key=lambda x: x["beat_clv_pct"], reverse=True),
    }
