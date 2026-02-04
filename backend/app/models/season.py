"""Season model for tracking sports seasons."""

from datetime import date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, String, Date, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.sport import Sport
    from app.models.game import Game
    from app.models.season_roster import SeasonRoster


class Season(Base, TimestampMixin):
    """
    Season model for tracking sports seasons.
    
    Each sport can have multiple seasons (e.g., NBA 2025-26, NFL 2026).
    Seasons have a year identifier and date range.
    """
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Sport reference
    sport_id: Mapped[int] = mapped_column(
        ForeignKey("sports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Season identification
    season_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Primary year of the season (e.g., 2026 for 2025-26 or 2026)",
    )
    
    label: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Display label (e.g., '2025-26' for NBA, '2026' for NFL)",
    )
    
    # Date range
    start_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Season start date",
    )
    
    end_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        comment="Season end date",
    )
    
    # Status
    is_current: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        comment="Whether this is the current active season for the sport",
    )
    
    # Relationships
    sport: Mapped["Sport"] = relationship(back_populates="seasons")
    games: Mapped[List["Game"]] = relationship(back_populates="season")
    rosters: Mapped[List["SeasonRoster"]] = relationship(back_populates="season")
    
    # Unique constraint: one season per year per sport
    __table_args__ = (
        UniqueConstraint('sport_id', 'season_year', name='uq_season_sport_year'),
    )

    def __repr__(self) -> str:
        return f"<Season {self.label} (sport_id={self.sport_id})>"
