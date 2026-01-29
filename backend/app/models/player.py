from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import ForeignKey, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.sport import Sport
    from app.models.team import Team
    from app.models.line import Line
    from app.models.injury import Injury
    from app.models.player_game_stats import PlayerGameStats
    from app.models.model_pick import ModelPick
    from app.models.pick_result import PickResult
    from app.models.player_hit_rate import PlayerHitRate


class Player(Base, TimestampMixin):
    """Player model."""
    
    __tablename__ = "players"
    __table_args__ = (
        Index("ix_players_sport_external", "sport_id", "external_player_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))
    external_player_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[Optional[str]] = mapped_column(String(20))

    # Relationships
    sport: Mapped["Sport"] = relationship(back_populates="players")
    team: Mapped[Optional["Team"]] = relationship(back_populates="players")
    lines: Mapped[List["Line"]] = relationship(back_populates="player")
    injuries: Mapped[List["Injury"]] = relationship(back_populates="player")
    game_stats: Mapped[List["PlayerGameStats"]] = relationship(back_populates="player")
    model_picks: Mapped[List["ModelPick"]] = relationship(back_populates="player")
    pick_results: Mapped[List["PickResult"]] = relationship(back_populates="player")
    hit_rate_stats: Mapped[Optional["PlayerHitRate"]] = relationship(back_populates="player", uselist=False)

    def __repr__(self) -> str:
        return f"<Player(id={self.id}, name='{self.name}', position='{self.position}')>"
