from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class RefereeGame(Base):
    __tablename__ = "refereegames"
    
    id = Column(Integer, primary_key=True, index=True)
    ref_name = Column(String, index=True)
    game_id = Column(String, index=True)
    total_fouls = Column(Integer, default=0)
    pace = Column(Float, default=0.0)
    total_points = Column(Integer, default=0)
    fta = Column(Integer, default=0) # Free Throw Attempts
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
