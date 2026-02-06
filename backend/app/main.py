"""Perplex Edge - Sports Betting Analytics API."""
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import get_settings
from app.core.database import db_lifespan, get_db
from app.core.logging import (
    configure_logging,
    get_logger,
    get_correlation_id,
    set_correlation_id,
    request_metrics,
)
from app.models import Sport
from app.scheduler import (
    start_background_tasks,
    stop_background_tasks,
    get_scheduler_status,
)
from app.api.admin import router as admin_router
from app.api.public import router as public_router
from app.api.sync import router as sync_router
from app.api.stats import router as stats_router
from app.api.games import router as games_router
from app.api.odds import router as odds_router
from app.api.props import router as props_router
from app.api.injuries import router as injuries_router
from app.api.picks import router as picks_router
from app.api.analytics import router as analytics_router
from app.api.nfl import router as nfl_router
from app.api.ncaab import router as ncaab_router
from app.api.bets import router as bets_router
from app.api.data_v2 import router as data_v2_router
from app.api.watchlists import router as watchlists_router
from app.api.cards import router as cards_router
from app.api.slate import router as slate_router
from app.api.users import router as users_router
from app.api.webhooks import router as webhooks_router
from app.api.seasons import router as seasons_router
from app.api.trades import router as trades_router
from app.api.ai_recommendations import router as ai_router
from app.api.deep_dive import router as deep_dive_router
from app.api.sports import router as sports_router
from app.api.meta import router as meta_router
from app.api.health import router as health_router
from app.api.brain_persistence import router as brain_persistence_router

# Configure structured logging
# Use JSON logs in production (ENVIRONMENT != 'development')
_env = os.getenv("ENVIRONMENT", "production")
configure_logging(json_logs=(_env != "development"), log_level="INFO")
logger = get_logger(__name__)

settings = get_settings()


