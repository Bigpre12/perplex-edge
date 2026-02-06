from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, model_validator
from functools import lru_cache
from typing import Optional, Any
import logging
import sys

import yaml


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

    # AI Integration (optional - disabled by default)
    ai_enabled: bool = False
    ai_api_base_url: str = "https://api.groq.com/openai/v1"
    ai_api_key: str = ""
    ai_model: str = "llama-3.3-70b-versatile"
    ai_timeout_seconds: int = 30
    ai_max_retries: int = 2

    # Whop Integration
    whop_free_checkout_url: str = "https://whop.com/checkout/plan_WxHa3UGwMmjdd"
    whop_pro_checkout_url: str = "https://whop.com/checkout/plan_8Qztt62kvlW8y"

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
    
    # Check AI integration config
    if settings.ai_enabled and not settings.ai_api_key:
        issues.append("AI_ENABLED=true but AI_API_KEY is not set")
    elif not settings.ai_enabled:
        warnings.append("AI integration disabled (AI_ENABLED=false)")

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


# =============================================================================
# Stats Configuration (from YAML)
# =============================================================================

_stats_config_cache: Optional[dict[str, Any]] = None


def load_stats_config(reload: bool = False) -> dict[str, Any]:
    """
    Load stats configuration from stats_config.yaml.
    
    Configuration is cached after first load. Pass reload=True to force reload.
    
    Args:
        reload: Force reload from file (default: False)
    
    Returns:
        Dictionary with stats configuration
    
    Example:
        >>> config = load_stats_config()
        >>> nba_season = config["nba"]["season"]  # "2025-26"
        >>> default_games = config["nba"]["games_windows"]["default"]  # 5
    """
    global _stats_config_cache
    
    if _stats_config_cache is not None and not reload:
        return _stats_config_cache
    
    config_path = Path(__file__).parent / "stats_config.yaml"
    
    if not config_path.exists():
        logging.warning(f"Stats config file not found: {config_path}")
        # Return sensible defaults
        _stats_config_cache = {
            "rate_limiting": {
                "default_delay": 1.0,
                "batch_player_delay": 0.5,
            },
            "nba": {
                "season": "2025-26",
                "games_windows": {"short": 3, "default": 5, "medium": 10, "long": 20},
                "thresholds": {"points": 0.03, "rebounds": 0.04, "assists": 0.05},
                "confidence": {"min_model_probability": 0.55, "high_confidence": 0.65},
                "matching": {"fuzzy_threshold": 0.85},
            },
        }
        return _stats_config_cache
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            _stats_config_cache = yaml.safe_load(f)
        logging.info(f"Loaded stats config from {config_path}")
        return _stats_config_cache
    except Exception as e:
        logging.error(f"Failed to load stats config: {e}")
        # Return minimal defaults on error
        _stats_config_cache = {}
        return _stats_config_cache


def get_sport_config(sport_key: str) -> dict[str, Any]:
    """
    Get configuration for a specific sport.
    
    Args:
        sport_key: Sport identifier (e.g., 'nba', 'nfl', 'basketball_nba')
    
    Returns:
        Sport-specific configuration dict, or defaults if not found
    """
    config = load_stats_config()
    
    # Normalize sport key (strip "basketball_", "americanfootball_", etc.)
    normalized = sport_key.lower()
    if normalized.startswith("basketball_"):
        normalized = normalized.replace("basketball_", "")
    elif normalized.startswith("americanfootball_"):
        normalized = normalized.replace("americanfootball_", "")
    elif normalized.startswith("baseball_"):
        normalized = normalized.replace("baseball_", "")
    
    # Try direct match first, then normalized
    if sport_key in config:
        return config[sport_key]
    if normalized in config:
        return config[normalized]
    
    # Return NBA defaults if sport not found
    return config.get("nba", {})


def get_games_window(sport_key: str, window_type: str = "default") -> int:
    """
    Get the games window setting for a sport.
    
    Args:
        sport_key: Sport identifier
        window_type: Window type ('short', 'default', 'medium', 'long')
    
    Returns:
        Number of games to use for the window
    """
    sport_config = get_sport_config(sport_key)
    windows = sport_config.get("games_windows", {})
    return windows.get(window_type, windows.get("default", 5))


def get_ev_threshold(sport_key: str, stat_type: str) -> float:
    """
    Get the EV threshold for a specific stat type.
    
    Args:
        sport_key: Sport identifier
        stat_type: Stat type (e.g., 'points', 'rebounds', 'passing_yards')
    
    Returns:
        Minimum EV threshold (default: 0.03)
    """
    sport_config = get_sport_config(sport_key)
    thresholds = sport_config.get("thresholds", {})
    # Normalize stat type to lowercase
    stat_normalized = stat_type.lower()
    return thresholds.get(stat_normalized, 0.03)


def get_season_string(sport_key: str) -> str:
    """
    Get the current season string for a sport.
    
    Args:
        sport_key: Sport identifier
    
    Returns:
        Season string (e.g., '2025-26' for NBA, '2025' for NFL)
    """
    sport_config = get_sport_config(sport_key)
    return sport_config.get("season", "2025-26")


def get_rate_limit_delay() -> float:
    """Get the default API rate limit delay in seconds."""
    config = load_stats_config()
    rate_limiting = config.get("rate_limiting", {})
    return rate_limiting.get("default_delay", 1.0)


def get_batch_player_delay() -> float:
    """Get the delay between processing players in batch ETL."""
    config = load_stats_config()
    rate_limiting = config.get("rate_limiting", {})
    return rate_limiting.get("batch_player_delay", 0.5)


def get_fuzzy_match_threshold(sport_key: str) -> float:
    """
    Get the fuzzy match threshold for player name matching.
    
    Args:
        sport_key: Sport identifier
    
    Returns:
        Minimum similarity score (0.0-1.0) for a match
    """
    sport_config = get_sport_config(sport_key)
    matching = sport_config.get("matching", {})
    return matching.get("fuzzy_threshold", 0.85)


def get_min_model_probability(sport_key: str) -> float:
    """
    Get the minimum model probability threshold.
    
    Args:
        sport_key: Sport identifier
    
    Returns:
        Minimum win probability to consider a pick
    """
    sport_config = get_sport_config(sport_key)
    confidence = sport_config.get("confidence", {})
    return confidence.get("min_model_probability", 0.55)
