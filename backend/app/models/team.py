from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.sport import Sport
    from app.models.player import Player
    from app.models.game import Game


class Team(Base, TimestampMixin):
    """Team model."""
    
    __tablename__ = "teams"
    __table_args__ = (
        Index("ix_teams_sport_external", "sport_id", "external_team_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    external_team_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    abbreviation: Mapped[Optional[str]] = mapped_column(String(10))

    # Relationships
    sport: Mapped["Sport"] = relationship(back_populates="teams")
    players: Mapped[List["Player"]] = relationship(back_populates="team")
    home_games: Mapped[List["Game"]] = relationship(
        back_populates="home_team",
        foreign_keys="Game.home_team_id",
    )
    away_games: Mapped[List["Game"]] = relationship(
        back_populates="away_team",
        foreign_keys="Game.away_team_id",
    )

    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', abbreviation='{self.abbreviation}')>"
