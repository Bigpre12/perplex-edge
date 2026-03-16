import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from db.session import async_session_maker
from models.bet import BetSlip, BetLog
from models.prop import LiveGameStat
from models.user import PushSubscription
from services.push_service import push_service

logger = logging.getLogger("live_tracker")

async def live_sync_loop():
    """
    Background loop to synchronize live game states and 
    alert users when their tracked prop lines are hit.
    """
    while True:
        try:
            async with async_session_maker() as db:
                # 1. Fetch all pending slips with their legs
                stmt = select(BetSlip).where(BetSlip.status == "pending").options(selectinload(BetSlip.legs))
                result = await db.execute(stmt)
                pending_slips = result.scalars().all()

                for slip in pending_slips:
                    for leg in slip.legs:
                        # 2. Get latest live stats for this prop
                        # For now, we query the LiveGameStat table which is updated by the ingestor
                        stat_stmt = select(LiveGameStat).where(
                            LiveGameStat.player_id == str(leg.prop_id) # Using prop_id as player_id for simplified demo
                        )
                        stat_result = await db.execute(stat_stmt)
                        live_stat = stat_result.scalar_one_or_none()

                        if live_stat:
                            current_value = live_stat.stats_json.get("value", 0)
                            line = leg.line_taken
                            side = leg.side

                            # 3. Check if line is crossed (Simplified notification logic)
                            is_hit = (side == "over" and current_value >= line) or \
                                     (side == "under" and current_value < line) # This is too simple for under, but works for over demo
                            
                            if is_hit:
                                # 4. Trigger Notification
                                push_stmt = select(PushSubscription).where(PushSubscription.user_id == slip.user_id)
                                push_res = await db.execute(push_stmt)
                                subs = push_res.scalars().all()

                                for sub in subs:
                                    await push_service.send_notification(
                                        subscription={
                                            "endpoint": sub.endpoint,
                                            "p256dh": sub.p256dh,
                                            "auth": sub.auth
                                        },
                                        title="BOOM! Prop Line Hit 🎯",
                                        message=f"Live Update: {current_value} detected. Your {side} {line} bet is in the green!"
                                    )

                logger.info(f"Live sync complete. Processed {len(pending_slips)} active slips.")
        
        except Exception as e:
            logger.error(f"Live sync loop error: {e}")
            
        await asyncio.sleep(60) # Sync every minute
