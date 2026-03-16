from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Index
from sqlalchemy.sql import func
from db.base import Base

class PropLine(Base):
    __tablename__ = "proplines"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(String, index=True)
    player_name = Column(String)
    team = Column(String)
    opponent = Column(String)
    sport_key = Column(String, index=True)
    stat_type = Column(String)
    line = Column(Float)
    game_id = Column(String, index=True, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    
    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    hit_rate_l10 = Column(Integer, default=50) # Sprint 11: Player's L10 hit rate %
    fatigue_flag = Column(String, nullable=True) # Sprint 15: 'B2B', '3-IN-4', etc.
    position = Column(String, nullable=True)     # NBA: 'PG', 'SG', etc.
    sharp_money = Column(Boolean, default=False) # Signal if sharp activity detected
    is_settled = Column(Boolean, default=False)  # Whether the result has been graded
    steam_score = Column(Float, default=0.0)      # Velocity of line movement
    
    # CLV Tracking (Closing Line Value)
    closing_line = Column(Float, nullable=True)
    clv_val = Column(Float, nullable=True)
    beat_closing_line = Column(Boolean, nullable=True)
    
    # Settlement
    hit = Column(Boolean, nullable=True)
    actual_value = Column(Float, nullable=True)

class PropOdds(Base):
    __tablename__ = "propodds"
    
    id = Column(Integer, primary_key=True, index=True)
    prop_line_id = Column(Integer) # Foreign key to proplines.id
    sportsbook = Column(String, index=True)
    over_odds = Column(Integer)
    under_odds = Column(Integer)
    
    # Calculated Analytics
    ev_percent = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class GameLine(Base):
    __tablename__ = "gamelines"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    sport_key = Column(String, index=True)
    home_team = Column(String)
    away_team = Column(String)
    commence_time = Column(DateTime(timezone=True), index=True)
    market_key = Column(String) # h2h, spreads, totals
    
    # Meta
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class GameLineOdds(Base):
    __tablename__ = "gamelineodds"
    
    id = Column(Integer, primary_key=True, index=True)
    game_line_id = Column(Integer) # FK to gamelines.id
    sportsbook = Column(String, index=True)
    
    home_price = Column(Integer, nullable=True) # for h2h/spreads
    away_price = Column(Integer, nullable=True)
    draw_price = Column(Integer, nullable=True)
    
    home_point = Column(Float, nullable=True) # line for spreads
    away_point = Column(Float, nullable=True)
    
    over_price = Column(Integer, nullable=True) # for totals
    under_price = Column(Integer, nullable=True)
    total_line = Column(Float, nullable=True)
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class LiveGameStat(Base):
    __tablename__ = "livegamestats"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, index=True)
    player_id = Column(String, index=True)
    stats_json = Column(JSON) # Stores real-time accumulators
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Market(Base):
    __tablename__ = "markets"
    
    id = Column(Integer, primary_key=True, index=True)
    stat_type = Column(String, index=True)
    description = Column(String)
    sport_id = Column(Integer, index=True)

class Sport(Base):
    __tablename__ = "sports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    key = Column(String, index=True)
    league_code = Column(String, nullable=True)




class Prop(Base):
    __tablename__ = "props"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sport = Column(String, index=True, nullable=False)
    player = Column(String, index=True, nullable=False)
    team = Column(String, index=True, nullable=True)
    market = Column(String, index=True, nullable=False)
    line = Column(Float, nullable=False)
    odds = Column(Integer, nullable=False, default=-110)
    book = Column(String, nullable=False)
    projection = Column(Float, nullable=True)
    edge = Column(Float, nullable=True)
    ev = Column(Float, nullable=True)
    result = Column(String, nullable=True)
    actual = Column(Float, nullable=True)
    is_scored = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Neural Engine Models (SQLModel) ---

class GameV2(SQLModel, table=True):
    __tablename__ = "games_v2"
    id: Optional[int] = Field(default=None, primary_key=True)
    sport: str = Field(index=True)
    commence_time: datetime = Field(sa_column=Column(DateTime(timezone=True), index=True))
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = Field(default="scheduled") # scheduled, live, completed
    
    props: List["PropV2"] = Relationship(back_populates="game")

class PropV2(SQLModel, table=True):
    __tablename__ = "props_v2"
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="games_v2.id", index=True)
    player_name: str = Field(index=True)
    stat_type: str = Field(index=True)  # points, rebounds, etc.
    line: float
    over_price: float
    under_price: float
    sportsbook: str = Field(index=True)
    
    game: GameV2 = Relationship(back_populates="props")
    edges: List["NeuralEdge"] = Relationship(back_populates="prop")
    picks: List["NeuralPick"] = Relationship(back_populates="prop")
