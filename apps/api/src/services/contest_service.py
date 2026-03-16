class AsyncSession: pass
from sqlalchemy import select, desc, func
from models.contests import Contest, ContestEntry
from models.user import User
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ContestService:
    async def get_active_contests(self, db: AsyncSession):
        """Fetch all contests that are currently live."""
        stmt = select(Contest).where(Contest.status == "active")
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_contest_leaderboard(self, db: AsyncSession, contest_id: int, limit: int = 20):
        """Fetch the leaderboard for a specific contest."""
        stmt = (
            select(ContestEntry)
            .where(ContestEntry.contest_id == contest_id)
            .order_by(desc(ContestEntry.hits))
            .limit(limit)
        )
        result = await db.execute(stmt)
        entries = result.scalars().all()
        
        return [
            {
                "rank": i + 1,
                "user": e.display_name,
                "hits": e.hits,
                "total": e.total_legs,
                "hit_rate": round(e.hits / e.total_legs * 100, 1) if e.total_legs else 0,
            }
            for i, e in enumerate(entries)
        ]

    async def get_global_leaderboard(self, db: AsyncSession, limit: int = 10):
        """Standard global ROI leaderboard based on BetLog."""
        from models import BetLog
        stmt = (
            select(
                BetLog.user_id,
                func.count(BetLog.id).label("total_bets"),
                func.sum(BetLog.profit_loss).label("total_pl"),
            )
            .where(BetLog.result != "pending")
            .group_by(BetLog.user_id)
            .order_by(desc(func.sum(BetLog.profit_loss)))
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()

        return [
            {
                "rank": i + 1,
                "userid": row.user_id,
                "total_bets": row.total_bets,
                "total_pl": round(row.total_pl or 0, 2),
                "win_rate": 0.0,  # Could calculate if needed
            }
            for i, row in enumerate(rows)
        ]

    async def join_contest(self, db: AsyncSession, user_id: int, display_name: str, contest_id: int, prop_ids: List[str]):
        """Register a user for a specific contest with their prop picks."""
        import json
        
        # 1. Fetch contest to check validity
        stmt = select(Contest).where(Contest.id == contest_id)
        result = await db.execute(stmt)
        contest = result.scalar_one_or_none()
        
        if not contest or not contest.is_active:
            return False, "Contest not found or closed"
            
        if len(prop_ids) != contest.required_legs:
            return False, f"Must submit exactly {contest.required_legs} legs"

        # 2. Check if already joined
        stmt = select(ContestEntry).where(
            ContestEntry.user_id == user_id,
            ContestEntry.contest_id == contest_id
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            return False, "Already joined this contest."
            
        # 3. Create entry
        new_entry = ContestEntry(
            user_id=user_id,
            display_name=display_name,
            contest_id=contest_id,
            prop_ids_json=json.dumps(prop_ids),
            total_legs=len(prop_ids),
            hits=0,
            current_score=0.0
        )
        db.add(new_entry)
        
        # 4. Increment entry count
        contest.entry_count = (contest.entry_count or 0) + 1
        
        await db.commit()
        return True, "Successfully joined contest."

contest_service = ContestService()
