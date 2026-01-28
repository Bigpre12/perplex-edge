from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.sport import Sport
    from app.models.team import Team
    from app.models.line import Line
    from app.models.player_game_stats import PlayerGameStats
    from app.models.model_pick import ModelPick


class Game(Base, TimestampMixin):
    """Game model."""
    
    __tablename__ = "games"
    __table_args__ = (
        Index("ix_games_sport_external", "sport_id", "external_game_id", unique=True),
        Index("ix_games_start_time", "start_time"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    external_game_id: Mapped[str] = mapped_column(String(100), nullable=False)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="scheduled")
    # Status values: scheduled, in_progress, final, postponed, cancelled

    # Relationships
    sport: Mapped["Sport"] = relationship(back_populates="games")
    home_team: Mapped["Team"] = relationship(
        back_populates="home_games",
        foreign_keys=[home_team_id],
    )
    away_team: Mapped["Team"] = relationship(
        back_populates="away_games",
        foreign_keys=[away_team_id],
    )
    lines: Mapped[List["Line"]] = relationship(back_populates="game")
    player_stats: Mapped[List["PlayerGameStats"]] = relationship(back_populates="game")
    model_picks: Mapped[List["ModelPick"]] = relationship(back_populates="game")

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, external_id='{self.external_game_id}', status='{self.status}')>"
