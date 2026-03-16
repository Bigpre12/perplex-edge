from fastapi import HTTPException, Depends
from routers.auth import get_current_user
from models.user import User

TIER_RANK = {"free": 0, "pro": 1, "elite": 2}

FEATURE_TIERS = {
    "view_props":         "free",
    "view_all_sports":    "pro",
    "view_ev_badges":     "pro",
    "view_hit_rates":     "pro",
    "parlay_builder":     "pro",
    "bankroll_tracker":   "pro",
    "discord_alerts":     "pro",
    "live_feed":          "pro",
    "arb_finder":         "elite",
    "steam_alerts":       "elite",
    "whale_detector":     "elite",
    "clv_tracker":        "elite",
    "line_movement":      "elite",
    "sharp_book_compare": "elite",
    "oracle_ai":          "elite",
}


def require_feature(feature: str):
    """Dependency — blocks route if user doesn't have access"""
    async def guard(current_user: User = Depends(get_current_user)):
        required = FEATURE_TIERS.get(feature, "elite")
        user_tier = (current_user.subscription_tier or "free").lower()
        if TIER_RANK.get(user_tier, 0) < TIER_RANK.get(required, 99):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "upgrade_required",
                    "required_tier": required,
                    "current_tier": user_tier,
                    "message": f"This feature requires {required} plan",
                    "upgrade_url": "/pricing",
                }
            )
        return current_user
    return guard
