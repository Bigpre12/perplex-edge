import logging
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update, and_
from database import async_session_maker
from models.props import PropLine, PropOdds
from models.history import PropHistory
from models.brain import ModelPick

logger = logging.getLogger(__name__)

class BrainCLVTracker:
    """
    Automates performance analysis by tracking Closing Line Value (CLV).
    Compares initial pick lines vs game-time closing snapshots.
    """

    async def track_closing_lines(self, active_props: list, sport_key: str):
        """
        Snapshot closing lines as games start.
        Should be called when a game status moves to 'in_progress' or close to start time.
        """
        async with async_session_maker() as session:
            try:
                for p in active_props:
                    # Handle both PropLine objects and dictionaries
                    player_name = getattr(p, 'player_name', None) or p.get('player', {}).get('name')
                    stat_type = getattr(p, 'stat_type', None) or p.get('market', {}).get('stat_type')
                    
                    if not player_name or not stat_type:
                        continue

                    # 1. Find the PropLine in DB
                    stmt = select(PropLine).where(
                        PropLine.player_name == player_name,
                        PropLine.stat_type == stat_type,
                        PropLine.sport_key == sport_key
                    )
                    result = await session.execute(stmt)
                    db_prop = result.scalar_one_or_none()
                    
                    if not db_prop:
                        continue

                    # 2. Get the last history entry (Closing Line)
                    hist_stmt = select(PropHistory).where(
                        PropHistory.prop_line_id == db_prop.id
                    ).order_by(PropHistory.timestamp.desc()).limit(1)
                    
                    hist_result = await session.execute(hist_stmt)
                    last_hist = hist_result.scalar_one_or_none()
                    
                    if last_hist:
                        closing_line = last_hist.new_line
                        clv_delta = closing_line - db_prop.line
                        beat_clv = clv_delta > 0
                            
                        # Update DB
                        db_prop.closing_line = closing_line
                        db_prop.clv_val = clv_delta
                        db_prop.beat_closing_line = beat_clv
                        
                        # 4. Enrich any associated ModelPicks
                        pick_stmt = select(ModelPick).where(
                            ModelPick.player_name == player_name,
                            ModelPick.stat_type == stat_type,
                            ModelPick.sport == sport_key,
                            ModelPick.status == 'pending'
                        )
                        pick_result = await session.execute(pick_stmt)
                        picks = pick_result.scalars().all()
                        
                        for pick in picks:
                            pick.closing_odds = last_hist.new_odds_over or pick.odds
                            pick.line_movement = clv_delta
                            pick.clv_percentage = (clv_delta / db_prop.line * 100) if db_prop.line else 0
                
                await session.commit()
                logger.info(f"CLV Tracking complete for {len(active_props)} props in {sport_key}")
            except Exception as e:
                await session.rollback()
                logger.error(f"CLV Tracking failed: {e}")

brain_clv_tracker = BrainCLVTracker()
