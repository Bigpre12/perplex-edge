from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import text

from db.session import async_session_maker


async def try_start_job(job_key: str) -> Optional[int]:
    """Returns job_run_id if lock acquired, else None."""
    async with async_session_maker() as session:
        existing = await session.execute(
            text(
                """
                SELECT id FROM ingestion_job_runs
                WHERE job_key = :job_key
                  AND status = 'running'
                  AND started_at >= NOW() - INTERVAL '30 minutes'
                ORDER BY started_at DESC
                LIMIT 1
                """
            ),
            {"job_key": job_key},
        )
        row = existing.first()
        if row:
            return None
        ins = await session.execute(
            text(
                """
                INSERT INTO ingestion_job_runs (job_key, started_at, status)
                VALUES (:job_key, :started_at, 'running')
                RETURNING id
                """
            ),
            {"job_key": job_key, "started_at": datetime.now(timezone.utc)},
        )
        run_id = ins.scalar()
        await session.commit()
        return int(run_id) if run_id is not None else None


async def finish_job(run_id: int, *, status: str, rows_written: int = 0, error_message: Optional[str] = None) -> None:
    async with async_session_maker() as session:
        await session.execute(
            text(
                """
                UPDATE ingestion_job_runs
                SET status = :status,
                    rows_written = :rows_written,
                    error_message = :error_message,
                    completed_at = :completed_at
                WHERE id = :run_id
                """
            ),
            {
                "status": status,
                "rows_written": rows_written,
                "error_message": error_message,
                "completed_at": datetime.now(timezone.utc),
                "run_id": run_id,
            },
        )
        await session.commit()
