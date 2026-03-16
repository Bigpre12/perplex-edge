from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from datetime import datetime, timezone
from db.base import Base

class SavedSystem(Base):
    """
    SavedSystem model - Persistent user-defined filter sets with ROI and performance metrics.
    Allows bettors to track specific systems (e.g., 'NBA Assist Unders') over time.
    """
    __tablename__ = "saved_systems"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    name = Column(String)               # e.g. "NBA Assist Unders"
    filters = Column(JSON)              # {"sport": "NBA", "prop_type": "assists", "pick": "under", "min_hit_rate": 0.65}
    total_bets = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    roi = Column(Float, default=0.0)
    units_profit = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
