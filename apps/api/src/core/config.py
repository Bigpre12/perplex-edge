print(f"DEBUG: core.config is initializing...")
import os
import logging

APP_NAME = os.getenv("APP_NAME", "Lucrix")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'perplex_local.db'))}"
)
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
PORT = int(os.environ.get("PORT") or 8000)

class Settings:
    def __init__(self):
        self.APP_NAME = APP_NAME
        self.DATABASE_URL = DATABASE_URL
        self.CORS_ORIGINS = CORS_ORIGINS
        self.PORT = PORT
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.SECRET_KEY = os.environ.get("SECRET_KEY", "lucrix_dev_secret")
        self.ODDS_API_KEY = os.getenv("ODDS_API_KEY", "e9b6956ba6e50da9cc6a11511cb7e372")
        self.DEVELOPMENT_MODE = os.getenv("DEV_MODE", "true").lower() == "true"
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"
        self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
        self.STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
        self.STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "")
        self.STRIPE_ELITE_PRICE_ID = os.getenv("STRIPE_ELITE_PRICE_ID", "")
        self.FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

settings = Settings()
