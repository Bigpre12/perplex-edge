from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class LineSnapshot(Base):
    __tablename__ = "line_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, index=True)
    stat_type = Column(String, index=True)
    sportsbook = Column(String, index=True)
    line = Column(Float)
    over_odds = Column(Integer)
    under_odds = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
