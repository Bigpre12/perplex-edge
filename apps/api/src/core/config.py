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
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "lucrix_dev_secret")
        self.STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "")
        self.STRIPE_ELITE_PRICE_ID = os.getenv("STRIPE_ELITE_PRICE_ID", "")
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
        self.SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
        
        # Odds API Configuration
        self.ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
        self.ODDS_API_KEY_PRIMARY = self.ODDS_API_KEY
        raw_keys = os.getenv("ODDS_API_KEYS", "")
        self.ODDS_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
        self.ODDS_API_KEY_BACKUP = os.getenv("ODDS_API_KEY_BACKUP", "")
        
        self.DEVELOPMENT_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
        self.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
        self.INGEST_EVENT_WINDOW_HOURS = int(os.getenv("INGEST_EVENT_WINDOW_HOURS", "36"))
        
        # CORS Setup
        raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
        self.CORS_ORIGINS = [o.strip() for o in raw_origins.split(",") if o.strip()]

        self.validate()

    def validate(self):
        """Fail fast if critical configuration is missing."""
        required = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
        missing = [k for k in required if not getattr(self, k)]
        if missing:
            error_msg = f"CRITICAL: Missing required configuration: {', '.join(missing)}"
            logging.critical(error_msg)
            # In production, we might want to raise an exception. 
            # In dev, we alert the user prominently.
            if not self.DEVELOPMENT_MODE:
                raise ValueError(error_msg)

settings = Settings()
