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

    # Frontend URL (for CORS)
    frontend_url: str = "http://localhost:5173"
    # Additional CORS origins (comma-separated)
    cors_origins: str = ""

    # Scheduler (disabled by default - enable once DB is confirmed working)
    scheduler_enabled: bool = False
    sched_odds_interval_min: int = 5
    sched_stats_interval_min: int = 15
    sched_model_interval_min: int = 10

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def database_url_async(self) -> str:
        """Get database URL with async driver prefix.
        
        Railway provides postgresql:// but SQLAlchemy async needs postgresql+psycopg://
        Handles various input formats: postgresql://, postgres://, postgresql+asyncpg://
        """
        url = self.database_url
        # Handle asyncpg URLs (convert to psycopg)
        if "+asyncpg://" in url:
            url = url.replace("+asyncpg://", "+psycopg://", 1)
        # Handle plain postgresql:// URLs
        elif url.startswith("postgresql://") and "+psycopg://" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        # Handle postgres:// URLs (Heroku/Railway shorthand)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
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
