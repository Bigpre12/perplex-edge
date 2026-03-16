from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db.base import Base

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, unique=True, index=True)
    sport = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    commence_time = Column(DateTime(timezone=True))
    referee_crew = Column(String, nullable=True) # Sprint 17: Comma-separated crew names
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
