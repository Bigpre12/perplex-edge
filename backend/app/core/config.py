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

    # Scheduler
    scheduler_enabled: bool = True
    sched_odds_interval_min: int = 5
    sched_stats_interval_min: int = 15
    sched_model_interval_min: int = 10

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
