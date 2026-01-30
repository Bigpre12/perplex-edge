"""SyncMetadata model for tracking data freshness and sync status."""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SyncMetadata(Base):
    """
    Tracks the last successful sync for each sport and data type.
    
    Used to:
    - Display "Last updated: X" in the frontend
    - Detect stale data (sync failures)
    - Monitor sync job health
    """
    
    __tablename__ = "sync_metadata"
    __table_args__ = (
        Index("ix_sync_metadata_sport_type", "sport_key", "data_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Sport identifier (e.g., "basketball_nba", "americanfootball_nfl")
    sport_key: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Data type (e.g., "games", "lines", "props", "injuries", "rosters")
    data_type: Mapped[str] = mapped_column(String(30), nullable=False)
    
    # Last successful sync timestamp
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
    )
    
    # Counts from the last sync
    games_count: Mapped[Optional[int]] = mapped_column(Integer)
    lines_count: Mapped[Optional[int]] = mapped_column(Integer)
    props_count: Mapped[Optional[int]] = mapped_column(Integer)
    picks_count: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Data source used (e.g., "odds_api", "espn", "stubs")
    source: Mapped[Optional[str]] = mapped_column(String(30))
    
    # Sync duration in seconds
    sync_duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    
    # Error message if sync partially failed
    error_message: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Whether the sync was considered healthy
    is_healthy: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return (
            f"<SyncMetadata(sport='{self.sport_key}', type='{self.data_type}', "
            f"updated={self.last_updated}, healthy={self.is_healthy})>"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "sport_key": self.sport_key,
            "data_type": self.data_type,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "games_count": self.games_count,
            "lines_count": self.lines_count,
            "props_count": self.props_count,
            "picks_count": self.picks_count,
            "source": self.source,
            "sync_duration_seconds": self.sync_duration_seconds,
            "is_healthy": self.is_healthy,
            "error_message": self.error_message,
        }
