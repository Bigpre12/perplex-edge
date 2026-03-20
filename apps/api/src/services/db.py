import logging
from db.session import engine
from sqlalchemy import text

logger = logging.getLogger(__name__)

class DBWrapper:
    async def executemany(self, query: str, rows: list):
        if not rows:
            return
        async with engine.begin() as conn:
            # We convert the query to text() and execute it with the rows list
            # sqlalchemy's async execute with multiple parameter sets is roughly executemany
            try:
                await conn.execute(text(query), rows)
            except Exception as e:
                logger.error(f"DBWrapper executemany failed: {e}")
    async def fetch_all(self, query: str, params: dict = None):
        async with engine.connect() as conn:
            try:
                result = await conn.execute(text(query), params or {})
                return result.mappings().all()
            except Exception as e:
                logger.error(f"DBWrapper fetch_all failed: {e}")
                raise e

db = DBWrapper()
