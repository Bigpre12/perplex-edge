"""Plan-based feature limits configuration."""

from dataclasses import dataclass
from typing import Optional

from app.models.user import User, UserPlan


# =============================================================================
# Plan Limits Configuration
# =============================================================================

@dataclass
class PlanLimits:
    """Feature limits for a subscription plan."""
    
    # Sports access
    allowed_sports: list[int] | str  # List of sport IDs or "all"
    
    # Props limits
    daily_props_limit: Optional[int]  # None = unlimited
    
    # Features
    stats_filters: bool  # Can use market/side filters in Stats
    stats_hot_cold: bool  # Can see Hot/Cold players
    stats_streaks: bool  # Can see streaks
    parlay_max_legs: Optional[int]  # None = unlimited
    
    # Premium features
    live_ev: bool
    alt_lines: bool
    watchlists: bool
    backtest: bool
    analytics: bool
    model_performance: bool
    my_edge: bool
    export_data: bool


# Sport IDs
SPORT_NBA = 30
SPORT_NFL = 31
SPORT_NCAAB = 32
SPORT_MLB = 40
SPORT_NCAAF = 41
SPORT_ATP = 42
SPORT_WTA = 43
SPORT_NHL = 53

FREE_SPORTS = [SPORT_NBA, SPORT_NFL]
ALL_SPORTS = [SPORT_NBA, SPORT_NFL, SPORT_NCAAB, SPORT_MLB, SPORT_NCAAF, SPORT_ATP, SPORT_WTA, SPORT_NHL]


# =============================================================================
# Plan Definitions
# =============================================================================

PLAN_LIMITS: dict[str, PlanLimits] = {
    UserPlan.FREE.value: PlanLimits(
        # Limited sports
        allowed_sports=FREE_SPORTS,
        
        # Limited props per day
        daily_props_limit=10,
        
        # Basic stats only
        stats_filters=False,
        stats_hot_cold=True,  # Can see summary
        stats_streaks=True,
        parlay_max_legs=3,
        
        # No premium features
        live_ev=False,
        alt_lines=False,
        watchlists=False,
        backtest=False,
        analytics=False,
        model_performance=False,
        my_edge=False,
        export_data=False,
    ),
    
    UserPlan.TRIAL.value: PlanLimits(
        # Full sports access
        allowed_sports="all",
        
        # Unlimited props
        daily_props_limit=None,
        
        # Full stats
        stats_filters=True,
        stats_hot_cold=True,
        stats_streaks=True,
        parlay_max_legs=None,
        
        # All premium features
        live_ev=True,
        alt_lines=True,
        watchlists=True,
        backtest=True,
        analytics=True,
        model_performance=True,
        my_edge=True,
        export_data=True,
    ),
    
    UserPlan.PRO.value: PlanLimits(
        # Full sports access
        allowed_sports="all",
        
        # Unlimited props
        daily_props_limit=None,
        
        # Full stats
        stats_filters=True,
        stats_hot_cold=True,
        stats_streaks=True,
        parlay_max_legs=None,
        
        # All premium features
        live_ev=True,
        alt_lines=True,
        watchlists=True,
        backtest=True,
        analytics=True,
        model_performance=True,
        my_edge=True,
        export_data=True,
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_plan_limits(user: Optional[User]) -> PlanLimits:
    """
    Get plan limits for a user.
    
    Anonymous users get free tier limits.
    """
    if user is None:
        return PLAN_LIMITS[UserPlan.FREE.value]
    
    # Active trial counts as pro
    if user.is_trial:
        return PLAN_LIMITS[UserPlan.PRO.value]
    
    return PLAN_LIMITS.get(user.plan, PLAN_LIMITS[UserPlan.FREE.value])


def get_allowed_sports(user: Optional[User]) -> list[int]:
    """Get list of sport IDs the user can access."""
    limits = get_plan_limits(user)
    
    if limits.allowed_sports == "all":
        return ALL_SPORTS
    
    return limits.allowed_sports


def can_access_sport(user: Optional[User], sport_id: int) -> bool:
    """Check if user can access a specific sport."""
    allowed = get_allowed_sports(user)
    return sport_id in allowed


def check_daily_props_limit(user: Optional[User]) -> tuple[bool, int, Optional[int]]:
    """
    Check if user has hit their daily props limit.
    
    Returns:
        (can_view_more, viewed_today, limit)
    """
    limits = get_plan_limits(user)
    
    if limits.daily_props_limit is None:
        return (True, 0, None)
    
    if user is None:
        # Anonymous users: simple limit
        return (True, 0, limits.daily_props_limit)
    
    viewed = user.props_viewed_today or 0
    can_view = viewed < limits.daily_props_limit
    
    return (can_view, viewed, limits.daily_props_limit)


def can_use_feature(user: Optional[User], feature: str) -> bool:
    """
    Check if user can use a specific feature.
    
    Features: live_ev, alt_lines, watchlists, backtest, analytics,
              model_performance, my_edge, export_data, stats_filters
    """
    limits = get_plan_limits(user)
    return getattr(limits, feature, False)


# =============================================================================
# Response Helpers
# =============================================================================

def get_plan_info_response(user: Optional[User]) -> dict:
    """
    Get plan info for API response.
    
    Useful for frontend to know what features are available.
    """
    limits = get_plan_limits(user)
    can_view, viewed, limit = check_daily_props_limit(user)
    
    return {
        "plan": user.plan if user else "free",
        "is_pro": user.is_pro if user else False,
        "is_trial": user.is_trial if user else False,
        "trial_days_left": user.trial_days_left if user else None,
        "allowed_sports": get_allowed_sports(user),
        "daily_props_limit": limit,
        "props_viewed_today": viewed,
        "can_view_more_props": can_view,
        "features": {
            "live_ev": limits.live_ev,
            "alt_lines": limits.alt_lines,
            "watchlists": limits.watchlists,
            "backtest": limits.backtest,
            "analytics": limits.analytics,
            "model_performance": limits.model_performance,
            "my_edge": limits.my_edge,
            "stats_filters": limits.stats_filters,
            "export_data": limits.export_data,
        },
    }
