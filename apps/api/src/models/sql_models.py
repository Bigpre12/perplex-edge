from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, String, DateTime, func

class Game(SQLModel, table=True):
    __tablename__ = "games_v2"
    id: Optional[int] = Field(default=None, primary_key=True)
    sport: str = Field(index=True)
    commence_time: datetime = Field(sa_column=Column(DateTime(timezone=True), index=True))
    home_team: str
    away_team: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = Field(default="scheduled") # scheduled, live, completed
    
    props: List["Prop"] = Relationship(back_populates="game")

class Prop(SQLModel, table=True):
    __tablename__ = "props_v2"
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="games_v2.id", index=True)
    player_name: str = Field(index=True)
    stat_type: str = Field(index=True)  # points, rebounds, etc.
    line: float
    over_price: float
    under_price: float
    sportsbook: str = Field(index=True)
    
    game: Game = Relationship(back_populates="props")
    edges: List["Edge"] = Relationship(back_populates="prop")
    picks: List["Pick"] = Relationship(back_populates="prop")

class Edge(SQLModel, table=True):
    __tablename__ = "edges_v2"
    id: Optional[int] = Field(default=None, primary_key=True)
    prop_id: int = Field(foreign_key="props_v2.id", index=True)
    ev: float = Field(index=True)  # expected value
    hit_rate: float = Field(index=True)  # % success
    model_confidence: float = Field(default=0.0)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    
    prop: Prop = Relationship(back_populates="edges")

class Pick(SQLModel, table=True):
    __tablename__ = "user_picks_v2"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    prop_id: int = Field(foreign_key="props_v2.id", index=True)
    side: str  # over/under
    stake: float
    odds: int
    is_hit: Optional[bool] = None
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    
    prop: Prop = Relationship(back_populates="picks")
