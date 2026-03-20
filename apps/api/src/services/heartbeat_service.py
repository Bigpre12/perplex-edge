from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from models.heartbeat import Heartbeat
import logging

logger = logging.getLogger(__name__)

class HeartbeatService:
    @staticmethod
    async def log_heartbeat(
        db: AsyncSession,
        feed_name: str,
        status: str = "ok",
        rows_written: int = 0,
        error_count: int = 0,
        meta: dict = None
    ):
        """Update or create a heartbeat record for a given feed."""
        try:
            stmt = select(Heartbeat).where(Heartbeat.feed_name == feed_name)
            res = await db.execute(stmt)
            record = res.scalar_one_none()
            
            now = datetime.now(timezone.utc)
            
            if record:
                record.last_run_at = now
                if status == "ok":
                    record.last_success_at = now
                record.rows_written_today += rows_written
                record.error_count_today += error_count
                record.status = status
                if meta:
                    record.meta = {**(record.meta or {}), **meta}
            else:
                new_record = Heartbeat(
                    feed_name=feed_name,
                    last_run_at=now,
                    last_success_at=now if status == "ok" else None,
                    rows_written_today=rows_written,
                    error_count_today=error_count,
                    status=status,
                    meta=meta
                )
                db.add(new_record)
            
            await db.commit()
        except Exception as e:
            logger.error(f"Failed to log heartbeat for {feed_name}: {e}")
            await db.rollback()

    @staticmethod
    async def get_all_heartbeats(db: AsyncSession):
        stmt = select(Heartbeat)
        res = await db.execute(stmt)
        return res.scalars().all()
    
    @staticmethod
    async def get_heartbeat(db: AsyncSession, feed_name: str):
        stmt = select(Heartbeat).where(Heartbeat.feed_name == feed_name)
        res = await db.execute(stmt)
        return res.scalar_one_none()
