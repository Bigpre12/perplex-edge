from sqlalchemy import func
from sqlalchemy.orm import Session
from models.prop import Prop
from models.line_move import LineMove
from models.injury import Injury

def get_dashboard_metrics(db: Session):
    props_scored = db.query(func.count(Prop.id)).filter(Prop.is_scored.is_(True)).scalar() or 0
    sharp_signals = db.query(func.count(LineMove.id)).scalar() or 0
    injury_count = db.query(func.count(Injury.id)).scalar() or 0

    return {
        "status": "ok",
        "counts": {
            "props_scored": props_scored,
            "sharp_signals": sharp_signals,
            "injuries": injury_count,
        },
        "services": {
            "db": "healthy",
            "cache": "healthy",
            "odds_feed": "healthy",
        }
    }
