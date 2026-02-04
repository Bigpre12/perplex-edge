"""User model for authentication and subscription management."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class UserPlan(str, Enum):
    """User subscription plan types."""
    FREE = "free"
    TRIAL = "trial"
    PRO = "pro"


class User(Base, TimestampMixin):
    """
    User model for managing authentication and subscriptions.
    
    The id is the Clerk user ID, which is used as the primary key
    to sync with Clerk authentication.
    """
    __tablename__ = "users"

    # Clerk user ID as primary key
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    
    # User info
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Subscription info
    plan: Mapped[str] = mapped_column(
        String(20),
        default=UserPlan.FREE.value,
        server_default=UserPlan.FREE.value,
    )
    
    # Trial tracking
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    # Whop subscription tracking
    whop_membership_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    
    # Usage tracking for rate limiting
    props_viewed_today: Mapped[int] = mapped_column(default=0, server_default="0")
    props_reset_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.plan})>"
    
    @property
    def is_pro(self) -> bool:
        """Check if user has pro access (paid or active trial)."""
        if self.plan == UserPlan.PRO.value:
            return True
        if self.plan == UserPlan.TRIAL.value and self.trial_ends_at:
            return datetime.now(self.trial_ends_at.tzinfo) < self.trial_ends_at
        return False
    
    @property
    def is_trial(self) -> bool:
        """Check if user is on an active trial."""
        if self.plan != UserPlan.TRIAL.value:
            return False
        if not self.trial_ends_at:
            return False
        return datetime.now(self.trial_ends_at.tzinfo) < self.trial_ends_at
    
    @property
    def trial_days_left(self) -> Optional[int]:
        """Calculate days remaining in trial."""
        if not self.trial_ends_at or self.plan != UserPlan.TRIAL.value:
            return None
        delta = self.trial_ends_at - datetime.now(self.trial_ends_at.tzinfo)
        return max(0, delta.days)
