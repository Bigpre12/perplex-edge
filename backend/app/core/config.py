from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from functools import lru_cache
from typing import Optional, Any
import logging
import sys


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: str = "development"
    port: int = 8000

    # Database
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/perplex"

    # The Odds API (Primary)
    odds_api_key: str = ""
    odds_api_base_url: str = "https://api.the-odds-api.com/v4"

    # BetStack API (Secondary fallback)
    betstack_api_key: str = ""
    betstack_api_base_url: str = "https://api.the-odds-api.com/v4"  # Uses same format as Odds API

    # OddsPapi API (Historical data & analytics)
    oddspapi_api_key: str = ""
    oddspapi_base_url: str = "https://api.oddspapi.io/v4"

    # Stats API
    stats_api_key: str = ""
    stats_api_base_url: str = "https://api.sportsstats.example.com/v1"

    # Injury API
    injury_api_key: str = ""
    injury_api_base_url: str = "https://api.injurytracker.example.com/v1"

    # Roster API (balldontlie.io)
    roster_api_key: str = ""
    roster_api_base_url: str = "https://api.balldontlie.io/v1"

    # Frontend URL (for CORS)
    frontend_url: str = "http://localhost:5173"
    # Additional CORS origins (comma-separated)
    cors_origins: str = ""

    # Scheduler (disabled by default - enable once DB is confirmed working)
    scheduler_enabled: bool = False
    scheduler_use_stubs: bool = True  # Use stub data for scheduled syncs (no API keys needed)
    
    # Sentry DSN for error monitoring (optional)
    sentry_dsn: str = ""
    
    # Redis URL for caching (optional - falls back to in-memory)
    redis_url: str = ""

    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL is provided and not empty."""
        if not v or v == "":
            raise ValueError("DATABASE_URL is required")
        return v
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is a known value."""
        valid_envs = ["development", "staging", "production", "test"]
        if v.lower() not in valid_envs:
            logging.warning(f"Unknown environment '{v}'. Expected one of: {valid_envs}")
        return v.lower()
    
    @model_validator(mode='after')
    def validate_api_keys_for_scheduler(self) -> 'Settings':
        """Warn if scheduler is enabled but API keys are missing (when not using stubs)."""
        if self.scheduler_enabled and not self.scheduler_use_stubs:
            if not self.odds_api_key:
                logging.warning(
                    "SCHEDULER_ENABLED=true and SCHEDULER_USE_STUBS=false but ODDS_API_KEY is not set. "
                    "Real API calls will fail. Set SCHEDULER_USE_STUBS=true or provide ODDS_API_KEY."
                )
        return self
    # Intervals optimized for Odds API free tier (500 requests/month)
    # Set to 60 min to stay within limits; reduce if you have paid plan
    sched_odds_interval_min: int = 60  # Hourly odds/injuries sync
    sched_stats_interval_min: int = 60  # Hourly stats sync
    sched_model_interval_min: int = 60  # Hourly pick generation
    sched_roster_interval_hours: int = 24  # Daily roster sync
    sched_settlement_interval_min: int = 30  # Settlement check interval (hit rate tracking)
    
    # Daily refresh configuration
    daily_refresh_hour: int = 6  # 6 AM ET (before NBA games posted)
    hourly_check_interval: int = 60  # minutes

    # NFL-specific settings
    nfl_sync_interval_min: int = 60  # Hourly NFL odds sync
    nfl_snapshot_hour: int = 6  # 6 AM ET daily snapshot
    nfl_backup_dir: str = "backups"  # JSON backup directory

    # NCAAB-specific settings
    ncaab_sync_interval_min: int = 60  # Hourly NCAAB odds sync
    ncaab_snapshot_hour: int = 6  # 6 AM ET daily snapshot
    ncaab_backup_dir: str = "backups"  # JSON backup directory

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def database_url_async(self) -> str:
        """Convert DATABASE_URL to asyncpg format for SQLAlchemy async."""
        url = self.database_url
        # Already has asyncpg - use as-is
        if "+asyncpg://" in url:
            return url
        # Convert postgresql+psycopg:// to postgresql+asyncpg://
        if url.startswith("postgresql+psycopg://"):
            return url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
        # Convert postgresql:// to postgresql+asyncpg://
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Convert postgres:// to postgresql+asyncpg://
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    @property
    def allowed_origins(self) -> list[str]:
        """Get list of allowed CORS origins."""
        origins = ["http://localhost:5173"]
        if self.frontend_url and self.frontend_url not in origins:
            origins.append(self.frontend_url)
        if self.cors_origins:
            for origin in self.cors_origins.split(","):
                origin = origin.strip()
                if origin and origin not in origins:
                    origins.append(origin)
        return origins


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def validate_startup_config() -> dict[str, Any]:
    """
    Validate configuration at startup and return a summary.
    
    Called during application startup to:
    1. Verify required settings are present
    2. Log warnings for missing optional settings
    3. Return a status summary
    
    Returns:
        dict with validation results
    """
    issues: list[str] = []
    warnings: list[str] = []
    
    try:
        settings = get_settings()
    except Exception as e:
        logging.error(f"Failed to load settings: {e}")
        return {
            "valid": False,
            "issues": [f"Settings load failed: {str(e)}"],
            "warnings": [],
        }
    
    # Check required settings
    if not settings.database_url:
        issues.append("DATABASE_URL is required but not set")
    
    # Check API keys and log warnings for missing ones
    api_keys = {
        "ODDS_API_KEY": settings.odds_api_key,
        "STATS_API_KEY": settings.stats_api_key,
        "INJURY_API_KEY": settings.injury_api_key,
        "ROSTER_API_KEY": settings.roster_api_key,
    }
    
    missing_keys = [name for name, value in api_keys.items() if not value]
    if missing_keys:
        if settings.scheduler_use_stubs:
            warnings.append(
                f"Using stub data (SCHEDULER_USE_STUBS=true). "
                f"Missing API keys: {', '.join(missing_keys)}"
            )
        else:
            warnings.append(
                f"Missing API keys (real API calls may fail): {', '.join(missing_keys)}"
            )
    
    # Check Sentry DSN in production
    if settings.is_production and not settings.sentry_dsn:
        warnings.append("SENTRY_DSN not set - error monitoring disabled in production")
    
    # Log results
    if issues:
        for issue in issues:
            logging.error(f"Config Error: {issue}")
    
    if warnings:
        for warning in warnings:
            logging.warning(f"Config Warning: {warning}")
    
    # Log successful settings summary
    logging.info(
        f"Config loaded: environment={settings.environment}, "
        f"scheduler_enabled={settings.scheduler_enabled}, "
        f"scheduler_use_stubs={settings.scheduler_use_stubs}"
    )
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "environment": settings.environment,
        "scheduler_enabled": settings.scheduler_enabled,
        "scheduler_use_stubs": settings.scheduler_use_stubs,
    }
