from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.dashboard import get_dashboard_metrics

router = APIRouter()

@router.get("")
def metrics(db: Session = Depends(get_db)):
    return get_dashboard_metrics(db)

@router.get("/picks-stats")
async def picks_stats():
    """Returns pick statistics for the leaderboard page."""
    return {
        "top_pickers": [],
        "consensus_picks": [],
        "total_active_picks": 0
    }
