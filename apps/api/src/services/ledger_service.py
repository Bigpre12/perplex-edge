class AsyncSession: pass
from models import BetSlip, BetLog, BetLeg, BetResult
from models.user import User
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import List
import logging

logger = logging.getLogger(__name__)

class LedgerService:
    async def track_bet(self, db: AsyncSession, user_id: str, slip_data: dict, legs: List[dict]):
        """
        Track a new bet slip with multiple legs.
        """
        # Create BetSlip
        new_slip = BetSlip(
            user_id=user_id,
            slip_type=slip_data.get("slip_type", "straight"),
            sportsbook=slip_data.get("sportsbook"),
            total_odds=slip_data.get("total_odds"),
        )
        db.add(new_slip)
        await db.flush() # Get ID
        
        # Create Legs
        for leg in legs:
            new_leg = BetLeg(
                slip_id=new_slip.id,
                prop_id=leg.get("prop_id"),
                side=leg.get("side"),
                odds_taken=leg.get("odds_taken"),
                line_taken=leg.get("line_taken")
            )
            db.add(new_leg)
        
        await db.commit()
        await db.refresh(new_slip)
        return new_slip

    async def get_user_ledger(self, db: AsyncSession, user_id: str):
        """Fetch all bets for a user with legs."""
        stmt = select(BetSlip).where(BetSlip.user_id == user_id).options(selectinload(BetSlip.legs)).order_by(BetSlip.placed_at.desc())
        result = await db.execute(stmt)
        slips = result.scalars().all()
        return slips

    async def get_user_stats(self, db: AsyncSession, user_id: str):
        """Calculate ROI, Win Rate, Heatmaps, and Risk/Reward data."""
        from models.prop import PropLine
        
        # 1. Fetch all slips for the user
        stmt = select(BetSlip).where(BetSlip.user_id == user_id).options(selectinload(BetSlip.legs))
        result = await db.execute(stmt)
        slips = result.scalars().all()
        
        if not slips:
            return {
                "total_bets": 0, "win_rate": 0, "profit_loss": 0,
                "heatmaps": {"by_sport": [], "by_market": []},
                "risk_reward": []
            }

        slip_ids = [s.id for s in slips]
        
        # 2. Fetch all legs and join with PropLine for sport/stat info
        legs_stmt = select(BetLeg, PropLine).join(PropLine, BetLeg.prop_id == PropLine.id).where(BetLeg.slip_id.in_(slip_ids))
        legs_result = await db.execute(legs_stmt)
        legs_data = legs_result.all()

        # Aggregators
        stats = {
            "total_bets": len(slips),
            "wins": len([s for s in slips if s.status == "won"]),
            "losses": len([s for s in slips if s.status == "lost"]),
            "by_sport": {}, 
            "by_market": {}, 
            "risk_reward": []
        }

        # Helper to calculate profit for a slip (1 unit assumption)
        def get_slip_profit(slip: BetSlip):
            if slip.status == "won":
                odds = slip.total_odds
                if not odds: return 0.0
                return (odds/100) if odds > 0 else (100/abs(odds))
            elif slip.status == "lost":
                return -1.0
            return 0.0

        for slip in slips:
            profit = get_slip_profit(slip)
            
            # Find legs for this slip to aggregate sport/market
            slip_legs = [l for l in legs_data if l[0].slip_id == slip.id]
            div = len(slip_legs) if slip_legs else 1
            for leg, prop in slip_legs:
                sport = prop.sport_key or "Unknown"
                market = prop.stat_type or "Unknown"
                
                # aggregate sport
                if sport not in stats["by_sport"]: stats["by_sport"][sport] = {"profit": 0, "bets": 0}
                stats["by_sport"][sport]["profit"] += profit / div 
                stats["by_sport"][sport]["bets"] += 1
                
                # aggregate market
                if market not in stats["by_market"]: stats["by_market"][market] = {"profit": 0, "bets": 0}
                stats["by_market"][market]["profit"] += profit / div
                stats["by_market"][market]["bets"] += 1

            # Scatter plot data: odds vs profit
            stats["risk_reward"].append({
                "odds": slip.total_odds,
                "profit": profit,
                "status": slip.status,
                "date": slip.placed_at.isoformat() if slip.placed_at else None
            })

        # Format heatmaps for frontend
        sport_heatmap = [
            {"label": k, "value": round(v["profit"], 2), "intensity": min(1, max(0, (v["profit"] + 5) / 10))}
            for k, v in stats["by_sport"].items()
        ]
        
        market_heatmap = [
            {"label": k, "value": round(v["profit"], 2), "intensity": min(1, max(0, (v["profit"] + 5) / 10))}
            for k, v in stats["by_market"].items()
        ]

        from services.risk_service import RiskService
        
        total_profit = sum(get_slip_profit(s) for s in slips)

        # 3. Calculate Balance History & Drawdown (Starting with 100 units)
        balance_history = [100.0]
        current_balance = 100.0
        sorted_slips = sorted([s for s in slips if s.placed_at], key=lambda x: x.placed_at)
        for slip in sorted_slips:
            current_balance += get_slip_profit(slip)
            balance_history.append(current_balance)
        
        max_dd = RiskService.calculate_max_drawdown(balance_history)

        # 4. Calculate Risk of Ruin
        win_rate_raw = (stats["wins"] / stats["total_bets"]) if stats["total_bets"] > 0 else 0
        ror = RiskService.calculate_risk_of_ruin(win_rate_raw, 0.03, 100)

        return {
            "total_bets": stats["total_bets"],
            "win_rate": round((stats["wins"] / stats["total_bets"] * 100), 1) if stats["total_bets"] > 0 else 0,
            "profit_loss": round(total_profit, 2),
            "risk_metrics": {
                "max_drawdown": f"{max_dd}%",
                "risk_of_ruin": f"{ror}%",
                "stability_score": round(max(0, 100 - max_dd - ror), 1),
                "alerts": [
                    "High Risk of Ruin. Consider reducing unit size." if ror > 20 else None,
                    "Significant Drawdown detected. Review strategy volatility." if max_dd > 15 else None
                ]
            },
            "heatmaps": {
                "by_sport": sorted(sport_heatmap, key=lambda x: x["value"], reverse=True),
                "by_market": sorted(market_heatmap, key=lambda x: x["value"], reverse=True)
            },
            "risk_reward": stats["risk_reward"]
        }

    async def settle_pending_bets(self, db: AsyncSession):
        """Find pending bets and settle them against player_stats table."""
        from services.player_stats_service import player_stats_service
        
        # Get pending slips
        stmt = select(BetSlip).where(BetSlip.status == "pending")
        result = await db.execute(stmt)
        pending_slips = result.scalars().all()
        
        settled_count = 0
        for slip in pending_slips:
            # Load legs explicitly if not already loaded
            stmt_legs = select(BetLeg).where(BetLeg.slip_id == slip.id)
            res_legs = await db.execute(stmt_legs)
            legs = res_legs.scalars().all()
            
            leg_results = []
            for leg in legs:
                stats = await player_stats_service.search_player_stats(
                    query=f"{leg.prop_id}", 
                    limit=1
                )
                
                if stats:
                    stat = stats[0]
                    actual = stat.get('actual_value', 0)
                    line = leg.line_taken
                    side = leg.side
                    
                    is_win = False
                    if side == "over" and actual > line: is_win = True
                    elif side == "under" and actual < line: is_win = True
                    
                    # We might want to store leg status too, but for now we just track it
                    leg_results.append("won" if is_win else "lost")
            
            if leg_results:
                if all(r == "won" for r in leg_results):
                    slip.status = "won"
                elif any(r == "lost" for r in leg_results):
                    slip.status = "lost"
                settled_count += 1
        
        await db.commit()
        return settled_count

ledger_service = LedgerService()
