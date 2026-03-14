class AsyncSession: pass
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update, desc
from models.props import PropLine, PropOdds
from models.bets import BetLog # BetLog is in models.bets

logger = logging.getLogger(__name__)

class CLVService:
    async def calculate_clv(self, bet: Any, closing_line: float) -> dict:
        if not closing_line or not bet.line:
            return {'clv': 0.0, 'clv_label': 'NEUTRAL', 'beat_close': False}
        
        # In props, beat close depends on side
        if hasattr(bet, 'side') and bet.side.lower() == 'over':
            clv = round(closing_line - bet.line, 2)
        elif hasattr(bet, 'side') and bet.side.lower() == 'under':
            clv = round(bet.line - closing_line, 2)
        else:
            clv = 0.0
            
        label = 'GREAT' if clv >= 1.0 else 'GOOD' if clv >= 0.5 else 'NEUTRAL' if clv >= -0.5 else 'POOR'
        return {'clv': clv, 'clv_label': label, 'beat_close': clv > 0}

    async def settle_clv_for_user(self, user_id: str, db: AsyncSession):
        """Settle CLV for all completed bets for a user."""
        try:
            stmt = select(BetLog).where(
                BetLog.user_id == user_id, 
                BetLog.clv == None, 
                BetLog.status != 'pending'
            )
            res = await db.execute(stmt)
            bets = res.scalars().all()
            
            updated = 0
            for bet in bets:
                # Find the closing line from PropOdds (most recent update before or around game start)
                closing_stmt = select(PropOdds).where(
                    PropOdds.player_name == bet.player_name,
                    PropOdds.stat_category == bet.stat_category
                ).order_by(desc(PropOdds.updated_at))
                
                closing_res = await db.execute(closing_stmt)
                closing = closing_res.scalars().first()
                
                if not closing:
                    continue
                    
                result = await self.calculate_clv(bet, closing.line)
                bet.clv = result['clv']
                bet.clv_label = result['clv_label']
                updated += 1
                
            await db.commit()
            return updated
        except Exception as e:
            logger.error(f"Error settling CLV: {e}")
            await db.rollback()
            return 0

    async def get_clv_summary(self, user_id: str, db: AsyncSession) -> dict:
        try:
            stmt = select(BetLog).where(BetLog.user_id == user_id, BetLog.clv != None)
            res = await db.execute(stmt)
            bets = res.scalars().all()
            
            if not bets:
                return {'message': 'No CLV data available yet.'}
                
            clvs = [b.clv for b in bets if b.clv is not None]
            beat_close = sum(1 for c in clvs if c > 0)
            avg_clv = round(sum(clvs) / len(clvs), 3) if clvs else 0.0
            
            return {
                'user_id': user_id,
                'total_bets_with_clv': len(clvs),
                'avg_clv': avg_clv,
                'beat_close_pct': round(beat_close / len(clvs) * 100, 1) if clvs else 0.0,
                'skill_verdict': 'SHARP' if avg_clv >= 0.5 else 'ABOVE AVG' if avg_clv >= 0 else 'NEEDS WORK',
                'interpretation': f'You beat closing line by {avg_clv} pts on average.'
            }
        except Exception as e:
            logger.error(f"Error getting CLV summary: {e}")
            return {'error': str(e)}

    def compute_for_pick(self, pick_data: Dict, odds_history: Optional[List[Dict]] = None) -> Dict:
        """Immediate CLV calculation for a specific pick based on its provided history."""
        if not odds_history or len(odds_history) < 2:
            return {"clv_percentage": 0.0, "roi_percentage": 0.0}
            
        opening = odds_history[0].get('line_value', 0)
        closing = odds_history[-1].get('line_value', 0)
        
        if opening == 0: return {"clv_percentage": 0.0, "roi_percentage": 0.0}
        
        clv_pct = ((closing - opening) / opening) * 100
        return {
            "clv_percentage": round(clv_pct, 2),
            "roi_percentage": round(clv_pct * 1.5, 2)
        }

clv_service = CLVService()
calculate_clv = clv_service.calculate_clv
settle_clv_for_user = clv_service.settle_clv_for_user
get_clv_summary = clv_service.get_clv_summary
compute_for_pick = clv_service.compute_for_pick
