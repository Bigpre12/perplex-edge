from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


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

    # The Odds API
    odds_api_key: str = ""
    odds_api_base_url: str = "https://api.the-odds-api.com/v4"

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
    sched_odds_interval_min: int = 5
    sched_stats_interval_min: int = 15
    sched_model_interval_min: int = 10
    sched_roster_interval_hours: int = 24  # Daily roster sync
    
    # Daily refresh configuration
    daily_refresh_hour: int = 9  # 9 AM EST
    hourly_check_interval: int = 60  # minutes

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
