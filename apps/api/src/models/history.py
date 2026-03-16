# apps/api/src/models/history.py
from sqlalchemy import Column, String, Numeric, DateTime, BigInteger
from sqlalchemy.sql import func
from db.base import Base

class OddsHistory(Base):
    """
    Historical odds for line movement tracking.
    """
    __tablename__ = "odds_history"
    
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, nullable=False)
    event_id = Column(String, nullable=False, index=True)
    market_key = Column(String, nullable=False, index=True)
    outcome_key = Column(String, nullable=False)
    bookmaker = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    line = Column(Numeric, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class PropHistory(Base):
    """Legacy prop history tracking."""
    __tablename__ = "prop_history"
    id = Column(BigInteger, primary_key=True)
    prop_id = Column(String, nullable=False)
    price = Column(Numeric, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
