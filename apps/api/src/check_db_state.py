
import asyncio
import os
from sqlalchemy import select, func
from db.session import async_session_maker
from models.unified import UnifiedOdds, UnifiedEVSignal

async def check():
    async with async_session_maker() as session:
        # Check Odds
        stmt_odds = select(UnifiedOdds.sport, func.count(UnifiedOdds.id)).group_by(UnifiedOdds.sport)
        res_odds = await session.execute(stmt_odds)
        odds_counts = res_odds.all()
        print(f"UnifiedOdds Counts: {odds_counts}")

        # Check Signals
        stmt_ev = select(UnifiedEVSignal.sport, func.count(UnifiedEVSignal.id)).group_by(UnifiedEVSignal.sport)
        res_ev = await session.execute(stmt_ev)
        ev_counts = res_ev.all()
        print(f"UnifiedEVSignal Counts: {ev_counts}")
        
        # Check latest timestamps
        stmt_latest = select(func.max(UnifiedOdds.ingested_ts))
        res_latest = await session.execute(stmt_latest)
        print(f"Latest Odds TS: {res_latest.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
