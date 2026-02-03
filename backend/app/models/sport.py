from typing import TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.team import Team
    from app.models.player import Player
    from app.models.game import Game
    from app.models.market import Market
    from app.models.injury import Injury
    from app.models.model_pick import ModelPick
    from app.models.player_hit_rate import PlayerHitRate
    from app.models.player_market_hit_rate import PlayerMarketHitRate


class Sport(Base, TimestampMixin):
    """Sport model (e.g., NBA, NFL, MLB)."""
    
    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    league_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relationships
    teams: Mapped[List["Team"]] = relationship(back_populates="sport")
    players: Mapped[List["Player"]] = relationship(back_populates="sport")
    games: Mapped[List["Game"]] = relationship(back_populates="sport")
    markets: Mapped[List["Market"]] = relationship(back_populates="sport")
    injuries: Mapped[List["Injury"]] = relationship(back_populates="sport")
    model_picks: Mapped[List["ModelPick"]] = relationship(back_populates="sport")
    player_hit_rates: Mapped[List["PlayerHitRate"]] = relationship(back_populates="sport")
    player_market_hit_rates: Mapped[List["PlayerMarketHitRate"]] = relationship(back_populates="sport")

    def __repr__(self) -> str:
        return f"<Sport(id={self.id}, name='{self.name}', league_code='{self.league_code}', key='{self.key}')>"
