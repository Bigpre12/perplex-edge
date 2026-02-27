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

# --- ROUTER IMPORTS ---
# Core Odds & Picks API
from api.immediate_working import router as immediate_router
from api.validation_endpoints import router as validation_router
from api.track_record_endpoints import router as track_record_router
from api.model_status_endpoints import router as model_status_router
from api.working_parlays import router as working_parlays_router
from api.picks import router as picks_router
from api.analysis import router as analysis_v2_router
from api.share import router as share_router

# Market Intelligence & Tools
from routers.deeplinks import router as deeplinks_router
from routers.splits import router as splits_router
from routers.alt_lines import router as alt_lines_router
from routers.injuries import router as injuries_router
from routers.middle_boost import router as middle_boost_router
from routers.dvp import router as dvp_router
from routers.kelly_router import router as kelly_router
from routers.sgp_router import router as sgp_router
from routers.hedge_router import router as hedge_router
from routers.line_shopping_router import router as shop_router
from routers.whale_router import router as whale_router

# Institutional & SaaS Infrastructure
from routers import auth_router, ledger_router, stripe_router, push_router, admin_router, config_router, affiliate_router, chat_router
from routers.api_tier_router import router as api_tier_router
from routers.autocopy_router import router as autocopy_router
from routers.reporting_router import router as reporting_router
from routers.execution_router import router as execution_router
from routers.backtest_router import router as backtest_router
from routers.referral_router import router as referral_router
from routers.ai_assistant import router as assistant_router
from utils.feature_gate import router as webhook_router

# Community & Real-Time Engine (Phase 10/11)
from routers.live_odds_socket import router as live_socket_router, live_odds_broadcaster
from routers.user_profile_router import router as user_profile_router
from ml.prop_predictor import router as prop_predictor_router

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
    
    try:
        if redis_client:
            redis_client.ping()
            print("✅ connected to redis")
    except Exception as e:
        print(f"⚠️ redis not available: {e}")

    try:
        start_email_cron()
    except Exception as e:
        print(f"⚠️ email cron failed to boot: {e}")
        
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# --- ROUTER REGISTRATION ---

# 1. Core Odds Engine & Analytics
app.include_router(immediate_router, prefix="/immediate", tags=["immediate"])
app.include_router(validation_router, prefix="/validation", tags=["validation"])
app.include_router(track_record_router, prefix="/track-record", tags=["track-record"])
app.include_router(model_status_router, prefix="/status", tags=["status"])
app.include_router(working_parlays_router, prefix="/parlays", tags=["parlays"])
app.include_router(analysis_v2_router, prefix="/analysis", tags=["analysis"])
app.include_router(picks_router, prefix="/picks", tags=["picks"])
app.include_router(share_router, prefix="/share", tags=["share"])

# 2. Market Tools & Sharp Intel
app.include_router(deeplinks_router)
app.include_router(splits_router)
app.include_router(alt_lines_router)
app.include_router(injuries_router)
app.include_router(middle_boost_router)
app.include_router(dvp_router)
app.include_router(kelly_router)
app.include_router(sgp_router)
app.include_router(hedge_router)
app.include_router(shop_router)
app.include_router(whale_router)

# 3. Institutional & SaaS Infrastructure
app.include_router(auth_router.router)
app.include_router(ledger_router.router)
app.include_router(stripe_router.router)
app.include_router(push_router.router)
app.include_router(admin_router.router)
app.include_router(config_router.router)
app.include_router(affiliate_router.router)
app.include_router(api_tier_router)
app.include_router(autocopy_router)
app.include_router(reporting_router)
app.include_router(execution_router)
app.include_router(backtest_router)
app.include_router(referral_router)
app.include_router(assistant_router)
app.include_router(chat_router.router)
app.include_router(webhook_router)

# 4. Community & Real-Time Expansion
app.include_router(live_socket_router)
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
