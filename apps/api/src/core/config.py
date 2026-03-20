import os
import logging
from dotenv import load_dotenv # type: ignore

# Try to load .env from current working directory (root)
load_dotenv(os.path.join(os.getcwd(), ".env"))

APP_NAME = os.getenv("APP_NAME", "Lucrix")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'perplex_local.db'))}"
)
PORT = int(os.environ.get("PORT") or 8000)

class Settings:
    def __init__(self):
        self.APP_NAME = APP_NAME
        self.DATABASE_URL = DATABASE_URL
        self.PORT = PORT
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # FIX 4: Secure defaults for production
        secret = os.environ.get("SECRET_KEY", "")
        if not secret:
            logging.critical("FATAL: SECRET_KEY environment variable is not set. Using insecure default.")
            secret = "CHANGE_ME_IN_PRODUCTION"
        self.SECRET_KEY = secret
        self.STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "")
        self.STRIPE_ELITE_PRICE_ID = os.getenv("STRIPE_ELITE_PRICE_ID", "")
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        self.SUPABASE_URL: str = os.getenv("SUPABASE_URL", os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""))
        self.SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", ""))
        self.SUPABASE_ANON_KEY: str = self.SUPABASE_KEY
        self.SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
        
        # Ensure default values are set for Pydantic-like compatibility if needed
        # although this class is not inherited from pydantic.BaseSettings here.
        
        # Odds API Configuration
        self.ODDS_API_KEY = os.getenv("ODDS_API_KEY", os.getenv("THE_ODDS_API_KEY", ""))
        self.ODDS_API_KEY_PRIMARY = self.ODDS_API_KEY
        raw_keys = os.getenv("ODDS_API_KEYS", "")
        self.ODDS_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
        self.ODDS_API_KEY_BACKUP = os.getenv("ODDS_API_KEY_BACKUP", "")
        
        self.DEVELOPMENT_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
        self.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", os.getenv("AI_API_KEY", ""))
        self.BETSTACK_API_KEY = os.getenv("BETSTACK_API_KEY", "")
        self.ODDSPAPI_API_KEY = os.getenv("ODDSPAPI_API_KEY", "")
        self.ROSTER_API_KEY = os.getenv("ROSTER_API_KEY", "")
        self.DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
        
        self.INGEST_EVENT_WINDOW_HOURS = int(os.getenv("INGEST_EVENT_WINDOW_HOURS", "36"))
        
        # CORS Setup — allow Vercel preview/production domains automatically
        raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        self.CORS_ORIGINS = [o.strip() for o in raw_origins.split(",") if o.strip()]
        # Always allow the configured FRONTEND_URL
        if self.FRONTEND_URL and self.FRONTEND_URL not in self.CORS_ORIGINS:
            self.CORS_ORIGINS.append(self.FRONTEND_URL)
        # Auto-allow all Vercel preview URLs for this project
        vercel_patterns = [
            "https://perplex-edge.vercel.app",
            "https://perplex-edge-git-main-bigpre12s-projects.vercel.app",
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

settings = Settings()
