from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from models.contests import Contest, ContestEntry
from models.users import User
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ContestService:
    async def get_active_contests(self, db: AsyncSession):
        """Fetch all contests that are currently live."""
        stmt = select(Contest).where(Contest.status == "active")
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_leaderboard(self, db: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generates a global leaderboard based on user performance.
        Note: In a real app we'd aggregate over BetSlips or use a pre-computed stats table.
        """
        # For demo, we'll rank users by their documented lifetime ROI if available,
        # otherwise we'll use ContestEntry scores.
        stmt = select(User).order_by(desc(User.lifetime_roi)).limit(limit)
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        leaderboard = []
        for i, u in enumerate(users):
            leaderboard.append({
                "rank": i + 1,
                "username": u.username,
                "roi": u.lifetime_roi or 0.0,
                "win_rate": 58.4, # Mocked
                "streak": 3 if i < 3 else 0,
                "tier": u.subscription_tier
            })
        return leaderboard

    async def join_contest(self, db: AsyncSession, user_id: int, contest_id: int):
        """Register a user for a specific contest."""
        # Check if already joined
        stmt = select(ContestEntry).where(
            ContestEntry.user_id == user_id,
            ContestEntry.contest_id == contest_id
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            return False, "Already joined this contest."
            
        new_entry = ContestEntry(
            user_id=user_id,
            contest_id=contest_id,
            current_score=0.0
        )
        db.add(new_entry)
        await db.commit()
        return True, "Successfully joined contest."

contest_service = ContestService()
