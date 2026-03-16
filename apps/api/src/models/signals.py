# apps/api/src/models/signals.py
from sqlalchemy import Column, String, Numeric, DateTime, BigInteger, JSON
from sqlalchemy.sql import func
from db.base import Base

class Signal(Base):
    """
    Sharp, Steam, Whale, and RLM signals.
    """
    __tablename__ = "signals"
    
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    signal_type = Column(String, nullable=False, index=True)  # 'steam', 'sharp', 'whale', 'rlm', 'clv'
    market_key = Column(String, nullable=False)
    outcome_key = Column(String, nullable=False)
    player_name = Column(String, nullable=True, index=True)
    book_origin = Column(String, nullable=True)
    line_open = Column(Numeric, nullable=True)
    line_current = Column(Numeric, nullable=True)
    line_delta = Column(Numeric, nullable=True)
    sharp_pct = Column(Numeric, nullable=True)
    public_pct = Column(Numeric, nullable=True)
    confidence = Column(Numeric, nullable=True)
    detail = Column(JSON, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

class InjuryImpact(Base):
    """
    Quantified impact of player injuries.
    """
    __tablename__ = "injury_impacts"
    
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, index=True)
    player_name = Column(String, index=True)
    team = Column(String)
    status = Column(String) # 'Out', 'Questionable'
    impact_description = Column(String)
    affected_markets = Column(JSON) # e.g. [{"market": "points", "adjustment": -2.5}]
    teammate_boosts = Column(JSON) # e.g. [{"player": "Teammate A", "boost": 0.15}]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class LinePrediction(Base):
    """
    Predicted line movements.
    """
    __tablename__ = "line_predictions"
    
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, index=True)
    event_id = Column(String, index=True)
    market_key = Column(String)
    current_line = Column(Numeric)
    predicted_line = Column(Numeric)
    confidence = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