# =============================================================================
# Request Logging Middleware
# =============================================================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests with correlation IDs and metrics.
    
    Logs: path, method, status_code, duration_ms, correlation_id
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())[:8]
        set_correlation_id(correlation_id)
        
        # Record start time
        start_time = time.perf_counter()
        
        # Process request
        response = None
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(
                "request_failed",
                path=request.url.path,
                method=request.method,
                error=str(e)[:200],
            )
            raise
        finally:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Record metrics
            request_metrics.record_request(
                path=request.url.path,
                method=request.method,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            
            # Log request (skip health checks for noise reduction)
            if not request.url.path.startswith(("/health", "/ping")):
                log_level = "warning" if status_code >= 400 else "info"
                getattr(logger, log_level)(
                    "request_completed",
                    path=request.url.path,
                    method=request.method,
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    query_params=str(request.query_params) if request.query_params else None,
                )
        
        # Add correlation ID to response headers
        if response:
            response.headers["X-Correlation-ID"] = correlation_id
        
        return response


# =============================================================================
# Lifespan
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    logger.info("starting_perplex_engine", version="0.1.0")
    
    # Initialize Sentry for error monitoring (before anything else)
    from app.core.sentry import init_sentry
    sentry_enabled = init_sentry()
    
    # Validate configuration at startup
    from app.core.config import validate_startup_config
    config_status = validate_startup_config()
    
    if not config_status["valid"]:
        logger.error(
            "startup_config_invalid",
            issues=config_status["issues"],
        )
        # Continue anyway - let individual services fail gracefully
    
    if config_status.get("warnings"):
        for warning in config_status["warnings"]:
            logger.warning("startup_config_warning", message=warning)
    
    # Initialize database
    async with db_lifespan(app):
        # Database is now initialized and ready
        
        # Start the autonomous brain loop
        try:
            from app.services.brain import brain_loop
            import asyncio
            
            # Start brain loop in background
            brain_task = asyncio.create_task(brain_loop(interval_minutes=5, initial_delay=90))
            logger.info("[STARTUP] Autonomous brain loop started (5min cycles, 90s delay)")
            
            # Store task reference for cleanup
            app.state.brain_task = brain_task
            
        except Exception as e:
            logger.error(f"[STARTUP] Failed to start brain loop: {e}", exc_info=True)
            # Continue without brain - system can still function
        
        logger.info("Application startup complete")
        
        # Start background tasks if scheduler is enabled
        background_tasks = []
        if settings.scheduler_enabled:
            try:
                background_tasks = start_background_tasks()
                logger.info(
                    "background_tasks_started",
                    task_count=len(background_tasks),
                )
            except Exception as e:
                logger.error("background_tasks_failed", error=str(e))
        else:
            logger.info("scheduler_disabled")
        
        logger.info(
            "perplex_engine_ready",
            environment=config_status.get("environment"),
            scheduler_enabled=settings.scheduler_enabled,
        )
        
        yield
        
        # Shutdown
        logger.info("perplex_engine_shutting_down")
        
        # Stop background tasks
        if background_tasks:
            await stop_background_tasks(background_tasks)
            logger.info("background_tasks_stopped")
    
    logger.info("perplex_engine_shutdown_complete")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Perplex Edge",
    description="Sports betting analytics platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration - use production config
from app.core.production import validate_and_log_config, get_production_config

# Validate production configuration
validate_and_log_config()

ALLOWED_ORIGINS = settings.allowed_origins

# Force wildcard CORS for Railway environments as fallback
production_config = get_production_config()
if production_config.is_railway():
    logger.warning("CORS: Railway environment detected, forcing wildcard CORS")
    ALLOWED_ORIGINS = ["*"]
elif not ALLOWED_ORIGINS or ("perplex-edge-production.up.railway.app" not in str(ALLOWED_ORIGINS) and "*" not in str(ALLOWED_ORIGINS)):
    logger.warning("CORS: No valid origins found, allowing all origins for Railway compatibility")
    ALLOWED_ORIGINS = ["*"]

# Additional safety: Always include wildcard for Railway production
if os.getenv("RAILWAY_ENVIRONMENT") == "production":
    logger.warning("CORS: Railway production environment, ensuring wildcard CORS")
    ALLOWED_ORIGINS = ["*"]

logger.info("cors_origins_configured", origins=ALLOWED_ORIGINS)

# Middleware ordering: Starlette executes middleware in REVERSE order of addition.
# We add RequestLoggingMiddleware FIRST so it runs INSIDE CORSMiddleware,
# ensuring CORS headers are always present even if the logging layer errors.

# 1) Request logging middleware (inner — runs after CORS headers are set)
app.add_middleware(RequestLoggingMiddleware)

# 2) CORS middleware (outer — always adds Access-Control-* headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "Content-Type", "Authorization"],
    max_age=600,  # Cache preflight for 10 minutes
)

