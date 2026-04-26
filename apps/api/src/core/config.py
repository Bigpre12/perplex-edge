import os
import logging

from core.env_loader import load_project_dotenv

load_project_dotenv()

APP_NAME = os.getenv("APP_NAME", "Lucrix")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'perplex_local.db'))}"
)
PORT = int(os.environ.get("PORT") or 8000)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}

class Settings:
    def __init__(self):
        self.APP_NAME = APP_NAME
        self.DATABASE_URL = DATABASE_URL
        self.PORT = PORT
        self.REDIS_URL = (os.getenv("REDIS_URL") or "").strip()
        self.CACHE_REDIS_URL = (os.getenv("CACHE_REDIS_URL") or "").strip()
        self.CELERY_REDIS_URL = (os.getenv("CELERY_REDIS_URL") or "").strip()
        self.REDIS_PRIMARY_URL = self.CACHE_REDIS_URL or self.REDIS_URL or "redis://localhost:6379"
        self.REDIS_WORKER_URL = self.CELERY_REDIS_URL or self.REDIS_PRIMARY_URL
        # Betstack: no URL unless set, unless API key is set (legacy default host for backwards compatibility)
        _betstack_url = (os.getenv("BETSTACK_BASE_URL") or "").strip().rstrip("/")
        _betstack_key = (os.getenv("BETSTACK_API_KEY") or "").strip()
        if _betstack_url:
            self.BETSTACK_BASE_URL = _betstack_url
        elif _betstack_key:
            # Free sports API (betstack.dev signup); enterprise uses explicit BETSTACK_BASE_URL
            self.BETSTACK_BASE_URL = "https://api.betstack.dev/api/v1"
        else:
            self.BETSTACK_BASE_URL = ""
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "https://perplex-edge.vercel.app")

        # Kalshi Trade API v2 (RSA). Demo default; set KALSHI_BASE_URL + keys for production.
        from core.kalshi_urls import sanitize_kalshi_base_url
        self.KALSHI_BASE_URL = sanitize_kalshi_base_url(os.getenv("KALSHI_BASE_URL"))
        self.KALSHI_KEY_ID = os.getenv("KALSHI_KEY_ID", os.getenv("KALSHI_API_KEY_ID", "")).strip()
        self.KALSHI_PRIVATE_KEY = os.getenv("KALSHI_PRIVATE_KEY", "").strip()
        
        # Diagnostic logging for Redis (redacted host)
        try:
            from urllib.parse import urlparse
            parsed_redis = urlparse(self.REDIS_URL)
            logging.info(f"Infrastructure: Redis configured at host={parsed_redis.hostname} port={parsed_redis.port}")
        except Exception:
            pass
        
        # FIX 4: Secure defaults for production
        secret = os.environ.get("SECRET_KEY", "")
        if not secret:
            logging.critical("FATAL: SECRET_KEY environment variable is not set. Using insecure default.")
            secret = "CHANGE_ME_IN_PRODUCTION"
        self.SECRET_KEY = secret
        self.STRIPE_PRO_MONTHLY_PRICE_ID = os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID", os.getenv("STRIPE_PRO_PRICE_ID", ""))
        self.STRIPE_PRO_ANNUAL_PRICE_ID = os.getenv("STRIPE_PRO_ANNUAL_PRICE_ID", "")
        self.STRIPE_ELITE_MONTHLY_PRICE_ID = os.getenv("STRIPE_ELITE_MONTHLY_PRICE_ID", os.getenv("STRIPE_ELITE_PRICE_ID", ""))
        self.STRIPE_ELITE_ANNUAL_PRICE_ID = os.getenv("STRIPE_ELITE_ANNUAL_PRICE_ID", "")
        
        # Legacy Aliases
        self.STRIPE_PRO_PRICE_ID = self.STRIPE_PRO_MONTHLY_PRICE_ID
        self.STRIPE_ELITE_PRICE_ID = self.STRIPE_ELITE_MONTHLY_PRICE_ID
        
        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""))
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", ""))
        self.SUPABASE_ANON_KEY: str = self.SUPABASE_KEY
        self.SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
        self.SUPABASE_ROLE_SPLIT_READY = bool(self.SUPABASE_ANON_KEY and self.SUPABASE_SERVICE_KEY)
        self.SUPABASE_SERVICE_KEY_LOOKS_ANON = (
            bool(self.SUPABASE_SERVICE_KEY and self.SUPABASE_ANON_KEY)
            and self.SUPABASE_SERVICE_KEY == self.SUPABASE_ANON_KEY
        )
        
        # Odds API Configuration - Centralized for Rotation
        raw_list = os.getenv("ODDS_API_KEYS", "")
        primary = os.getenv("ODDS_API_KEY", os.getenv("THE_ODDS_API_KEY", ""))

        # Support single-key deployments where the value is stored under ODDS_API_KEYS.
        if not primary and raw_list and "," not in raw_list:
            primary = raw_list.strip()
            raw_list = ""

        backup = os.getenv("ODDS_API_KEY_BACKUP", "")
        indexed_keys = []
        idx = 0
        while True:
            k = (os.getenv(f"THE_ODDS_API_KEY_{idx}") or "").strip()
            if not k:
                break
            indexed_keys.append(k)
            idx += 1
        
        # Aggregate all unique keys
        all_keys = [k.strip() for k in raw_list.split(",") if k.strip()]

        if primary and primary not in all_keys:
            all_keys.insert(0, primary)
        if backup and backup not in all_keys:
            all_keys.append(backup)
        for idx_key in indexed_keys:
            if idx_key and idx_key not in all_keys:
                all_keys.append(idx_key)
            
        self.ODDS_API_KEYS = all_keys
        self.ODDS_API_KEY = all_keys[0] if all_keys else ""
        self.ODDS_API_KEY_PRIMARY = self.ODDS_API_KEY
        self.ODDS_API_KEY_BACKUP = backup
        
        self.DEVELOPMENT_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
        self.IS_PRODUCTION = not self.DEVELOPMENT_MODE and (
            _env_bool("PRODUCTION", False)
            or _env_bool("RAILWAY_STATIC_URL", False)
            or bool((os.getenv("RAILWAY_ENVIRONMENT_NAME") or "").strip())
        )
        self.BYPASS_AUTH = _env_bool("BYPASS_AUTH", False)
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
        self.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.AI_GATEWAY_ENABLED = _env_bool("AI_GATEWAY_ENABLED", False)
        self.AI_GATEWAY_API_KEY = (os.getenv("AI_GATEWAY_API_KEY") or "").strip()
        self.AI_GATEWAY_BASE_URL = (
            os.getenv("AI_GATEWAY_BASE_URL", "https://ai-gateway.vercel.sh/v1").strip().rstrip("/")
        )
        self.AI_GATEWAY_MODEL = (os.getenv("AI_GATEWAY_MODEL") or "").strip()
        self.ORACLE_MODEL = os.getenv("ORACLE_MODEL", "gpt-4o")
        self.ORACLE_MAX_TOKENS = int(os.getenv("ORACLE_MAX_TOKENS", "1000"))
        self.ORACLE_TEMPERATURE = float(os.getenv("ORACLE_TEMPERATURE", "0.2"))
        
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", os.getenv("AI_API_KEY", ""))
        self.BETSTACK_API_KEY = os.getenv("BETSTACK_API_KEY", "")
        self.ODDSPAPI_API_KEY = os.getenv("ODDSPAPI_API_KEY", "")
        self.ROSTER_API_KEY = os.getenv("ROSTER_API_KEY", "")
        self.DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
        self.RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
        
        self.INGEST_EVENT_WINDOW_HOURS = int(os.getenv("INGEST_EVENT_WINDOW_HOURS", "36"))
        
        # New Waterfall Providers
        self.API_SPORTS_KEY = os.getenv("API_SPORTS_KEY", "")
        self.SPORTMONKS_KEY = (
            os.getenv("SPORTMONKS_KEY") or os.getenv("SPORTMONKS_API_KEY") or ""
        ).strip()
        self.ISPORTS_API_KEY = os.getenv("ISPORTS_API_KEY", "")
        
        # Betting Engine Configuration
        self.SHARP_BOOKMAKERS = ["pinnacle", "betonline", "betonlineag", "bookmaker", "circa", "circasports", "lowvig", "cris"]
        self.SOFT_BOOKMAKERS = ["draftkings", "fanduel", "betmgm", "caesars", "pointsbet", "williamhill", "betrivers", "unibet", "bovada", "betway"]
        self.EV_MIN_THRESHOLD = float(os.getenv("EV_MIN_THRESHOLD", "-100.0"))
        self.MAJOR_LINE_MOVE_THRESHOLD = float(os.getenv("MAJOR_LINE_MOVE_THRESHOLD", "5.0"))
        self.LIVE_DATA_POLLING_INTERVAL = int(os.getenv("LIVE_DATA_POLLING_INTERVAL", "30"))

        # Railway / quota governor (read here so deploy env is visible on Settings)
        from core.ingest_coordinator_env import (
            INGEST_COORDINATOR_MAX_PER_TICK,
            INGEST_COORDINATOR_TICK_SECONDS,
        )

        self.BRAIN_SKIP_WHEN_FRESH_MINUTES = int(os.getenv("BRAIN_SKIP_WHEN_FRESH_MINUTES", "7"))
        self.BRAIN_CACHE_SKIP = os.getenv("BRAIN_CACHE_SKIP", "true")
        self.INGEST_COORDINATOR_TICK_SECONDS = INGEST_COORDINATOR_TICK_SECONDS
        self.INGEST_COORDINATOR_MAX_PER_TICK = INGEST_COORDINATOR_MAX_PER_TICK
        self.ODDS_API_HARD_STOP_PCT = float(os.getenv("ODDS_API_HARD_STOP_PCT", "0.95"))
        self.ODDS_API_QUOTA_CONSERVATIVE_PCT = float(os.getenv("ODDS_API_QUOTA_CONSERVATIVE_PCT", "0.60"))
        self.ODDS_API_WARN_PCT = float(
            os.getenv("ODDS_API_WARN_PCT") or os.getenv("ODDS_API_USAGE_WARN_PCT", "0.80")
        )
        try:
            self.ODDS_API_MONTHLY_LIMIT = max(
                0,
                int(
                    os.getenv("ODDS_API_MONTHLY_LIMIT")
                    or os.getenv("THE_ODDS_API_MAX_CALLS_PER_MONTH", "20000")
                ),
            )
        except ValueError:
            self.ODDS_API_MONTHLY_LIMIT = 20_000
        
        # CORS Setup — allow Vercel preview/production domains automatically
        raw_origins = os.getenv("ALLOWED_ORIGINS", os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://localhost:5173"))
        self.CORS_ORIGINS = [o.strip() for o in raw_origins.split(",") if o.strip()]
        
        # Always allow the configured FRONTEND_URL
        if self.FRONTEND_URL and self.FRONTEND_URL not in self.CORS_ORIGINS:
            self.CORS_ORIGINS.append(self.FRONTEND_URL)
            
        # Auto-allow all Vercel preview URLs for this project
        vercel_patterns = [
            "https://perplex-edge.vercel.app",
            "https://perplex-edge-git-main-bigpre12s-projects.vercel.app",
            "https://perplex-edge-mu2vm4wb2-bigpre12s-projects.vercel.app",
        ]
        for vp in vercel_patterns:
            if vp not in self.CORS_ORIGINS:
                self.CORS_ORIGINS.append(vp)

        class Config:
            extra = "ignore"
            
        self.Config = Config

        self.validate()

    def validate(self):
        """Log warnings if critical configuration is missing, but do not crash."""
        required = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
        missing = [k for k in required if not getattr(self, k)]
        if missing:
            error_msg = f"WARNING: Missing Supabase configuration: {', '.join(missing)}. Auth features will be disabled."
            logging.warning(error_msg)
        if self.SUPABASE_SERVICE_KEY_LOOKS_ANON:
            logging.critical(
                "Supabase key role split is invalid: service key matches anon key. "
                "Set SUPABASE_SERVICE_ROLE_KEY/SUPABASE_SERVICE_KEY to a real service-role secret."
            )
        if self.IS_PRODUCTION and self.BYPASS_AUTH:
            logging.critical("BYPASS_AUTH=true is forbidden in production.")
        if self.AI_GATEWAY_ENABLED and not self.AI_GATEWAY_API_KEY:
            logging.warning("AI_GATEWAY_ENABLED=true but AI_GATEWAY_API_KEY is missing.")
        if not self.AI_GATEWAY_BASE_URL.startswith("http"):
            logging.warning(
                "AI_GATEWAY_BASE_URL appears malformed (%s). Expected an http(s) URL.",
                self.AI_GATEWAY_BASE_URL,
            )

settings = Settings()
