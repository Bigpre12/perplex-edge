"""
Verify Postgres connectivity using the same DSN rules as production asyncpg paths.

Run from repo root or apps/api (with cwd on PYTHONPATH):

  cd apps/api/src && py test_asyncpg_connect.py

Or on Railway shell (same env as the service):

  cd /app && python -m scripts.test_asyncpg_connect

Requires DATABASE_URL. Skips with message if URL is sqlite.
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.asyncpg_dsn import asyncpg_dsn_from_database_url


async def main() -> None:
    raw = os.getenv("DATABASE_URL", "").strip()
    if not raw:
        print("FAIL: DATABASE_URL is not set")
        sys.exit(1)
    if raw.startswith("sqlite") or "sqlite" in raw.split(":", 1)[0].lower():
        print("SKIP: DATABASE_URL is sqlite (use SQLAlchemy for local checks)")
        sys.exit(0)

    url = asyncpg_dsn_from_database_url(raw)
    try:
        import asyncpg

        conn = await asyncpg.connect(url)
        try:
            await conn.execute("SELECT 1")
        finally:
            await conn.close()
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
    print("OK: asyncpg connected; SELECT 1 succeeded")


if __name__ == "__main__":
    asyncio.run(main())
