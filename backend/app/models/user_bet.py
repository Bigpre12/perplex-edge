"""UserBet model for tracking personal betting results."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, String, Float, Integer, Text, Index, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.sport import Sport
    from app.models.game import Game
    from app.models.player import Player
    from app.models.model_pick import ModelPick


class BetStatus(str, enum.Enum):
    """Status of a bet."""
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    PUSH = "push"
    VOID = "void"


class UserBet(Base):
    """
    Tracks personal betting results for ROI and CLV analysis.
    
    Separate from ModelPick/PickResult which track the model's recommendations.
    This tracks what the user actually bet, which may or may not align with
    model picks.
    """
    
    __tablename__ = "user_bets"
    __table_args__ = (
        Index("ix_user_bets_sport", "sport_id"),
        Index("ix_user_bets_game", "game_id"),
        Index("ix_user_bets_player", "player_id"),
        Index("ix_user_bets_status", "status"),
        Index("ix_user_bets_sportsbook", "sportsbook"),
        Index("ix_user_bets_market", "market_type"),
        Index("ix_user_bets_placed_at", "placed_at"),
        Index("ix_user_bets_settled_at", "settled_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # What was bet on
    sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), nullable=False)
    game_id: Mapped[Optional[int]] = mapped_column(ForeignKey("games.id"))
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"))
    
    # Market details
    market_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # e.g., "spread", "total", "moneyline", "player_points", "player_rebounds", etc.
    
    side: Mapped[str] = mapped_column(String(20), nullable=False)
    # e.g., "over", "under", "home", "away"
    
    line_value: Mapped[Optional[float]] = mapped_column(Float)
    # The line at time of bet (e.g., 24.5 for points, -3.5 for spread)
    
    # Sportsbook and odds
    sportsbook: Mapped[str] = mapped_column(String(50), nullable=False)
    # e.g., "FanDuel", "DraftKings", "PrizePicks", "Fliff", "BetMGM", etc.
    
    opening_odds: Mapped[int] = mapped_column(Integer, nullable=False)
    # American odds when bet was placed (e.g., -110, +150)
    
    # Stake
    stake: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    # Amount wagered in units (default 1 unit)
    
    # Status and settlement
    status: Mapped[BetStatus] = mapped_column(
        Enum(BetStatus), 
        default=BetStatus.PENDING,
        nullable=False,
    )
    
    # Result details (populated when settled)
    actual_value: Mapped[Optional[float]] = mapped_column(Float)
    # For props: the actual stat value achieved
    
    # Closing line data (captured at game start for CLV)
    closing_odds: Mapped[Optional[int]] = mapped_column(Integer)
    closing_line: Mapped[Optional[float]] = mapped_column(Float)
    
    # CLV = Closing Line Value in cents
    # Positive = got better odds than market close (good)
    # Negative = got worse odds than market close (bad)
    clv_cents: Mapped[Optional[float]] = mapped_column(Float)
    
    # Profit/Loss after settlement
    # Calculated based on odds and stake
    profit_loss: Mapped[Optional[float]] = mapped_column(Float)
    
    # Timestamps
    placed_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    settled_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Optional user notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Optional link to model pick (if bet was based on a recommendation)
    model_pick_id: Mapped[Optional[int]] = mapped_column(ForeignKey("model_picks.id"))
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    sport: Mapped["Sport"] = relationship()
    game: Mapped[Optional["Game"]] = relationship()
    player: Mapped[Optional["Player"]] = relationship()
    model_pick: Mapped[Optional["ModelPick"]] = relationship()

    def calculate_profit_loss(self) -> Optional[float]:
        """
        Calculate profit/loss based on status and odds.
        
        For a $100 (1 unit) bet:
        - Win with +150 odds: profit = 150
        - Win with -150 odds: profit = 66.67
        - Loss: profit = -100 (stake)
        - Push: profit = 0
        """
        if self.status == BetStatus.PENDING:
            return None
        
        if self.status == BetStatus.PUSH or self.status == BetStatus.VOID:
            return 0.0
        
        stake_amount = self.stake * 100  # Convert units to dollars
        
        if self.status == BetStatus.WON:
            if self.opening_odds >= 100:
                # Positive odds: profit = stake * (odds / 100)
                return stake_amount * (self.opening_odds / 100)
            else:
                # Negative odds: profit = stake * (100 / abs(odds))
                return stake_amount * (100 / abs(self.opening_odds))
        
        elif self.status == BetStatus.LOST:
            return -stake_amount
        
        return None

    def calculate_clv(self) -> Optional[float]:
        """
        Calculate Closing Line Value in cents.
        
        CLV = difference between opening odds and closing odds,
        normalized to "cents" of juice.
        
        Positive CLV = you got better odds than the close (sharp)
        Negative CLV = you got worse odds than the close (bad timing)
        """
        if self.closing_odds is None:
            return None
        
        # Convert American odds to implied probability
        def american_to_prob(odds: int) -> float:
            if odds >= 100:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        
        opening_prob = american_to_prob(self.opening_odds)
        closing_prob = american_to_prob(self.closing_odds)
        
        # CLV in "cents" (percentage points * 100)
        # If your opening odds implied 45% and close was 48%, you got 3 cents of value
        clv = (closing_prob - opening_prob) * 100
        
        # For "over" side, positive CLV is good
        # For "under" side, we need to flip the sign
        if self.side.lower() in ["under", "away", "home_ml_dog"]:
            clv = -clv
        
        return round(clv, 2)

    def __repr__(self) -> str:
        status_str = self.status.value if self.status else "?"
        return (
            f"<UserBet(id={self.id}, {self.market_type} {self.side}, "
            f"line={self.line_value}, odds={self.opening_odds}, "
            f"status={status_str}, P/L={self.profit_loss})>"
        )
