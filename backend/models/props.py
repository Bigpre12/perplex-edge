from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Index
from sqlalchemy.sql import func
from database import Base

class PropLine(Base):
    __tablename__ = "proplines"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    player_name = Column(String)
    team = Column(String)
    opponent = Column(String)
    sport_key = Column(String, index=True)
    stat_type = Column(String)
    line = Column(Float)
    
    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class PropOdds(Base):
    __tablename__ = "propodds"
    
    id = Column(Integer, primary_key=True, index=True)
    prop_line_id = Column(Integer) # Foreign key to proplines.id
    sportsbook = Column(String, index=True)
    over_odds = Column(Integer)
    under_odds = Column(Integer)
    
    # Calculated Analytics
    ev_percent = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class LiveGameStat(Base):
    __tablename__ = "livegamestats"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    player_id = Column(String, index=True)
    stats_json = Column(JSON) # Stores real-time accumulators
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
