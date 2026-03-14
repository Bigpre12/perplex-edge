from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from database import Base

class BetResult(str, enum.Enum):
    pending = "pending"
    win = "win"
    loss = "loss"
    push = "push"

class BetSlip(Base):
    __tablename__ = "betslips"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    slip_type = Column(String) # 'straight', 'parlay', 'sgp'
    sportsbook = Column(String)
    total_odds = Column(Integer)
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="pending")
    
    legs = relationship("BetLeg", back_populates="slip")

class BetLeg(Base):
    """Individual legs within a betslip, used for CLV tracking"""
    __tablename__ = "betlegs"
    
    id = Column(Integer, primary_key=True, index=True)
    slip_id = Column(Integer, ForeignKey("betslips.id"), index=True)
    prop_id = Column(Integer) # Foreign Key to PropLine
    side = Column(String) # 'over', 'under'
    odds_taken = Column(Integer)
    line_taken = Column(Float)
    
    # Closing Line Value Analytics
    closing_odds = Column(Integer, nullable=True)
    closing_line = Column(Float, nullable=True)
    clv = Column(Float, nullable=True)
    clv_label = Column(String, nullable=True)
    clv_percent = Column(Float, nullable=True)
    
    slip = relationship("BetSlip", back_populates="legs")

class BetLog(Base):
    """Rich bet record for performance and history"""
    __tablename__ = "bet_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    player_name = Column(String)
    prop_type = Column(String)
    line = Column(Float)
    side = Column(String)        # over/under
    odds = Column(Integer)
    stake = Column(Float, default=1.0)
    bookmaker = Column(String)
    result = Column(SQLEnum(BetResult), default=BetResult.pending)
    profit_loss = Column(Float, default=0.0)
    clv = Column(Float, nullable=True)
    sport = Column(String)
    notes = Column(String, nullable=True)
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    settled_at = Column(DateTime(timezone=True), nullable=True)
