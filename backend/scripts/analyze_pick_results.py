#!/usr/bin/env python3
"""
PICK RESULTS ANALYSIS - Comprehensive analysis of the pick_results table
"""
import asyncio
import asyncpg
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import json

async def analyze_pick_results():
    """Analyze the pick_results table structure and data"""
    
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found")
        return
    
    try:
        conn = await asyncpg.connect(db_url)
        print("Connected to database")
        
        # Get all pick results data
        pick_results = await conn.fetch("""
            SELECT * FROM pick_results 
            ORDER BY settled_at DESC, id DESC
            LIMIT 100
        """)
        
        print("PICK RESULTS TABLE ANALYSIS")
        print("="*80)
        
        print(f"\nTotal Pick Results: {len(pick_results)}")
        
        # Analyze hit rates
        hits = await conn.fetchrow("""
            SELECT 
                COUNT(*) as total_picks,
                COUNT(CASE WHEN hit = true THEN 1 END) as hits,
                COUNT(CASE WHEN hit = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN hit = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                SUM(profit_loss) as total_profit_loss,
                ROUND(AVG(profit_loss), 2) as avg_profit_loss,
                ROUND(AVG(clv_cents), 2) as avg_clv_cents
            FROM pick_results
        """)
        
        print(f"\nOverall Performance:")
        print(f"  Total Picks: {hits['total_picks']}")
        print(f"  Hits: {hits['hits']}")
        print(f"  Misses: {hits['misses']}")
        print(f"  Hit Rate: {hits['hit_rate_percentage']:.2f}%")
        print(f"  Total P&L: ${hits['total_profit_loss']:.2f}")
        print(f"  Avg P&L: ${hits['avg_profit_loss']:.2f}")
        print(f"  Avg CLV: {hits['avg_clv_cents']:.2f} cents")
        
        # Analyze by player
        by_player = await conn.fetch("""
            SELECT 
                player_id,
                COUNT(*) as total_picks,
                COUNT(CASE WHEN hit = true THEN 1 END) as hits,
                COUNT(CASE WHEN hit = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN hit = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                SUM(profit_loss) as total_profit_loss,
                ROUND(AVG(profit_loss), 2) as avg_profit_loss,
                ROUND(AVG(clv_cents), 2) as avg_clv_cents,
                MIN(settled_at) as first_pick,
                MAX(settled_at) as last_pick
            FROM pick_results
            GROUP BY player_id
            ORDER BY total_profit_loss DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Players by Profit:")
        for player in by_player:
            print(f"  Player {player['player_id']}:")
            print(f"    Total Picks: {player['total_picks']}")
            print(f"    Hit Rate: {player['hit_rate_percentage']:.2f}%")
            print(f"    Total P&L: ${player['total_profit_loss']:.2f}")
            print(f"    Avg P&L: ${player['avg_profit_loss']:.2f}")
            print(f"    Avg CLV: {player['avg_clv_cents']:.2f} cents")
            print(f"    Period: {player['first_pick']} to {player['last_pick']}")
        
        # Analyze by game
        by_game = await conn.fetch("""
            SELECT 
                game_id,
                COUNT(*) as total_picks,
                COUNT(CASE WHEN hit = true THEN 1 END) as hits,
                COUNT(CASE WHEN hit = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN hit = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                SUM(profit_loss) as total_profit_loss,
                ROUND(AVG(profit_loss), 2) as avg_profit_loss,
                ROUND(AVG(clv_cents), 2) as avg_clv_cents,
                MIN(settled_at) as settled_at
            FROM pick_results
            GROUP BY game_id
            ORDER BY total_picks DESC
            LIMIT 10
        """)
        
        print(f"\nTop 10 Games by Pick Volume:")
        for game in by_game:
            print(f"  Game {game['game_id']}:")
            print(f"    Total Picks: {game['total_picks']}")
            print(f"    Hit Rate: {game['hit_rate_percentage']:.2f}%")
            print(f"    Total P&L: ${game['total_profit_loss']:.2f}")
            print(f"    Avg P&L: ${game['avg_profit_loss']:.2f}")
            print(f"    Avg CLV: {game['avg_clv_cents']:.2f} cents")
            print(f"    Settled: {game['settled_at']}")
        
        # Analyze by side
        by_side = await conn.fetch("""
            SELECT 
                side,
                COUNT(*) as total_picks,
                COUNT(CASE WHEN hit = true THEN 1 END) as hits,
                COUNT(CASE WHEN hit = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN hit = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                SUM(profit_loss) as total_profit_loss,
                ROUND(AVG(profit_loss), 2) as avg_profit_loss,
                ROUND(AVG(clv_cents), 2) as avg_clv_cents
            FROM pick_results
            GROUP BY side
            ORDER BY total_picks DESC
        """)
        
        print(f"\nPerformance by Side:")
        for side in by_side:
            print(f"  {side.upper()}:")
            print(f"    Total Picks: {side['total_picks']}")
            print(f"    Hit Rate: {side['hit_rate_percentage']:.2f}%")
            print(f"    Total P&L: ${side['total_profit_loss']:.2f}")
            print(f"    Avg P&L: ${side['avg_profit_loss']:.2f}")
            print(f"    Avg CLV: {side['avg_clv_cents']:.2f} cents")
        
        # Analyze CLV performance
        clv_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN clv_cents > 0 THEN 'Positive CLV'
                    WHEN clv_cents < 0 THEN 'Negative CLV'
                    ELSE 'Zero CLV'
                END as clv_category,
                COUNT(*) as total_picks,
                COUNT(CASE WHEN hit = true THEN 1 END) as hits,
                COUNT(CASE WHEN hit = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN hit = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                SUM(profit_loss) as total_profit_loss,
                ROUND(AVG(profit_loss), 2) as avg_profit_loss,
                ROUND(AVG(clv_cents), 2) as avg_clv_cents
            FROM pick_results
            GROUP BY clv_category
            ORDER BY avg_clv_cents DESC
        """)
        
        print(f"\nPerformance by CLV Category:")
        for clv in clv_analysis:
            print(f"  {clv['clv_category']}:")
            print(f"    Total Picks: {clv['total_picks']}")
            print(f"    Hit Rate: {clv['hit_rate_percentage']:.2f}%")
            print(f"    Total P&L: ${clv['total_profit_loss']:.2f}")
            print(f"    Avg P&L: ${clv['avg_profit_loss']:.2f}")
            print(f"    Avg CLV: {clv['avg_clv_cents']:.2f} cents")
        
        # Analyze profit/loss distribution
        pl_distribution = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN profit_loss > 0 THEN 'Profitable'
                    WHEN profit_loss < 0 THEN 'Loss'
                    ELSE 'Break Even'
                END as pl_category,
                COUNT(*) as total_picks,
                COUNT(CASE WHEN hit = true THEN 1 END) as hits,
                COUNT(CASE WHEN hit = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN hit = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                SUM(profit_loss) as total_profit_loss,
                ROUND(AVG(profit_loss), 2) as avg_profit_loss,
                ROUND(AVG(clv_cents), 2) as avg_clv_cents
            FROM pick_results
            GROUP BY pl_category
            ORDER BY total_profit_loss DESC
        """)
        
        print(f"\nProfit/Loss Distribution:")
        for pl in pl_distribution:
            print(f"  {pl['pl_category']}:")
            print(f"    Total Picks: {pl['total_picks']}")
            print(f"    Hit Rate: {pl['hit_rate_percentage']:.2f}%")
            print(f"    Total P&L: ${pl['total_profit_loss']:.2f}")
            print(f"    Avg P&L: ${pl['avg_profit_loss']:.2f}")
            print(f"    Avg CLV: {pl['avg_clv_cents']:.2f} cents")
        
        # Recent performance
        recent = await conn.fetch("""
            SELECT * FROM pick_results 
            ORDER BY settled_at DESC, id DESC 
            LIMIT 10
        """)
        
        print(f"\nRecent Pick Results:")
        for result in recent:
            print(f"  - Pick {result['pick_id']}: Player {result['player_id']}, Game {result['game_id']}")
            print(f"    Actual: {result['actual_value']}, Line: {result['line_value']} {result['side']}")
            print(f"    Hit: {result['hit']}, P&L: ${result['profit_loss']:.2f}")
            print(f"    CLV: {result['clv_cents']:.2f} cents")
            print(f"    Settled: {result['settled_at']}")
        
        # Performance by closing odds range
        closing_odds_analysis = await conn.fetch("""
            SELECT 
                CASE 
                    WHEN closing_odds <= -200 THEN 'Heavy Favorite (-200 or worse)'
                    WHEN closing_odds <= -150 THEN 'Strong Favorite (-150 to -201)'
                    WHEN closing_odds <= -110 THEN 'Moderate Favorite (-110 to -151)'
                    WHEN closing_odds <= -100 THEN 'Light Favorite (-100 to -111)'
                    WHEN closing_odds <= 100 THEN 'Pickem (-100 to 100)'
                    WHEN closing_odds <= 150 THEN 'Light Underdog (101 to 150)'
                    WHEN closing_odds <= 200 THEN 'Moderate Underdog (151 to 200)'
                    ELSE 'Heavy Underdog (201+)'
                END as odds_range,
                COUNT(*) as total_picks,
                COUNT(CASE WHEN hit = true THEN 1 END) as hits,
                COUNT(CASE WHEN hit = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN hit = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                SUM(profit_loss) as total_profit_loss,
                ROUND(AVG(profit_loss), 2) as avg_profit_loss,
                ROUND(AVG(clv_cents), 2) as avg_clv_cents
            FROM pick_results
            WHERE closing_odds IS NOT NULL
            GROUP BY odds_range
            ORDER BY avg_profit_loss DESC
        """)
        
        print(f"\nPerformance by Closing Odds Range:")
        for odds in closing_odds_analysis:
            print(f"  {odds['odds_range']}:")
            print(f"    Total Picks: {odds['total_picks']}")
            print(f"    Hit Rate: {odds['hit_rate_percentage']:.2f}%")
            print(f"    Total P&L: ${odds['total_profit_loss']:.2f}")
            print(f"    Avg P&L: ${odds['avg_profit_loss']:.2f}")
            print(f"    Avg CLV: {odds['avg_clv_cents']:.2f} cents")
        
        # Daily performance
        daily_performance = await conn.fetch("""
            SELECT 
                DATE(settled_at) as settlement_date,
                COUNT(*) as total_picks,
                COUNT(CASE WHEN hit = true THEN 1 END) as hits,
                COUNT(CASE WHEN hit = false THEN 1 END) as misses,
                ROUND(COUNT(CASE WHEN hit = true THEN 1 END) * 100.0 / COUNT(*), 2) as hit_rate_percentage,
                SUM(profit_loss) as daily_profit_loss,
                ROUND(AVG(profit_loss), 2) as avg_profit_loss,
                ROUND(AVG(clv_cents), 2) as avg_clv_cents
            FROM pick_results
            GROUP BY DATE(settled_at)
            ORDER BY settlement_date DESC
            LIMIT 10
        """)
        
        print(f"\nDaily Performance (Last 10 Days):")
        for day in daily_performance:
            print(f"  {day['settlement_date']}:")
            print(f"    Total Picks: {day['total_picks']}")
            print(f"    Hit Rate: {day['hit_rate_percentage']:.2f}%")
            print(f"    Daily P&L: ${day['daily_profit_loss']:.2f}")
            print(f"    Avg P&L: ${day['avg_profit_loss']:.2f}")
            print(f"    Avg CLV: {day['avg_clv_cents']:.2f} cents")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_pick_results())
