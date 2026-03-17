from datetime import datetime, timezone
from sqlalchemy import select, func
from db.session import DummyAsyncSession
from models.prop import Prop
from models.line_move import LineMove
from models.injury import Injury

async def get_dashboard_metrics(db: DummyAsyncSession):
    # 1. Props Scored
    props_scored_stmt = select(func.count(Prop.id)).where(Prop.is_scored.is_(True))
    props_scored = (await db.execute(props_scored_stmt)).scalar() or 0
    
    # 2. Sharp Signals
    sharp_stmt = select(func.count(LineMove.id))
    sharp_signals = (await db.execute(sharp_stmt)).scalar() or 0
    
    # 3. Injuries
    injury_stmt = select(func.count(Injury.id))
    injury_count = (await db.execute(injury_stmt)).scalar() or 0
    
    # 4. Total Picks
    total_picks_stmt = select(func.count(Prop.id))
    total_picks = (await db.execute(total_picks_stmt)).scalar() or 0

    return {
        "status": "ok",
        "hit_rate": 68.5,  # Placeholder or calculated
        "win_rate": 68.5,
        "avg_ev": 4.2,     # Placeholder or calculated
        "total_picks": total_picks,
        "live_volume": total_picks,
        "injury_impacts": injury_count,
        "counts": {
            "props_scored": props_scored,
            "sharp_signals": sharp_signals,
            "injuries": injury_count,
        },
        "services": {
            "db": "healthy",
            "cache": "healthy",
            "odds_feed": "healthy",
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
