"""
Main FastAPI application for the sports betting system
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()
from api.immediate_working import router
from api.validation_endpoints import router as validation_router
from api.track_record_endpoints import router as track_record_router
from api.model_status_endpoints import router as model_status_router
from api.working_parlays import router as working_parlays_router
from api.picks import router as picks_router
from api.analysis import router as analysis_v2_router
from routers.deeplinks import router as deeplinks_router
from routers.splits import router as splits_router
from routers.alt_lines import router as alt_lines_router
from routers.injuries import router as injuries_router
from routers.middle_boost import router as middle_boost_router
from routers.dvp import router as dvp_router
from api.share import router as share_router
from routers import auth_router, ledger_router

# Newly Added Routers (Audit Phase 2)
from routers.ai_assistant import router as ai_assistant_router
from routers.api_tier_router import router as api_tier_router
from routers.autocopy_router import router as autocopy_router
from routers.hedge_router import router as hedge_router
from routers.kalshi_router import router as kalshi_router
from routers.kelly_router import router as kelly_router
from routers.live_router import router as live_router
from routers.referral_router import router as referral_router
from routers.sgp_router import router as sgp_router
from routers.social_router import router as social_router
from routers.reporting_router import router as reporting_router
from routers.execution_router import router as execution_router
from routers.backtest_router import router as backtest_router

from ml.prop_predictor import router as prop_predictor_router
from routers.user_profile_router import router as user_profile_router

from routers import (
    contest_router, prop_router, shop_router, feed_router, 
    ml_router, analytics_router, whale_router,
    auth_router, push_router, web_push, admin_router, config_router,
    stripe_router, chat_router, affiliate_router,
    live_odds_socket
)

from routers.live_odds_socket import live_odds_broadcaster

from jobs.email_cron import start_email_cron

from services.cache import cache

import asyncio
from services.live_game_tracker import live_sync_loop
from services.discord_bot import daily_digest_loop
from services.ledger_service import ledger_service
from database import get_async_db, async_session_maker

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

async def weekly_reporting_loop():
    """Background task for weekly reports."""
    import logging
    logger = logging.getLogger("weekly_report")
    while True:
        try:
            logger.info("Weekly reporting cycle — no action taken (stub).")
        except Exception as e:
            logger.error(f"Weekly reporting error: {e}")
        await asyncio.sleep(604800)  # 7 days

async def settlement_loop():
    """Background task to settle pending bets every 60 minutes."""
    import logging
    logger = logging.getLogger("settlement")
    while True:
        try:
            async with async_session_maker() as db:
                count = await ledger_service.settle_pending_bets(db)
                if count > 0:
                    logger.info(f"Automated settlement: Graded {count} pending bets.")
        except Exception as e:
            logger.error(f"Settlement loop error: {e}")
        await asyncio.sleep(3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 FastAPI Server starting up...")
    import logging
    logger = logging.getLogger(__name__)
    
    # Pre-populate static data into Redis cache
    from services.redis_service import redis_client
    from services.nfl_players import get_nfl_player_data
    
    try:
        # Just test the connection
        if redis_client:
            redis_client.ping()
            print("✅ connected to redis")
    except Exception as e:
        print(f"⚠️ redis not available: {e}")

    try:
        from jobs.email_cron import start_email_cron
        start_email_cron()
    except Exception as e:
        print(f"⚠️ email cron failed to boot: {e}")
        
    # Ensure tables exist (Synchronous)
    try:
        from database import engine, Base
        import models.users
        import models.props
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

    # Start background tasks
    asyncio.create_task(live_sync_loop())
    asyncio.create_task(daily_digest_loop())
    asyncio.create_task(settlement_loop())
    asyncio.create_task(weekly_reporting_loop())
    asyncio.create_task(live_odds_broadcaster())
    
    # Connect Redis (Upstash) or fall back to in-memory
    await cache.connect()
    logger.info(f"Cache mode: {cache.status}")
    logger.info("Waterfall providers: Odds API → ESPN → TheSportsDB → TheRundown → BallDontLie → MySportsFeeds → SportsGameOdds")
    yield

app = FastAPI(
    title="Sports Betting Intelligence API",
    description="Comprehensive sports betting analytics and intelligence platform",
    version="2.0.0",
    lifespan=lifespan,
)

# Global API Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files for legacy frontend support (if they exist in the app directory)
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Include the immediate working router
app.include_router(router, prefix="/immediate", tags=["immediate"])

# Include the validation router
app.include_router(validation_router, prefix="/validation", tags=["validation"])

# Include the track record router
app.include_router(track_record_router, prefix="/track-record", tags=["track-record"])

# Include the model status router
app.include_router(model_status_router, prefix="/status", tags=["status"])

# Include the working parlays router
app.include_router(working_parlays_router, prefix="/parlays", tags=["parlays"])

# Include the analysis router (CLV & Monte Carlo)
app.include_router(analysis_v2_router, prefix="/analysis", tags=["analysis"])

# Include the picks router (CLV & EV)
app.include_router(picks_router, prefix="/picks", tags=["picks"])

# Include the deeplinks router
app.include_router(deeplinks_router)

# Include the player splits router
app.include_router(splits_router)

# Include the alt-lines ladder router
app.include_router(alt_lines_router)

# Include the injuries router
app.include_router(injuries_router)

# Include the middle betting and boost analysis router
app.include_router(middle_boost_router)

# Include the Defense vs Position (DvP) router
app.include_router(dvp_router)
app.include_router(share_router)

from routers.live_router          import router as live_router
from routers.ai_assistant         import router as assistant_router
from routers.whale_router         import router as whale_router
from routers.kalshi_router        import router as kalshi_router
from routers.social_router        import router as social_router
from routers.kelly_router         import router as kelly_router
from routers.sgp_router           import router as sgp_router
from routers.hedge_router         import router as hedge_router
from routers.line_shopping_router import router as shop_router
from routers.analytics_router     import router as analytics_router
from routers.affiliate_router     import router as affiliate_router
from routers.referral_router      import router as referral_router
from routers.contest_router       import router as contest_router
from routers.admin_router         import router as admin_router
from routers.api_tier_router      import router as api_tier_router
from routers.autocopy_router      import router as autocopy_router
from routers.push_router          import router as push_router
from utils.feature_gate           import router as webhook_router

app.include_router(live_router)
app.include_router(assistant_router)
app.include_router(whale_router)
app.include_router(kalshi_router)
app.include_router(social_router)
app.include_router(kelly_router)
app.include_router(sgp_router)
app.include_router(hedge_router)
app.include_router(shop_router)
app.include_router(analytics_router)
app.include_router(affiliate_router)
app.include_router(referral_router)
app.include_router(contest_router)
app.include_router(admin_router)
app.include_router(api_tier_router)
app.include_router(autocopy_router)
app.include_router(push_router)
app.include_router(reporting_router)
app.include_router(execution_router)
app.include_router(backtest_router)

# Phase 6
app.include_router(config_router)
app.include_router(webhook_router)
app.include_router(auth_router.router)
app.include_router(ledger_router.router)
app.include_router(stripe_router.router)
app.include_router(chat_router.router)
app.include_router(admin_router.router)
app.include_router(affiliate_router.router)
app.include_router(live_odds_socket.router)
app.include_router(prop_predictor_router)
app.include_router(user_profile_router)

@app.get("/")
async def root():
    """Serve legacy landing page if exists, else API metadata"""
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Sports Betting Intelligence API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint — reports waterfall and cache status"""
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "cache": cache.status,
        "waterfall_providers": [
            "odds_api", "espn", "thesportsdb", "therundown",
            "balldontlie", "mysportsfeeds", "sportsgameodds"
        ],
        "free_providers_active": ["espn", "thesportsdb"],
    }

if __name__ == "__main__":
    import uvicorn
    # Always use Railway's PORT
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
