import asyncio
import os
import sys

# Add src to path so we can import internal modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlmodel import SQLModel
from db.session import async_engine
from models import sql_models # Ensure models are imported for metadata collection

async def init_db():
    print("🚀 Initializing SQLModel tables...")
    async with async_engine.begin() as conn:
        # This will create tables for all models that inherit from SQLModel
        await conn.run_sync(SQLModel.metadata.create_all)
    print("✅ SQLModel tables initialized successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())
