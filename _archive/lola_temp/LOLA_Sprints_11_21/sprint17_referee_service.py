# backend/services/referee_service.py
# NBA referee tendency tracker
from sqlalchemy.orm import Session
from models import RefereeGame, Schedule
from typing import Optional

def get_ref_tendencies(crew: list, db: Session) -> dict:
    if not crew:
        return {'message': 'No referee data available'}
    games = db.query(RefereeGame).filter(RefereeGame.ref_name.in_(crew)).all()
    if not games:
        return {'crew': crew, 'message': 'No historical data for this crew'}
    total_fouls = [g.total_fouls for g in games]
    total_pace = [g.pace for g in games]
    total_pts = [g.total_points for g in games]
    fta_per_game = [g.fta for g in games]
    avg_fouls = round(sum(total_fouls) / len(total_fouls), 1)
    avg_pace = round(sum(total_pace) / len(total_pace), 1)
    avg_pts = round(sum(total_pts) / len(total_pts), 1)
    avg_fta = round(sum(fta_per_game) / len(fta_per_game), 1)
    foul_label = 'WHISTLE-HAPPY' if avg_fouls >= 48 else 'LET THEM PLAY' if avg_fouls <= 38 else 'AVERAGE'
    return {
        'crew': crew,
        'games_tracked': len(games),
        'avg_fouls_per_game': avg_fouls,
        'avg_pace': avg_pace,
        'avg_total_points': avg_pts,
        'avg_fta_per_game': avg_fta,
        'foul_tendency': foul_label,
        'prop_impact': {
            'free_throws': 'BOOST' if foul_label == 'WHISTLE-HAPPY' else 'REDUCE' if foul_label == 'LET THEM PLAY' else 'NEUTRAL',
            'points': 'BOOST' if avg_pts >= 230 else 'REDUCE' if avg_pts <= 210 else 'NEUTRAL',
            'pace_props': 'BOOST assists/pts' if avg_pace >= 102 else 'REDUCE pts/ast' if avg_pace <= 96 else 'NEUTRAL'
        }
    }

def get_game_refs(game_id: str, db: Session) -> list:
    game = db.query(Schedule).filter(Schedule.game_id == game_id).first()
    if not game or not game.referee_crew:
        return []
    return game.referee_crew.split(',') if game.referee_crew else []
