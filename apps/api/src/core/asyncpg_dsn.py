"""
Normalize DATABASE_URL for asyncpg.connect().

SQLAlchemy uses postgresql+asyncpg://...; asyncpg expects postgresql:// or postgres://.
Matches host/ssl/pooler behavior in db/session.py so ORM and raw asyncpg hit the same target.
"""
import re
import logging

logger = logging.getLogger(__name__)


def asyncpg_dsn_from_database_url(database_url: str) -> str:
    """Convert DATABASE_URL (any common variant) to a DSN asyncpg.connect() accepts."""
    if not database_url or not str(database_url).strip():
        return ""
    url = str(database_url).strip()

    # Mirror db/session.py: coerce schemes before stripping driver suffix
    if url.startswith("sqlite"):
        if "aiosqlite" not in url:
            url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and "asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if "sslmode=" in url:
        url = re.sub(r"[?&]sslmode=[^&]*", "", url)
        if "&" in url and "?" not in url:
            url = url.replace("&", "?", 1)

    if "postgresql" in url and "pooler" in url and ":5432" in url:
        logger.info(
            "Switching Supabase pooler from Session Mode (5432) to Transaction Mode (6543) (asyncpg DSN)"
        )
        url = url.replace(":5432", ":6543", 1)

    url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    return url
