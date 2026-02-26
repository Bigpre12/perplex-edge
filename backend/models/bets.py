from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from database import Base

class BetSlip(Base):
    __tablename__ = "betslips"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True) # Foreign key to User
    slip_type = Column(String) # 'straight', 'parlay', 'sgp'
    sportsbook = Column(String)
    total_odds = Column(Integer)
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending") # 'pending', 'won', 'lost', 'void'
    
class BetLog(Base):
    """Individual legs within a betslip, used for CLV tracking"""
    __tablename__ = "betlogs"
    
    id = Column(Integer, primary_key=True, index=True)
    slip_id = Column(Integer, index=True) # Foreign Key to BetSlip
    prop_id = Column(Integer) # Foreign Key to PropLine
    side = Column(String) # 'over', 'under'
    odds_taken = Column(Integer)
    line_taken = Column(Float)
    
    # Closing Line Value Analytics
    closing_odds = Column(Integer, nullable=True)
    closing_line = Column(Float, nullable=True)
    clv_percent = Column(Float, nullable=True)
