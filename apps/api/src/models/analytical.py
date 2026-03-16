from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON
from sqlalchemy.sql import func
from db.base import Base

class WhaleMove(Base):
    __tablename__ = "whale_moves"
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    player_name = Column(String, index=True)
    stat_type = Column(String)
    line = Column(Float)
    move_type = Column(String)    # 'SHARP_SPLIT', 'WHALE_MOVE', etc.
    side = Column(String)         # 'over', 'under'
    amount_estimate = Column(Float, nullable=True) # or severity
    severity = Column(String)     # 'High', 'Moderate', 'Low'
    sportsbook = Column(String, nullable=True)
    books_involved = Column(String) # Comma-separated names
    whale_label = Column(String)  # e.g., 'WHALE', 'SHARP'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SteamEvent(Base):
    __tablename__ = "steam_events"
    
    id = Column(Integer, primary_key=True, index=True)
    sport = Column(String, index=True)
    player_name = Column(String, index=True)
    stat_type = Column(String)
    side = Column(String)
    line = Column(Float)
    movement = Column(Float)
    book_count = Column(Integer)
    severity = Column(Float)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CLVRecord(Base):
    __tablename__ = "clv_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    bet_id = Column(Integer, index=True, nullable=True)
    player_name = Column(String, index=True)
    stat_type = Column(String)
    opening_line = Column(Float)
    closing_line = Column(Float)
    clv = Column(Float)
    clv_label = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HitRateModel(Base):
    __tablename__ = "player_hit_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, index=True)
    stat_type = Column(String, index=True) # e.g. 'points', 'rebounds'
    
    # Hit rates as percentages (0-100)
    l5_hit_rate = Column(Float, default=0.0)
    l10_hit_rate = Column(Float, default=0.0)
    l20_hit_rate = Column(Float, default=0.0)
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class PlayerStats(Base):
    """Historical player stats for H2H and Trend analysis"""
    __tablename__ = "player_stats_v2" # Using v2 to avoid conflicts with old stubs
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    player_name = Column(String, index=True)
    game_date = Column(DateTime(timezone=True), index=True)
    stat_category = Column(String, index=True) # e.g. 'points'
    value = Column(Float)
    opponent_team = Column(String)
    is_home = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

__all__ = ["WhaleMove", "SteamEvent", "CLVRecord", "HitRateModel", "PlayerStats"]
