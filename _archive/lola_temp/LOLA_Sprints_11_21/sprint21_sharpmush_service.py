# backend/services/sharpmush_service.py
# LOLA Smart Money — aggregate signal from top-performing community users
from sqlalchemy.orm import Session
from models import BetLog
from datetime import datetime, timedelta
from collections import defaultdict

def identify_sharp_users(db: Session, min_bets: int = 20, min_roi: float = 5.0) -> list:
    since = datetime.utcnow() - timedelta(days=30)
    bets = db.query(BetLog).filter(BetLog.created_at >= since, BetLog.status != 'pending').all()
    user_stats = defaultdict(lambda: {'bets': 0, 'wins': 0, 'profit': 0.0})
    for b in bets:
        user_stats[b.user_id]['bets'] += 1
        user_stats[b.user_id]['wins'] += 1 if b.status == 'won' else 0
        user_stats[b.user_id]['profit'] += b.profit_units or 0
    sharp_users = []
    for uid, s in user_stats.items():
        if s['bets'] < min_bets:
            continue
        roi = s['profit'] / s['bets'] * 100
        if roi >= min_roi:
            sharp_users.append({'user_id': uid, 'bets': s['bets'], 'roi': round(roi, 2)})
    sharp_users.sort(key=lambda x: x['roi'], reverse=True)
    return sharp_users

def get_smart_money_signal(db: Session, top_n: int = 10) -> list:
    sharp_users = identify_sharp_users(db)
    if not sharp_users:
        return []
    top_user_ids = [u['user_id'] for u in sharp_users[:top_n]]
    since = datetime.utcnow() - timedelta(hours=24)
    recent_bets = db.query(BetLog).filter(
        BetLog.user_id.in_(top_user_ids),
        BetLog.created_at >= since
    ).all()
    prop_votes = defaultdict(lambda: {'over': 0, 'under': 0, 'player': '', 'stat': '', 'line': 0})
    for b in recent_bets:
        k = f'{b.player_id}_{b.stat_category}'
        prop_votes[k][b.side.lower()] += 1
        prop_votes[k]['player'] = b.player_name
        prop_votes[k]['stat'] = b.stat_category
        prop_votes[k]['line'] = b.line
    signals = []
    for k, v in prop_votes.items():
        total = v['over'] + v['under']
        if total < 2:
            continue
        over_pct = round(v['over'] / total * 100, 1)
        signals.append({
            'player': v['player'], 'stat': v['stat'], 'line': v['line'],
            'sharp_over_pct': over_pct, 'sharp_under_pct': round(100 - over_pct, 1),
            'sharp_bettors_count': total,
            'smart_money_side': 'OVER' if over_pct >= 60 else 'UNDER' if over_pct <= 40 else 'MIXED',
            'signal_strength': 'STRONG' if total >= 5 and (over_pct >= 80 or over_pct <= 20) else 'MODERATE' if total >= 3 else 'WEAK'
        })
    signals.sort(key=lambda x: x['sharp_bettors_count'], reverse=True)
    return signals
