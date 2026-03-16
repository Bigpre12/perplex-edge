import logging
import json
from datetime import datetime, timezone
from sqlalchemy import select, update, desc
from sqlalchemy.orm import Session
from db.session import async_session_maker
from models.prop import PropLine, PropOdds, GameLine, GameLineOdds
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

    async def analyze_and_persist(self, props: list, sport: str):
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
                        PropLine.sport_key == sport
                    )
                    result = await session.execute(stmt)
                    existing_line = result.scalar_one_or_none()
                    
                    current_line = p['line_value']
                    current_odds_over = p.get('odds', -110)
                    current_odds_under = -110 # Default for now
                    
                    if not existing_line:
                        # NEW PROP - create and initial history
                        existing_line = PropLine(
                            player_id=str(p.get('id', hash(player_name))),
                            player_name=player_name,
                            team=p['player']['team'],
                            opponent=p['matchup']['opponent'],
                            sport_key=sport,
                            stat_type=stat_type,
                            line=current_line,
                            game_id=p.get('game_id'),
                            start_time=p.get('start_time')
                        )
                        session.add(existing_line)
                        await session.flush() # Get the ID
                    else:
                        # ALWAYS Update metadata to ensure we have current game info
                        existing_line.game_id = p.get('game_id') or existing_line.game_id
                        existing_line.start_time = p.get('start_time') or existing_line.start_time
                        existing_line.team = p['player']['team'] or existing_line.team
                        existing_line.opponent = p['matchup']['opponent'] or existing_line.opponent
                        existing_line.updated_at = datetime.now(timezone.utc)
                        
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

    async def get_sharp_signals(self, sport: str = None) -> list:
        """Fetch all props that currently have active sharp signals."""
        async with async_session_maker() as session:
            stmt = select(PropLine).where(PropLine.sharp_money == True)
            if sport:
                stmt = stmt.where(PropLine.sport_key == sport)
            
            result = await session.execute(stmt)
            return result.scalars().all()

    async def analyze_game_lines(self, lines: list, sport: str):
        """
        Takes live game lines (h2h, spreads, totals), compares with history, and persists.
        """
        async with async_session_maker() as session:
            try:
                for g in lines:
                    game_id = g.get('id')
                    home_team = g.get('home_team')
                    away_team = g.get('away_team')
                    commence_time_str = g.get('commence_time')
                    
                    commence_time = None
                    if commence_time_str:
                        try:
                            commence_time = datetime.fromisoformat(commence_time_str.replace('Z', '+00:00'))
                        except: pass

                    # Process each market: h2h, spreads, totals
                    for book in g.get('bookmakers', []):
                        b_key = book.get('key')
                        for market in book.get('markets', []):
                            m_key = market.get('key') # h2h, spreads, totals
                            
                            # 1. Find or create GameLine
                            stmt = select(GameLine).where(
                                GameLine.game_id == game_id,
                                GameLine.market_key == m_key,
                                GameLine.sport_key == sport
                            )
                            res = await session.execute(stmt)
                            existing_gl = res.scalar_one_or_none()
                            
                            if not existing_gl:
                                existing_gl = GameLine(
                                    game_id=game_id,
                                    sport_key=sport,
                                    home_team=home_team,
                                    away_team=away_team,
                                    commence_time=commence_time,
                                    market_key=m_key
                                )
                                session.add(existing_gl)
                                await session.flush()

                            # 2. Update GameLineOdds
                            stmt_odds = select(GameLineOdds).where(
                                GameLineOdds.game_line_id == existing_gl.id,
                                GameLineOdds.sportsbook == b_key
                            )
                            res_odds = await session.execute(stmt_odds)
                            existing_odds = res_odds.scalar_one_or_none()
                            
                            if not existing_odds:
                                existing_odds = GameLineOdds(
                                    game_line_id=existing_gl.id,
                                    sportsbook=b_key
                                )
                                session.add(existing_odds)

                            # Map outcomes
                            for outcome in market.get('outcomes', []):
                                name = outcome.get('name')
                                price = outcome.get('price')
                                point = outcome.get('point')
                                
                                if m_key == 'h2h':
                                    if name == home_team: existing_odds.home_price = price
                                    elif name == away_team: existing_odds.away_price = price
                                    elif name == 'Draw': existing_odds.draw_price = price
                                elif m_key == 'spreads':
                                    if name == home_team:
                                        existing_odds.home_price = price
                                        existing_odds.home_point = point
                                    elif name == away_team:
                                        existing_odds.away_price = price
                                        existing_odds.away_point = point
                                elif m_key == 'totals':
                                    if name == 'Over': existing_odds.over_price = price
                                    elif name == 'Under': existing_odds.under_price = price
                                    existing_odds.total_line = point

                            existing_odds.updated_at = datetime.now(timezone.utc)

                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"GameLines analysis failed for {sport}: {e}")

brain_odds_scout = BrainOddsScout()
