# backend/services/clv_service.py
# Closing Line Value tracker — measures if line moved in your favor after bet
from sqlalchemy.orm import Session
from models import BetLog, PropOdds
from datetime import datetime
from typing import Dict, Any, List, Optional

class CLVService:
    def calculate_clv(self, bet: BetLog, closing_line: float) -> dict:
        if not closing_line or not bet.line:
            return {'clv': None, 'clv_label': 'Unknown'}
        if bet.side == 'over':
            clv = round(closing_line - bet.line, 2)
        else:
            clv = round(bet.line - closing_line, 2)
        label = 'GREAT' if clv >= 1.0 else 'GOOD' if clv >= 0.5 else 'NEUTRAL' if clv >= -0.5 else 'POOR'
        return {'clv': clv, 'clv_label': label, 'beat_close': clv > 0}

    def settle_clv_for_user(self, user_id: str, db: Session):
        bets = db.query(BetLog).filter(BetLog.user_id == user_id, BetLog.clv == None, BetLog.status != 'pending').all()
        updated = 0
        for bet in bets:
            closing = db.query(PropOdds).filter(
                PropOdds.player_name == bet.player_name,
                PropOdds.stat_category == bet.stat_category
            ).order_by(PropOdds.updated_at.desc()).first()
            if not closing:
                continue
            result = self.calculate_clv(bet, closing.line)
            bet.clv = result['clv']
            bet.clv_label = result['clv_label']
            updated += 1
        db.commit()
        return updated

    def get_clv_summary(self, user_id: str, db: Session) -> dict:
        bets = db.query(BetLog).filter(BetLog.user_id == user_id, BetLog.clv != None).all()
        if not bets:
            return {'message': 'No CLV data yet'}
        clvs = [b.clv for b in bets if b.clv is not None]
        beat_close = sum(1 for c in clvs if c > 0)
        avg_clv = round(sum(clvs) / len(clvs), 3)
        return {
            'user_id': user_id,
            'total_bets_with_clv': len(clvs),
            'avg_clv': avg_clv,
            'beat_close_pct': round(beat_close / len(clvs) * 100, 1),
            'skill_verdict': 'SHARP' if avg_clv >= 0.5 else 'ABOVE AVG' if avg_clv >= 0 else 'NEEDS WORK',
            'interpretation': f'You beat closing line by {avg_clv} pts on average. {"This indicates genuine edge." if avg_clv > 0 else "Negative CLV suggests timing or line selection issues."}'
        }
        
    def compute_for_pick(self, pick_data: Dict, odds_history: Optional[List[Dict]] = None, odds_by_book: Optional[Dict] = None, public_pct: Optional[float] = None) -> Dict:
        """
        Compute CLV percentage based on line movement.
        """
        if not odds_history or len(odds_history) < 2:
            return {"clv_percentage": 0.0, "roi_percentage": 0.0}
            
        opening = odds_history[0].get('line_value', 0)
        closing = odds_history[-1].get('line_value', 0)
        
        if opening == 0: return {"clv_percentage": 0.0, "roi_percentage": 0.0}
        
        # Simple CLV = (Closing Line - Opening Line) / Opening Line
        clv_pct = ((closing - opening) / opening) * 100
        return {
            "clv_percentage": round(clv_pct, 2),
            "roi_percentage": round(clv_pct * 1.5, 2) # Est ROI multiplier
        }
        
    def summary(self, picks: List[Dict]) -> Dict:
        if not picks:
            return {"avg_clv": 0.0, "positive_clv_pct": 0.0}
        clvs = [p.get('clv_percentage', 0) for p in picks]
        pos = sum(1 for c in clvs if c > 0)
        return {
            "avg_clv": round(sum(clvs) / len(clvs), 2),
            "positive_clv_pct": round((pos / len(picks)) * 100, 1) if picks else 0
        }

# Instantiate service
clv_service = CLVService()
