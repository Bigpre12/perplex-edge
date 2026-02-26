from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func
from database import Base

class Contest(Base):
    __tablename__ = "contests"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    entry_fee = Column(Float, default=0.0)
    prize_pool = Column(Float, default=0.0)
    status = Column(String, default="upcoming") # upcoming, active, completed

class ContestEntry(Base):
    __tablename__ = "contestentries"
    
    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    current_score = Column(Float, default=0.0)
    rank = Column(Integer, nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
