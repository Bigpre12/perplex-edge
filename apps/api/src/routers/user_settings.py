import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["user-settings"])

DEFAULT_SETTINGS: Dict[str, Any] = {
    "unit_size": 100,
    "default_sport": "basketball_nba",
    "default_sportsbook": "draftkings",
    "theme": "dark",
    "notifications_enabled": True,
    "api_enabled": False,
}

ALLOWED_KEYS = set(DEFAULT_SETTINGS.keys())


def _defaults_for_user(user: User) -> Dict[str, Any]:
    return {
        **DEFAULT_SETTINGS,
        "tier": (getattr(user, "subscription_tier", None) or "free").title(),
    }


@router.get("/user/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = str(getattr(current_user, "id", "") or getattr(current_user, "email", ""))
    defaults = _defaults_for_user(current_user)
    try:
        row = (
            await db.execute(
                text("SELECT settings FROM user_settings WHERE user_id = :uid"),
                {"uid": user_id},
            )
        ).mappings().first()
        if not row or not row.get("settings"):
            return defaults

        settings_obj = row["settings"] if isinstance(row["settings"], dict) else {}
        return {**defaults, **settings_obj}
    except Exception as e:
        logger.error("Settings fetch failed for user %s: %s", user_id, e, exc_info=True)
        return {"error": str(e), "defaults": True, **defaults}


@router.patch("/user/settings")
async def patch_user_settings(
    payload: Dict[str, Any] = Body(default_factory=dict),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = str(getattr(current_user, "id", "") or getattr(current_user, "email", ""))
    defaults = _defaults_for_user(current_user)
    updates = {k: v for k, v in payload.items() if k in ALLOWED_KEYS}
    if not updates:
        return defaults

    try:
        row = (
            await db.execute(
                text("SELECT settings FROM user_settings WHERE user_id = :uid"),
                {"uid": user_id},
            )
        ).mappings().first()
        existing = row.get("settings", {}) if row else {}
        existing = existing if isinstance(existing, dict) else {}
        merged = {**existing, **updates}
        merged_json = json.dumps(merged)

        if row:
            await db.execute(
                text(
                    "UPDATE user_settings "
                    "SET settings = CAST(:settings AS jsonb), updated_at = :updated_at "
                    "WHERE user_id = :uid"
                ),
                {"uid": user_id, "settings": merged_json, "updated_at": datetime.now(timezone.utc)},
            )
        else:
            await db.execute(
                text(
                    "INSERT INTO user_settings (user_id, settings, created_at, updated_at) "
                    "VALUES (:uid, CAST(:settings AS jsonb), :created_at, :updated_at)"
                ),
                {
                    "uid": user_id,
                    "settings": merged_json,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                },
            )
        await db.commit()
        return {**defaults, **merged}
    except Exception as e:
        await db.rollback()
        logger.error("Settings update failed for user %s: %s", user_id, e, exc_info=True)
        return {"error": str(e), "defaults": True, **defaults}
