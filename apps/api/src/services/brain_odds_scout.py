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
                    
                    print(f"DEBUG: Processing {player_name} | {stat_type} | Line: {current_line}")

                    if not existing_line:
                        # NEW PROP - create and initial history
                        print(f"DEBUG: Creating NEW PropLine for {player_name}")
                        existing_line = PropLine(
                            player_id=str(p.get('id', hash(player_name))),
                            player_name=player_name,
                            team=p['player']['team'],
                            opponent=p['matchup']['opponent'],
                            sport_key=sport_key,
                            stat_type=stat_type,
                            line=current_line,
                            game_id=p.get('game_id'),
                            start_time=p.get('start_time')
                        )
                        session.add(existing_line)
                        await session.flush() # Get the ID
                    else:
                        print(f"DEBUG: Updating EXISTING PropLine for {player_name}")
                        # Update metadata if missing
                        if not existing_line.game_id: existing_line.game_id = p.get('game_id')
                        if not existing_line.start_time: existing_line.start_time = p.get('start_time')
                        
                        # check for deltas (Steam detection)
                        delta_line = abs(current_line - existing_line.line)
                        if delta_line >= self.steam_threshold_line:
                            history = PropHistory(
                                prop_line_id=existing_line.id,
                                old_line=existing_line.line,
                                new_line=current_line,
                                change_type='steam_line'
                            )
                            session.add(history)
                            existing_line.line = current_line
                            existing_line.sharp_money = True
                            existing_line.steam_score += 1.0
                            existing_line.updated_at = datetime.now(timezone.utc)

                    # 2. Update PropOdds for each bookmaker
                    for b_key, b_data in p.get('books', {}).items():
                        # Find existing odds for this book
                        stmt_odds = select(PropOdds).where(
                            PropOdds.prop_line_id == existing_line.id,
                            PropOdds.sportsbook == b_key
                        )
                        res_odds = await session.execute(stmt_odds)
                        existing_odds = res_odds.scalar_one_or_none()
                        
                        if not existing_odds:
                            new_odds = PropOdds(
                                prop_line_id=existing_line.id,
                                sportsbook=b_key,
                                over_odds=int(b_data['over']),
                                under_odds=int(b_data['under']),
                                updated_at=datetime.now(timezone.utc)
                            )
                            session.add(new_odds)
                        else:
                            existing_odds.over_odds = int(b_data['over'])
                            existing_odds.under_odds = int(b_data['under'])
                            existing_odds.updated_at = datetime.now(timezone.utc)

                await session.commit()
                print("DEBUG: Session committed successfully")
            except Exception as e:
                await session.rollback()
                import traceback
                traceback.print_exc()
                print(f"DEBUG: Analysis failed: {e}")
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
