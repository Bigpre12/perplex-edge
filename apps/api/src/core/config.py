import os

APP_NAME = os.getenv("APP_NAME", "Perplex Edge API")
APP_ENV = os.getenv("APP_ENV", "development")
PORT = int(os.getenv("PORT", "8000"))

# Using the existing SQLite database path for consistency until PostgreSQL is explicitly required
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///../../../../perplex-edge/perplex_local.db"
)

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
