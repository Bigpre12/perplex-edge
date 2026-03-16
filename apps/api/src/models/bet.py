from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Enum as SQLEnum, Column as SAColumn, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from db.base import Base

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
class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    player = Column(String, index=True, nullable=False)
    market = Column(String, nullable=False)
    pick = Column(String, nullable=False)
    line = Column(Float, nullable=False)
    odds = Column(Integer, nullable=False)
    stake = Column(Float, nullable=False)
    status = Column(String, default="open", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Neural Engine Models (SQLModel) ---

class NeuralPick(SQLModel, table=True):
    __tablename__ = "user_picks_v2"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    prop_id: int = Field(foreign_key="props_v2.id", index=True)
    side: str  # over/under
    stake: float
    odds: int
    is_hit: Optional[bool] = None
    created_at: datetime = Field(sa_column=SAColumn(DateTime(timezone=True), server_default=func.now()))
    
    prop: "PropV2" = Relationship(back_populates="picks")
