"""NCAAB Odds models for live and historical college basketball odds tracking."""

import uuid
from datetime import datetime, date
from typing import Optional

from sqlalchemy import String, Float, Date, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class LiveOddsNCAAB(Base, TimestampMixin):
    """
    Live NCAAB odds from OddsAPI/BetStack.
    
    Stores current odds for upcoming college basketball games.
    Updated hourly via scheduled sync.
    """
    
    __tablename__ = "live_odds_ncaab"
    __table_args__ = (
        Index("ix_live_odds_ncaab_game", "game_id"),
        Index("ix_live_odds_ncaab_season", "season"),
        Index("ix_live_odds_ncaab_bookmaker", "bookmaker"),
        Index("ix_live_odds_ncaab_teams", "home_team", "away_team"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    sport: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NCAAB",
        server_default="NCAAB",
    )
    game_id: Mapped[str] = mapped_column(String(100), nullable=False)
    home_team: Mapped[str] = mapped_column(String(100), nullable=False)
    away_team: Mapped[str] = mapped_column(String(100), nullable=False)
    home_odds: Mapped[float] = mapped_column(Float, nullable=False)
    away_odds: Mapped[float] = mapped_column(Float, nullable=False)
    draw_odds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bookmaker: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
    )
    season: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "2025-2026"

    def __repr__(self) -> str:
        return f"<LiveOddsNCAAB({self.home_team} vs {self.away_team}, {self.season})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "sport": self.sport,
            "game_id": self.game_id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_odds": self.home_odds,
            "away_odds": self.away_odds,
            "draw_odds": self.draw_odds,
            "bookmaker": self.bookmaker,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "season": self.season,
        }


class HistoricalOddsNCAAB(Base, TimestampMixin):
    """
    Historical NCAAB odds snapshots.
    
    Daily snapshots of odds for tracking line movements
    and calculating hit rates after games complete.
    """
    
    __tablename__ = "historical_odds_ncaab"
    __table_args__ = (
        Index("ix_historical_odds_ncaab_game", "game_id"),
        Index("ix_historical_odds_ncaab_season", "season"),
        Index("ix_historical_odds_ncaab_bookmaker", "bookmaker"),
        Index("ix_historical_odds_ncaab_snapshot", "snapshot_date"),
        Index("ix_historical_odds_ncaab_result", "result"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    sport: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NCAAB",
        server_default="NCAAB",
    )
    game_id: Mapped[str] = mapped_column(String(100), nullable=False)
    home_team: Mapped[str] = mapped_column(String(100), nullable=False)
    away_team: Mapped[str] = mapped_column(String(100), nullable=False)
    home_odds: Mapped[float] = mapped_column(Float, nullable=False)
    away_odds: Mapped[float] = mapped_column(Float, nullable=False)
    draw_odds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bookmaker: Mapped[str] = mapped_column(String(50), nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    result: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )  # 'home', 'away', or None if game not played yet
    season: Mapped[str] = mapped_column(String(20), nullable=False)  # e.g., "2025-2026"

    def __repr__(self) -> str:
        return f"<HistoricalOddsNCAAB({self.home_team} vs {self.away_team}, {self.snapshot_date})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "sport": self.sport,
            "game_id": self.game_id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "home_odds": self.home_odds,
            "away_odds": self.away_odds,
            "draw_odds": self.draw_odds,
            "bookmaker": self.bookmaker,
            "snapshot_date": self.snapshot_date.isoformat() if self.snapshot_date else None,
            "result": self.result,
            "season": self.season,
        }
    
    @property
    def favorite(self) -> str:
        """Determine the favorite based on odds (lower odds = favorite)."""
        if self.home_odds < self.away_odds:
            return "home"
        elif self.away_odds < self.home_odds:
            return "away"
        return "even"
    
    @property
    def favorite_won(self) -> Optional[bool]:
        """Check if the favorite won (for hit rate calculation)."""
        if not self.result:
            return None
        return self.result == self.favorite
