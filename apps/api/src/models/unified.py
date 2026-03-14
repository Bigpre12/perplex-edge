# apps/api/src/models/unified.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, UniqueConstraint, BigInteger
from sqlalchemy.sql import func
from database import Base

class UnifiedOdds(Base):
    """
    Unified Odds Table: Single source of truth for all markets across all sports.
    """
    __tablename__ = "odds"
    
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, nullable=False, index=True)              # 'basketball_nba'
    league = Column(String, nullable=False)                         # 'NBA'
    event_id = Column(String, nullable=False, index=True)           # external game id
    market_key = Column(String, nullable=False, index=True)         # 'points', 'spread', 'moneyline'
    outcome_key = Column(String, nullable=False)                    # 'over', 'under', 'home', 'away', 'yes', 'no'
    bookmaker = Column(String, nullable=False, index=True)          # 'dk', 'fd', 'kalshi'
    price = Column(Numeric, nullable=False)                         # American or decimal (suggest decimal for easy math)
    implied_prob = Column(Numeric, nullable=False)
    line = Column(Numeric, nullable=True)                           # points/spread/total etc.
    source_ts = Column(DateTime(timezone=True), nullable=False)     # when provider said this was valid
    ingested_ts = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker', name='uix_odds_unique'),
    )

class UnifiedEVSignal(Base):
    """
    Unified EV Signals: Computed betting edges from the EV engine.
    """
    __tablename__ = "ev_signals"
    
    id = Column(BigInteger, primary_key=True)
    sport = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    market_key = Column(String, nullable=False, index=True)
    outcome_key = Column(String, nullable=False)
    bookmaker = Column(String, nullable=False, index=True)
    price = Column(Numeric, nullable=False)
    true_prob = Column(Numeric, nullable=False)
    edge_percent = Column(Numeric, nullable=False)                 # (price_implied - true_prob)*100
    engine_version = Column(String, nullable=False, server_default='v1')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker', 'engine_version', name='uix_ev_unique'),
    )
