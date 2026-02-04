"""SeasonRoster model for tracking player-team-season relationships."""

from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.season import Season
    from app.models.team import Team
    from app.models.player import Player


class SeasonRoster(Base, TimestampMixin):
    """
    SeasonRoster model for tracking which players are on which teams
    for each season.
    
    This allows tracking roster changes across seasons and handles
    mid-season trades by having multiple entries with is_active flags.
    """
    __tablename__ = "season_rosters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # References
    season_id: Mapped[int] = mapped_column(
        ForeignKey("seasons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Player info for this roster entry
    jersey_number: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        comment="Player's jersey number for this team/season",
    )
    
    position: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Player's position for this team/season",
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        comment="Whether player is currently active on this roster",
    )
    
    # Relationships
    season: Mapped["Season"] = relationship(back_populates="rosters")
    team: Mapped["Team"] = relationship(back_populates="season_rosters")
    player: Mapped["Player"] = relationship(back_populates="season_rosters")
    
    # Unique constraint: one entry per player-team-season combination
    __table_args__ = (
        UniqueConstraint('season_id', 'team_id', 'player_id', name='uq_roster_season_team_player'),
    )

    def __repr__(self) -> str:
        return f"<SeasonRoster player_id={self.player_id} team_id={self.team_id} season_id={self.season_id}>"