# Add additional CORS middleware as backup for Railway
class RailwayCORSMiddleware(BaseHTTPMiddleware):
    """Backup CORS middleware specifically for Railway environments."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Force CORS headers for Railway if not present
        origin = request.headers.get("origin")
        if origin and not response.headers.get("access-control-allow-origin"):
            response.headers["access-control-allow-origin"] = "*"
            response.headers["access-control-allow-methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["access-control-allow-headers"] = "*"
            response.headers["access-control-allow-credentials"] = "true"
            
            logger.info(
                "cors_backup_headers_added",
                origin=origin,
                path=request.url.path
            )
        
        return response

# Add Railway CORS backup middleware
app.add_middleware(RailwayCORSMiddleware)

# Add CORS debugging middleware
class CORSDebuggingMiddleware(BaseHTTPMiddleware):
    """Debug CORS issues by logging request details."""
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        method = request.headers.get("access-control-request-method")
        headers = request.headers.get("access-control-request-headers")
        
        # Log preflight requests for debugging
        if request.method == "OPTIONS":
            logger.info(
                "cors_preflight_request",
                origin=origin,
                method=method,
                headers=headers,
                path=request.url.path,
                allowed_origins=ALLOWED_ORIGINS
            )
        
        response = await call_next(request)
        
        # Log CORS headers in response
        if request.method == "OPTIONS":
            logger.info(
                "cors_preflight_response",
                access_control_allow_origin=response.headers.get("access-control-allow-origin"),
                access_control_allow_methods=response.headers.get("access-control-allow-methods"),
                access_control_allow_headers=response.headers.get("access-control-allow-headers"),
                status_code=response.status_code
            )
        
        return response

# Add CORS debugging middleware
app.add_middleware(CORSDebuggingMiddleware)


# =============================================================================
# CORS Health Check Endpoint
# =============================================================================

@app.get("/cors-debug")
async def cors_debug():
    """Debug endpoint to check CORS configuration."""
    from app.core.production import get_production_config
    
    config = get_production_config()
    
    return {
        "environment": os.getenv("ENVIRONMENT"),
        "is_railway": config.is_railway(),
        "frontend_url": os.getenv("FRONTEND_URL"),
        "cors_origins": os.getenv("CORS_ORIGINS"),
        "allowed_origins": settings.allowed_origins,
        "railway_env": os.getenv("RAILWAY_ENVIRONMENT"),
        "railway_service": os.getenv("RAILWAY_SERVICE_NAME"),
        "railway_project": os.getenv("RAILWAY_PROJECT_NAME"),
    }


@app.get("/cors-health")
async def cors_health_check():
    """Health check that explicitly sets CORS headers for debugging."""
    response = JSONResponse({
        "status": "ok",
        "cors_enabled": True,
        "allowed_origins": ALLOWED_ORIGINS,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "unknown"),
        "service_name": os.getenv("RAILWAY_SERVICE_NAME", "unknown")
    })
    
    # Explicitly set CORS headers
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response


@app.options("/cors-health")
async def cors_health_options():
    """OPTIONS preflight handler for CORS health check."""
    response = Response(status_code=200)
    
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "600"
    
    return response

# Include routers
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(public_router, prefix="/api", tags=["public"])
app.include_router(sync_router, prefix="/api/sync", tags=["sync"])
app.include_router(stats_router, prefix="/api/stats", tags=["stats"])
app.include_router(games_router, prefix="/api/games", tags=["games"])
app.include_router(odds_router, prefix="/api/odds", tags=["odds"])
app.include_router(props_router, prefix="/api/props", tags=["props"])
app.include_router(injuries_router, prefix="/api/injuries", tags=["injuries"])
app.include_router(picks_router, prefix="/api/picks", tags=["picks"])
app.include_router(analytics_router, prefix="/api", tags=["analytics"])
app.include_router(nfl_router, prefix="/api", tags=["nfl"])
app.include_router(ncaab_router, prefix="/api", tags=["ncaab"])
app.include_router(bets_router, prefix="/api", tags=["bets"])
app.include_router(data_v2_router, prefix="/api/data", tags=["data-v2"])
app.include_router(watchlists_router, prefix="/api", tags=["watchlists"])
app.include_router(cards_router, prefix="/api", tags=["cards"])
app.include_router(slate_router, prefix="/api", tags=["slate"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(webhooks_router, prefix="/api", tags=["webhooks"])
app.include_router(seasons_router, prefix="/api", tags=["seasons"])
app.include_router(trades_router, prefix="/api", tags=["trades"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
app.include_router(deep_dive_router, prefix="/api/deep-dive", tags=["deep-dive"])
app.include_router(sports_router, prefix="/api/sports", tags=["sports"])
app.include_router(meta_router, prefix="/api/meta", tags=["meta"])
app.include_router(health_router, prefix="/api/health", tags=["health"])
app.include_router(brain_persistence_router, tags=["brain-persistence"])


# =============================================================================
# Global Exception Handler (ensures CORS headers on 500 errors)
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle unhandled exceptions and ensure CORS headers are sent.
    
    When FastAPI throws an unhandled exception, the error response might
    bypass the CORS middleware. This handler ensures CORS headers are
    always included, so the browser can read the error response.
    """
    # Log the error with context
    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
    )
    
    # Build CORS headers if origin is allowed
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
        headers=headers,
    )


