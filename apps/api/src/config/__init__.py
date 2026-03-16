"""
Centralized Configuration for LUCRIX Backend
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Core
    APP_NAME: str = os.getenv("APP_NAME", "Lucrix")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    DEVELOPMENT_MODE: bool = os.getenv("DEV_MODE", "true").lower() == "true"
    ODDS_API_DAILY_CAP: int = int(os.getenv("ODDS_API_DAILY_CAP", "3000"))
    CACHE_TTL_ODDS: int = int(os.getenv("CACHE_TTL_ODDS", "120"))
    CACHE_TTL_EV: int = int(os.getenv("CACHE_TTL_EV", "120"))
    CACHE_TTL_PROPS: int = int(os.getenv("CACHE_TTL_PROPS", "120"))
    CACHE_TTL_LIVE: int = int(os.getenv("CACHE_TTL_LIVE", "30"))
    PORT: int = int(os.environ.get("PORT") or 8000)
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or os.environ.get("JWT_SECRET_KEY") or os.environ.get("JWT_SECRET") or "lucrix_dev_secret_change_in_production"
    ALGORITHM: str = os.environ.get("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES") or 43200)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Auth
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    ODDS_API_KEYS: List[str] = os.getenv("ODDS_API_KEYS", "").split(",") if os.getenv("ODDS_API_KEYS") else []
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'data', 'perplex_local.db'))}"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL: int = 300  # 5 minutes default
    
    # Integrations
    ODDS_API_KEY_PRIMARY: str = os.getenv("ODDS_API_KEY_PRIMARY", "e9b6956ba6e50da9cc6a11511cb7e372") # 100k Tier
    ODDS_API_KEY_BACKUP: str = os.getenv("ODDS_API_KEY_BACKUP", "b94144c89048238eff1856d83c383d9a") # Fallback
    ODDS_API_KEY: str = os.getenv("ODDS_API_KEY") or os.getenv("ODDS_API_KEY_PRIMARY") or "e9b6956ba6e50da9cc6a11511cb7e372"
    ODDS_API_KEYS: List[str] = [
        k.strip() for k in os.getenv("ODDS_API_KEYS", "").split(",") if k.strip()
    ]
    ESPN_API_BASE: str = os.getenv("ESPN_API_BASE", "https://site.api.espn.com/apis/site/v2/sports")
    
    # Oracle AI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", os.getenv("AI_API_KEY", ""))
    ORACLE_MODEL: str = os.getenv("ORACLE_MODEL", "gpt-4o")
    ORACLE_MAX_TOKENS: int = 1000
    ORACLE_TEMPERATURE: float = 0.3
    
    # Stripe Payments
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRO_MONTHLY_PRICE_ID: str = os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID", "")
    STRIPE_PRO_ANNUAL_PRICE_ID: str = os.getenv("STRIPE_PRO_ANNUAL_PRICE_ID", "")
    STRIPE_ELITE_MONTHLY_PRICE_ID: str = os.getenv("STRIPE_ELITE_MONTHLY_PRICE_ID", "")
    STRIPE_ELITE_ANNUAL_PRICE_ID: str = os.getenv("STRIPE_ELITE_ANNUAL_PRICE_ID", "")
    
    # Discord & Community
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    WHOP_API_KEY: str = os.getenv("WHOP_API_KEY", "")
    
    # Monitoring
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    # Security
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
        "https://lucrix.vercel.app",
        "https://*.vercel.app",
        os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip('/')
    ]
    
    # Sports Configuration
    VALID_SPORTS: List[str] = [
        "basketball_nba", "basketball_wnba", "basketball_ncaab",
        "americanfootball_nfl", "americanfootball_ncaaf",
        "baseball_mlb", "icehockey_nhl", "soccer_epl",
        "soccer_uefa_champs_league", "soccer_mls",
        "mma_mixed_martial_arts", "tennis_atp_french_open",
        "tennis_wta", "golf_pga_tour"
    ]
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        case_sensitive=True,
        extra='ignore'
    )

settings = Settings()
