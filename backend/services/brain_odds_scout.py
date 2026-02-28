import logging
import json
from datetime import datetime, timezone
from sqlalchemy import select, update, desc
from sqlalchemy.orm import Session
from database import async_session_maker
from models.props import PropLine, PropOdds
from models.history import PropHistory

logger = logging.getLogger(__name__)

class BrainOddsScout:
    """
    The 'Eyes' of the Brain system. 
    Monitors line movements, detects 'Steam' (fast moves), 
    and identifies 'Sharp' signals.
    """
    
    def __init__(self, steam_threshold_line: float = 0.5, steam_threshold_odds: int = 20):
        self.steam_threshold_line = steam_threshold_line
        self.steam_threshold_odds = steam_threshold_odds

    async def analyze_and_persist(self, props: list, sport_key: str):
        """
        Takes live props, compares with history, logs deltas, and updates signals.
        Called by the props persistence background task.
        """
        async with async_session_maker() as session:
            try:
                for p in props:
                    player_name = p['player']['name']
                    stat_type = p['market']['stat_type']
                    
                    # 1. Find existing PropLine or create new
                    stmt = select(PropLine).where(
                        PropLine.player_name == player_name,
                        PropLine.stat_type == stat_type,
                        PropLine.sport_key == sport_key
                    )
                    result = await session.execute(stmt)
                    existing_line = result.scalar_one_or_none()
                    
                    current_line = p['line_value']
                    current_odds_over = p.get('odds', -110)
                    current_odds_under = -110 # Default for now
                    
                    if not existing_line:
                        # NEW PROP - create and initial history
                        new_line = PropLine(
                            player_id=str(p['id']),
                            player_name=player_name,
                            team=p['player']['team'],
                            opponent=p['matchup']['opponent'],
                            sport_key=sport_key,
                            stat_type=stat_type,
                            line=current_line,
                            game_id=p.get('game_id'),
                            start_time=p.get('start_time')
                        )
                        session.add(new_line)
                        await session.flush()
                        
                        # Add initial history snapshot
                        history = PropHistory(
                            prop_line_id=new_line.id,
                            old_line=current_line,
                            new_line=current_line,
                            old_odds_over=current_odds_over,
                            new_odds_over=current_odds_over,
                            old_odds_under=current_odds_under,
                            new_odds_under=current_odds_under,
                            change_type='initial'
                        )
                        session.add(history)
                    else:
                        # EXISTING PROP - backfill metadata if missing
                        if not existing_line.game_id:
                            existing_line.game_id = p.get('game_id')
                        if not existing_line.start_time:
                            existing_line.start_time = p.get('start_time')

                        # check for deltas
                        delta_line = abs(current_line - existing_line.line)
                        delta_odds = abs(current_odds_over - current_odds_over) # Need better odds tracking
                        
                        change_type = None
                        if delta_line >= self.steam_threshold_line:
                            change_type = 'steam_line'
                            existing_line.sharp_money = True
                            existing_line.steam_score += 1.0 # Increment steam score
                        
                        if change_type:
                            # Log history
                            history = PropHistory(
                                prop_line_id=existing_line.id,
                                old_line=existing_line.line,
                                new_line=current_line,
                                old_odds_over=0, # Placeholder
                                new_odds_over=current_odds_over,
                                change_type=change_type
                            )
                            session.add(history)
                            
                            # Update existing line
                            existing_line.line = current_line
                            existing_line.updated_at = datetime.now(timezone.utc)
                            
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"OddsScout analysis failed: {e}")

    async def get_sharp_signals(self, sport_key: str = None) -> list:
        """Fetch all props that currently have active sharp signals."""
        async with async_session_maker() as session:
            stmt = select(PropLine).where(PropLine.sharp_money == True)
            if sport_key:
                stmt = stmt.where(PropLine.sport_key == sport_key)
            
            result = await session.execute(stmt)
            return result.scalars().all()

brain_odds_scout = BrainOddsScout()
