"""Trade and TradeDetail models for tracking NBA trades."""

from datetime import date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Date, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.player import Player
    from app.models.team import Team


class Trade(Base, TimestampMixin):
    """
    Trade model for tracking NBA trades.
    
    Each trade can involve multiple players and assets (picks, cash).
    The details are stored in TradeDetail records.
    """
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Trade identification
    trade_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="Date when trade occurred",
    )
    
    season_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Season year (e.g., 2026 for 2025-26 season)",
    )
    
    # Trade description
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable trade summary",
    )
    
    headline: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Short headline (e.g., 'Harden to Cavaliers')",
    )
    
    # Source tracking
    source_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Link to NBA.com or other source",
    )
    
    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="nba.com",
        comment="Data source (nba.com, espn, manual)",
    )
    
    # Status
    is_applied: Mapped[bool] = mapped_column(
        default=False,
        server_default="false",
        comment="Whether player team_ids have been updated",
    )
    
    # Relationships
    details: Mapped[List["TradeDetail"]] = relationship(
        back_populates="trade",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Trade {self.id}: {self.headline or self.trade_date}>"


class TradeDetail(Base, TimestampMixin):
    """
    TradeDetail model for individual assets in a trade.
    
    Each detail represents one asset (player, pick, or cash) moving
    from one team to another in a trade.
    """
    __tablename__ = "trade_details"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Trade reference
    trade_id: Mapped[int] = mapped_column(
        ForeignKey("trades.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Player reference (optional - only for player assets)
    player_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Team references
    from_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    to_team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Asset details
    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Type of asset: player, pick, cash, rights",
    )
    
    asset_description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Description (e.g., '2027 1st round pick', 'cash considerations')",
    )
    
    # For player assets, store the player name for reference
    player_name: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Player name at time of trade",
    )
    
    # Relationships
    trade: Mapped["Trade"] = relationship(back_populates="details")
    player: Mapped[Optional["Player"]] = relationship()
    from_team: Mapped["Team"] = relationship(foreign_keys=[from_team_id])
    to_team: Mapped["Team"] = relationship(foreign_keys=[to_team_id])

    def __repr__(self) -> str:
        return f"<TradeDetail {self.asset_type}: {self.player_name or self.asset_description}>"