# =============================================================================
# Health Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Perplex Edge API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint - no database access (for liveness probes)."""
    return {"status": "ok"}


@app.get("/health/ai")
async def health_ai():
    """Check AI integration config status."""
    s = get_settings()
    return {
        "ai_enabled": s.ai_enabled,
        "ai_api_base_url": s.ai_api_base_url,
        "ai_model": s.ai_model,
        "ai_api_key_set": bool(s.ai_api_key),
        "raw_env_ai_enabled": os.getenv("AI_ENABLED", "NOT_SET"),
    }


@app.get("/ping")
async def ping():
    """Simple ping endpoint - no database access."""
    return {"ping": "pong"}


@app.get("/health/db")
async def health_db():
    """Database health check endpoint."""
    from sqlalchemy import text
    from app.core.database import get_engine
    
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)[:200]}


@app.get("/health/full")
async def health_full(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.
    
    Checks all dependencies:
    - Database connectivity
    - Odds API quota
    - Cache health
    - Scheduler status
    - Data freshness
    - Circuit breakers
    
    Use /health for simple liveness checks, /health/full for readiness checks.
    """
    from app.core.health import run_all_health_checks
    return await run_all_health_checks(db)


@app.get("/health/ready")
async def health_ready(db: AsyncSession = Depends(get_db)):
    """
    Readiness check endpoint - verifies service is ready to accept traffic.
    
    Checks database connectivity only (quick check).
    """
    from app.core.health import run_quick_health_check
    return await run_quick_health_check(db)


@app.get("/api/health")
async def api_health():
    """API health check (for frontend compatibility)."""
    return {"status": "ok", "api": True}


@app.post("/api/admin/cache-bust")
async def cache_bust():
    """
    Invalidate all caches on deploy.
    
    Call this endpoint from Railway deploy hooks to ensure
    users see fresh data after each deployment.
    """
    from app.services.memory_cache import cache
    count = cache.clear()
    logger.info("cache_bust_triggered", entries_cleared=count)
    return {"status": "ok", "message": "All caches cleared", "entries_cleared": count}


@app.get("/api/scheduler/status")
async def scheduler_status():
    """Get scheduler status and running tasks."""
    return get_scheduler_status()


@app.get("/api/brain/status")
async def brain_status():
    """Get autonomous brain status and health with advanced monitoring."""
    try:
        from app.services.brain import (
            _brain, _brain_debugger, _correlation_tracker, 
            _anomaly_detector, _data_validator, _business_metrics
        )
        from app.core.production_config import production_config
        from app.core.dryrun_evaluation import dry_run_manager, evaluation_framework
        from app.core.brain_config import brain_config
        
        # Check if brain is running
        brain_task = getattr(app.state, 'brain_task', None)
        is_running = brain_task and not brain_task.done()
        
        # Get brain state
        brain_info = {
            "is_active": is_running,
            "started_at": _brain.started_at.isoformat() if hasattr(_brain, 'started_at') else None,
            "cycle_count": _brain.cycle_count,
            "overall_status": _brain.overall_status,
            "uptime_hours": None,
            "debug_enabled": _brain_debugger.debug_enabled,
            "debug_log_size": len(_brain_debugger.debug_log),
            "error_log_size": len(_brain_debugger.error_log),
            "last_cycle": None,
            # Advanced monitoring components
            "correlation_tracking": _correlation_tracker.get_operation_summary(),
            "anomaly_detection": {
                "baseline_metrics_count": len(_anomaly_detector.baseline_metrics),
                "anomaly_thresholds": _anomaly_detector.anomaly_thresholds
            },
            "data_validation": {
                "validation_rules_count": len(_data_validator.validation_rules),
                "rules": list(_data_validator.validation_rules.keys())
            },
            "business_metrics": {
                "current_metrics": _business_metrics.current_metrics,
                "history_size": len(_business_metrics.metrics_history),
                "trend_analysis": _business_metrics.get_trend_analysis()
            },
            # Production components
            "production_config": {
                "alert_rules_count": len(production_config.alert_rules),
                "runbooks_count": len(production_config.runbooks),
                "guardrails_count": len(production_config.guardrails),
                "metrics_count": len(production_config.metrics),
                "policies_count": len(production_config.policies)
            },
            "dry_run": {
                "mode": dry_run_manager.mode.value,
                "safe_mode": dry_run_manager.safe_mode,
                "action_history_count": len(dry_run_manager.action_history),
                "current_cycle_actions": len(dry_run_manager.current_cycle_actions)
            },
            "evaluation": {
                "experiments_count": len(evaluation_framework.experiments),
                "current_experiment": evaluation_framework.current_experiment.get("id") if evaluation_framework.current_experiment else None
            },
            "config": brain_config.get_config_summary()
        }
        
        if hasattr(_brain, 'started_at') and _brain.started_at:
            brain_info["uptime_hours"] = (datetime.now(timezone.utc) - _brain.started_at).total_seconds() / 3600
        
        # Get last cycle info if available
        if _brain_debugger.debug_log:
            last_cycle = next((log for log in reversed(_brain_debugger.debug_log) 
                             if log.get("component") == "brain_loop" and "cycle_" in log.get("operation", "")), None)
            if last_cycle:
                brain_info["last_cycle"] = {
                    "timestamp": last_cycle.get("timestamp"),
                    "operation": last_cycle.get("operation"),
                    "data": last_cycle.get("data", {}),
                }
        
        return brain_info
        
    except Exception as e:
        return {
            "is_active": False,
            "error": str(e),
            "message": "Brain service not available"
        }


@app.get("/api/brain/production/config")
async def get_production_config():
    """Get production configuration for brain service."""
    try:
        from app.core.production_config import production_config
        
        return {
            "alert_rules": [
                {
                    "name": rule.name,
                    "category": rule.category.value,
                    "severity": rule.severity.value,
                    "condition": rule.condition,
                    "threshold": rule.threshold,
                    "description": rule.description,
                    "runbook_id": rule.runbook_id,
                    "quiet_hours": rule.quiet_hours
                }
                for rule in production_config.alert_rules
            ],
            "runbooks": [
                {
                    "id": rb.id,
                    "title": rb.title,
                    "category": rb.category.value,
                    "severity": rb.severity.value,
                    "estimated_time_minutes": rb.estimated_time_minutes,
                    "required_permissions": rb.required_permissions
                }
                for rb in production_config.runbooks
            ],
            "guardrails": [
                {
                    "name": gr.name,
                    "max_data_deletion_per_cycle_mb": gr.max_data_deletion_per_cycle_mb,
                    "max_api_calls_per_hour": gr.max_api_calls_per_hour,
                    "max_config_changes_per_day": gr.max_config_changes_per_day,
                    "safe_mode_enabled": gr.safe_mode_enabled,
                    "requires_approval_for": gr.requires_approval_for
                }
                for gr in production_config.guardrails
            ],
            "metrics": [
                {
                    "name": m.name,
                    "description": m.description,
                    "unit": m.unit,
                    "target_value": m.target_value,
                    "warning_threshold": m.warning_threshold,
                    "critical_threshold": m.critical_threshold,
                    "category": m.category,
                    "sli": m.sli
                }
                for m in production_config.metrics
            ],
            "policies": production_config.policies,
            "deployment_checklist": production_config.deployment_checklist
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to get production config"}


@app.post("/api/brain/dry-run/mode")
async def set_dry_run_mode(mode: str):
    """Set dry-run mode for brain operations."""
    try:
        from app.core.dryrun_evaluation import DryRunMode, dry_run_manager
        
        if mode not in [m.value for m in DryRunMode]:
            return {"error": f"Invalid mode. Valid options: {[m.value for m in DryRunMode]}"}
        
        dry_run_manager.mode = DryRunMode(mode)
        
        return {
            "mode": dry_run_manager.mode.value,
            "safe_mode": dry_run_manager.safe_mode,
            "message": f"Dry-run mode set to {mode}"
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to set dry-run mode"}


@app.get("/api/brain/dry-run/history")
async def get_dry_run_history(limit: int = 10):
    """Get history of dry-run evaluations."""
    try:
        from app.core.dryrun_evaluation import dry_run_manager
        
        history = dry_run_manager.action_history[-limit:] if limit > 0 else dry_run_manager.action_history
        
        return {
            "total_cycles": len(dry_run_manager.action_history),
            "current_mode": dry_run_manager.mode.value,
            "safe_mode": dry_run_manager.safe_mode,
            "cycles": [
                {
                    "cycle_id": cycle.cycle_id,
                    "timestamp": cycle.timestamp.isoformat(),
                    "proposed_actions": len(cycle.proposed_actions),
                    "executed_actions": len(cycle.executed_actions),
                    "prevented_actions": len(cycle.prevented_actions),
                    "impact_assessment": cycle.impact_assessment,
                    "recommendations": cycle.recommendations
                }
                for cycle in reversed(history)
            ]
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to get dry-run history"}


@app.post("/api/brain/experiments/start")
async def start_experiment(name: str, description: str, duration_days: int = 7):
    """Start a new brain evaluation experiment."""
    try:
        from app.core.dryrun_evaluation import evaluation_framework
        
        experiment_id = evaluation_framework.start_experiment(name, description, duration_days)
        
        return {
            "experiment_id": experiment_id,
            "name": name,
            "description": description,
            "duration_days": duration_days,
            "status": "started",
            "message": f"Experiment {name} started"
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to start experiment"}


@app.get("/api/brain/experiments")
async def get_experiments():
    """Get all brain evaluation experiments."""
    try:
        from app.core.dryrun_evaluation import evaluation_framework
        
        return {
            "total_experiments": len(evaluation_framework.experiments),
            "current_experiment": evaluation_framework.current_experiment,
            "experiments": [
                {
                    "id": exp["id"],
                    "name": exp["name"],
                    "description": exp["description"],
                    "status": exp["status"],
                    "start_date": exp["start_date"].isoformat(),
                    "end_date": exp["end_date"].isoformat(),
                    "results": exp.get("results"),
                    "analysis": exp.get("analysis")
                }
                for exp in evaluation_framework.experiments
            ]
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to get experiments"}


@app.get("/api/brain/config/strategies")
async def get_brain_strategies():
    """Get brain strategy configurations."""
    try:
        from app.core.brain_config import brain_config
        
        strategies = brain_config.get_enabled_strategies()
        
        return {
            "enabled_strategies": [
                {
                    "name": s.name,
                    "description": s.description,
                    "priority": s.priority,
                    "parameters": s.parameters,
                    "conditions": s.conditions,
                    "limits": s.limits
                }
                for s in strategies
            ],
            "config_summary": brain_config.get_config_summary()
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Failed to get brain strategies"}


# =============================================================================
# Sports Endpoints (utility - database query)
# =============================================================================

@app.get("/sports")
async def list_sports_db(db: AsyncSession = Depends(get_db)):
    """List all sports from database (utility endpoint)."""
    try:
        result = await db.execute(select(Sport))
        sports = result.scalars().all()
        return {
            "items": [
                {"id": s.id, "name": s.name, "league_code": s.league_code}
                for s in sports
            ],
            "total": len(sports)
        }
    except Exception as e:
        return {"items": [], "total": 0, "error": str(e)[:200]}


# NOTE: /api/sports is handled by public_router (queries database)
# NOTE: /api/picks is handled by picks_router (uses ModelPick table)
# NOTE: /api/picks/refresh is handled by picks_router
# NOTE: /api/stats/* is handled by stats_router (mounted at /api/stats)
