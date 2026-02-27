# backend/services/h2h_service.py
# Head-to-Head historical splits and Back-to-Back detection
from sqlalchemy.orm import Session
from models import PlayerStats, Schedule
from datetime import datetime, timedelta
from typing import Optional

def get_h2h_splits(player_id: str, opponent_team: str, stat_category: str,
                   db: Session, seasons: int = 3) -> dict:
    cutoff = datetime.utcnow() - timedelta(days=365 * seasons)
    games = db.query(PlayerStats).filter(
        PlayerStats.player_id == player_id,
        PlayerStats.stat_category == stat_category,
        PlayerStats.opponent_team == opponent_team,
        PlayerStats.game_date >= cutoff
    ).order_by(PlayerStats.game_date.desc()).all()
    if not games:
        return {'games': 0, 'avg': None, 'message': 'No H2H data'}
    values = [g.value for g in games]
    return {
        'player_id': player_id,
        'opponent': opponent_team,
        'stat': stat_category,
        'games': len(values),
        'avg': round(sum(values) / len(values), 2),
        'max': max(values),
        'min': min(values),
        'last_3': [round(v, 1) for v in values[:3]],
        'last_5': [round(v, 1) for v in values[:5]],
    }

def check_back_to_back(player_id: str, game_date: str, db: Session) -> dict:
    game_dt = datetime.strptime(game_date, '%Y-%m-%d')
    yesterday = (game_dt - timedelta(days=1)).strftime('%Y-%m-%d')
    two_ago = (game_dt - timedelta(days=2)).strftime('%Y-%m-%d')
    played_yesterday = db.query(PlayerStats).filter(
        PlayerStats.player_id == player_id,
        PlayerStats.game_date == yesterday
    ).first()
    played_two_ago = db.query(PlayerStats).filter(
        PlayerStats.player_id == player_id,
        PlayerStats.game_date == two_ago
    ).first()
    is_b2b = played_yesterday is not None
    is_3_in_4 = played_yesterday and played_two_ago
    rest_days = 0 if is_b2b else (1 if not played_two_ago else 0)
    return {
        'is_back_to_back': is_b2b,
        'is_3_in_4_nights': bool(is_3_in_4),
        'rest_days': rest_days,
        'fatigue_flag': is_b2b or bool(is_3_in_4),
        'fatigue_label': '🚨 B2B' if is_b2b else '⚠️ 3-in-4' if is_3_in_4 else '✅ Rested',
        'prop_impact': 'REDUCE UNIT SIZE — fatigue risk' if is_b2b else 'Monitor — slight fatigue' if is_3_in_4 else 'No fatigue concern'
    }

def get_home_away_splits(player_id: str, stat_category: str, db: Session) -> dict:
    games = db.query(PlayerStats).filter(
        PlayerStats.player_id == player_id,
        PlayerStats.stat_category == stat_category
    ).all()
    home = [g.value for g in games if g.is_home]
    away = [g.value for g in games if not g.is_home]
    return {
        'home_avg': round(sum(home) / len(home), 2) if home else None,
        'away_avg': round(sum(away) / len(away), 2) if away else None,
        'home_games': len(home),
        'away_games': len(away),
        'home_advantage': round((sum(home)/len(home)) - (sum(away)/len(away)), 2) if home and away else None
    }
