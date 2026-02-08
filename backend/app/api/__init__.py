from fastapi import APIRouter

from app.api import games, odds, props, injuries, picks, sync, admin, public, stats

api_router = APIRouter()

# Public API (consumer-facing endpoints)
api_router.include_router(public.router, prefix="", tags=["public"])

# Internal/detailed API endpoints
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(odds.router, prefix="/odds", tags=["odds"])
api_router.include_router(props.router, prefix="/props", tags=["props"])
api_router.include_router(injuries.router, prefix="/injuries", tags=["injuries"])
api_router.include_router(picks.router, prefix="/picks", tags=["picks"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
