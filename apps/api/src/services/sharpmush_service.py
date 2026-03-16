class AsyncSession: pass
# backend/services/sharpmush_service.py
# LOLA Smart Money — aggregate signal from top-performing community users
from sqlalchemy import select, func
from models.bet import BetLog
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class SharpMushService:
    async def identify_sharp_users(self, db: AsyncSession, sport: str = None, min_bets: int = 5, min_roi: float = 2.0) -> list:
        since = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = select(BetLog).where(BetLog.placed_at >= since, BetLog.result != 'pending')
        
        if sport and sport != "all":
            stmt = stmt.where(BetLog.sport == sport)
        
        res = await db.execute(stmt)
        bets = res.scalars().all()
        
        user_stats = defaultdict(lambda: {'bets': 0, 'wins': 0, 'profit': 0.0})
        for b in bets:
            user_stats[b.user_id]['bets'] += 1
            user_stats[b.user_id]['wins'] += 1 if b.result == 'win' else 0
            user_stats[b.user_id]['profit'] += b.profit_loss or 0
        
        sharp_users = []
        for uid, s in user_stats.items():
            if s['bets'] < min_bets:
                continue
            roi = (s['profit'] / (s['bets'] * 1.0)) * 100 if s['bets'] > 0 else 0
            if roi >= min_roi:
                sharp_users.append({'user_id': uid, 'bets': s['bets'], 'roi': round(roi, 2)})
        
        sharp_users.sort(key=lambda x: x['roi'], reverse=True)
        return sharp_users

    async def get_smart_money_signal(self, db: AsyncSession, sport: str = "basketball_nba", top_n: int = 10) -> list:
        sharp_users = await self.identify_sharp_users(db, sport=sport)
        if not sharp_users:
            return []
        
        top_user_ids = [u['user_id'] for u in sharp_users[:top_n]]
        since = datetime.now(timezone.utc) - timedelta(hours=48)
        
        stmt = select(BetLog).where(
            BetLog.user_id.in_(top_user_ids),
            BetLog.placed_at >= since
        )
        if sport and sport != "all":
            stmt = stmt.where(BetLog.sport == sport)
            
        res = await db.execute(stmt)
        recent_bets = res.scalars().all()
        
        prop_votes = defaultdict(lambda: {'over': 0, 'under': 0, 'player': '', 'stat': '', 'line': 0})
        for b in recent_bets:
            player_name = getattr(b, 'player_name', 'Unknown')
            stat_type = getattr(b, 'stat_category', 'Stat')
            
            k = f"{getattr(b, 'player_id', '0')}_{stat_type}"
            prop_votes[k][b.side.lower()] += 1
            prop_votes[k]['player'] = player_name
            prop_votes[k]['stat'] = stat_type
            prop_votes[k]['line'] = getattr(b, 'line', 0)
            
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

sharpmush_service = SharpMushService()
identify_sharp_users = sharpmush_service.identify_sharp_users
get_smart_money_signal = sharpmush_service.get_smart_money_signal
