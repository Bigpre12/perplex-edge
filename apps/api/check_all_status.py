
import asyncio
import os
import json
from sqlalchemy import text
from db.session import async_session_maker

async def check_all():
    async with async_session_maker() as session:
        # Check all heartbeats
        res = await session.execute(text("SELECT feed_name, last_run_at, status, meta FROM heartbeats ORDER BY last_run_at DESC"))
        hbs = res.fetchall()
        for hb in hbs:
            meta = hb[3]
            if isinstance(meta, str):
                try:
                    meta = json.loads(meta)
                except:
                    pass
            error = "None"
            if isinstance(meta, dict):
                error = meta.get("error", "None")
            elif meta:
                error = str(meta)
            print(f"HB: {hb[0]} | Status: {hb[2]} | Error: {error}")

if __name__ == "__main__":
    asyncio.run(check_all())
