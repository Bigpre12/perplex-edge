import asyncio
import os
import logging
from sqlalchemy import text
from db.session import async_session_maker, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_migrations():
    async with async_session_maker() as session:
        is_sqlite = "sqlite" in str(engine.url)
        logger.info(f"Connected to {'SQLite' if is_sqlite else 'PostgreSQL'}")

        if not is_sqlite:
            # 1. Fix props_history columns
            logger.info("Checking props_history columns...")
            columns_to_add = [
                ("is_best_over", "BOOLEAN DEFAULT FALSE"),
                ("is_best_under", "BOOLEAN DEFAULT FALSE"),
                ("is_soft_book", "BOOLEAN DEFAULT FALSE"),
                ("is_sharp_book", "BOOLEAN DEFAULT FALSE"),
                ("confidence", "FLOAT")
            ]
            for col, col_type in columns_to_add:
                try:
                    await session.execute(text(f"ALTER TABLE props_history ADD COLUMN {col} {col_type}"))
                    logger.info(f"Added column {col} to props_history")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.info(f"Column {col} already exists in props_history")
                    else:
                        logger.error(f"Error adding {col}: {e}")

            # 2. Fix ev_signals constraint
            logger.info("Ensuring ev_signals unique constraint...")
            try:
                # First, drop any existing constraint to avoid duplicates if partially correctly named
                # But let's just try to add the one we need.
                # ON CONFLICT in code uses: (sport, event_id, market_key, outcome_key, bookmaker, engine_version)
                await session.execute(text("""
                    ALTER TABLE ev_signals 
                    ADD CONSTRAINT uix_ev_unique 
                    UNIQUE (sport, event_id, market_key, outcome_key, bookmaker, engine_version)
                """))
                logger.info("Added uix_ev_unique constraint to ev_signals")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info("Unique constraint uix_ev_unique already exists in ev_signals")
                else:
                    logger.error(f"Error adding constraint: {e}")

        await session.commit()
    logger.info("Migrations complete.")

if __name__ == "__main__":
    asyncio.run(run_migrations())
