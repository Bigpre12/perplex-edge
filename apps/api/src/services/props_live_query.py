"""
Shared time window for props_live reads shown in the product UI.

Excludes far-future schedule noise and very old rows while still allowing NULL
game_start_time when ingest has not attached a start yet.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Tuple

from sqlalchemy import ColumnElement, or_, and_


def props_live_game_time_window(
    game_start_time_col: Any,
    *,
    now: datetime | None = None,
) -> ColumnElement:
    """
    SQLAlchemy predicate: (game_start_time IS NULL) OR (now-6h <= game_start_time <= now+14d).
    """
    now = now or datetime.now(timezone.utc)
    lo = now - timedelta(hours=6)
    hi = now + timedelta(days=14)
    return or_(
        game_start_time_col.is_(None),
        and_(game_start_time_col >= lo, game_start_time_col <= hi),
    )


def props_live_window_params(
    *,
    now: datetime | None = None,
) -> Tuple[datetime, datetime]:
    """Boundaries for raw SQL with :t_lo / :t_hi and NULL OR between."""
    now = now or datetime.now(timezone.utc)
    return (now - timedelta(hours=6), now + timedelta(days=14))


def props_live_window_sql_clause(column: str = "game_start_time") -> str:
    """Parameterized fragment: AND (col IS NULL OR (col >= :t_lo AND col <= :t_hi))."""
    return (
        f" AND ({column} IS NULL OR "
        f"({column} >= :t_lo AND {column} <= :t_hi))"
    )
