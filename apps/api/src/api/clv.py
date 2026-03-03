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
