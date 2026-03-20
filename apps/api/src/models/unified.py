# apps/api/src/models/unified.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, UniqueConstraint, BigInteger
from sqlalchemy.sql import func
from db.base import Base

class UnifiedOdds(Base):
    """
    Unified Odds Table: Single source of truth for all markets across all sports.
    """
    __tablename__ = "odds"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport = Column(String, nullable=False, index=True)              # 'basketball_nba'
    league = Column(String, nullable=False)                         # 'NBA'
    event_id = Column(String, nullable=False, index=True)           # external game id
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    game_time = Column(DateTime(timezone=True), nullable=True)
    market_key = Column(String, nullable=False, index=True)         # 'points', 'spread', 'moneyline'
    outcome_key = Column(String, nullable=False)                    # 'over', 'under', 'home', 'away', 'yes', 'no'
    player_name = Column(String, nullable=True, index=True)
    bookmaker = Column(String, nullable=False, index=True)          # 'dk', 'fd', 'kalshi'
    price = Column(Numeric, nullable=False)                         # American or decimal
    line = Column(Numeric, nullable=True)                           # points/spread/total etc.
    implied_prob = Column(Numeric, nullable=False)
    source_ts = Column(DateTime(timezone=True), nullable=False)     # when provider said this was valid
    ingested_ts = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker', 'player_name', name='uix_odds_unique'),
    )

class UnifiedEVSignal(Base):
    """
    Unified EV Signals: Computed betting edges from the EV engine.
    """
    __tablename__ = "ev_signals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    market_key = Column(String, nullable=False, index=True)
    outcome_key = Column(String, nullable=False)
    player_name = Column(String, nullable=True)
    bookmaker = Column(String, nullable=False, index=True)
    price = Column(Numeric, nullable=False)
    line = Column(Numeric, nullable=True)
    true_prob = Column(Numeric, nullable=False)
    edge_percent = Column(Numeric, nullable=False)                 # (price_implied - true_prob)*100
    implied_prob = Column(Numeric, nullable=False)
    engine_version = Column(String, nullable=False, server_default='v1')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('sport', 'event_id', 'market_key', 'outcome_key', 'bookmaker', 'engine_version', name='uix_ev_unique'),
    )

class LineTick(Base):
    """
    Line Ticks: Historical record of price/line changes for movement analysis.
    """
    __tablename__ = "line_ticks"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sport = Column(String, nullable=False, index=True)
    event_id = Column(String, nullable=False, index=True)
    market_key = Column(String, nullable=False, index=True)
    outcome_key = Column(String, nullable=False)
    player_name = Column(String, nullable=True, index=True)
    bookmaker = Column(String, nullable=False, index=True)
    price = Column(Numeric, nullable=False)
    line = Column(Numeric, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
