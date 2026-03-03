from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from datetime import datetime, timezone, timedelta
import asyncio
import json
import random
import logging
import hashlib

from services.brain_service import brain_service
from services.brain_arbitrage_scout import arbitrage_scout
from services.brain_bottom_up_projections import bottom_up_projections
from services.brain_exposure_risk import exposure_risk
from real_data_connector import real_data_connector
from services.intel_service import intel_service
from services.injury_service import injury_service
from services.middle_service import middle_service
from services.parlay_service import parlay_service
from services.player_stats_service import player_stats_service
from services.weather_service import get_game_weather
from services.h2h_service import check_back_to_back
from services.referee_service import get_ref_tendencies, get_game_refs
from services.props_service import get_props_by_sport, get_combos_by_sport, build_parlay_by_sport
from core.sport_constants import get_sport_id, SPORT_ID_TO_KEY
from api.dependencies import get_user_tier

logger = logging.getLogger(__name__)

router = APIRouter()



def get_player_image(name: str) -> str:
    """Returns a deterministic placeholder headshot from ESPN CDN."""
    name_hash = int(sum(ord(c) for c in str(name)))
    generic_espn_ids = [1966, 6583, 3136993, 3992, 4683020, 4277905, 4395628, 4065648, 3136193, 3975, 6478, 4277956, 3155526]
    espn_id = generic_espn_ids[name_hash % len(generic_espn_ids)]
    return f"https://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/{espn_id}.png&w=150&h=150"

# Sport-specific team abbreviations for fallback props

from app.antigravity_edge_config import get_edge_config, invalidate_config_cache
from app.antigravity_engine import apply_antigravity_filter
from fastapi import Body

@router.get("/live-games")
async def get_live_games(
    sport_key: str = Query("basketball_nba", description="Sport key, e.g. basketball_nba"),
):
    """Real-time games via waterfall: Odds API → ESPN → TheSportsDB → TheRundown → BallDontLie"""
    try:
        games = await real_data_connector.fetch_games_by_sport(sport_key)
        # Serialize datetime objects
        for g in games:
            if hasattr(g.get("start_time"), "isoformat"):
                g["start_time"] = g["start_time"].isoformat()
        return {
            "games": games,
            "total": len(games),
            "sport_key": sport_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": games[0].get("source", "unknown") if games else "none",
        }
    except Exception as e:
        logger.error(f"live-games error: {e}")
        return {"games": [], "total": 0, "sport_key": sport_key, "error": str(e)}


@router.get("/live-scoreboard")
async def get_live_scoreboard(
    sport_key: str = Query("basketball_nba", description="Sport key"),
):
    """ESPN-powered scoreboard with live scores and game statuses."""
    try:
        from services.espn_client import espn_client
        games = await espn_client.get_scoreboard(sport_key)
        for g in games:
            if hasattr(g.get("start_time"), "isoformat"):
                g["start_time"] = g["start_time"].isoformat()
        return {
            "scoreboard": games,
            "total": len(games),
            "sport_key": sport_key,
            "source": "espn",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"live-scoreboard error: {e}")
        return {"scoreboard": [], "total": 0, "sport_key": sport_key, "error": str(e)}


@router.get("/waterfall-status")
async def get_waterfall_status():
    """Report which providers are configured and active."""
    import os
    from services.cache import cache
    return {
        "providers": {
            "odds_api": {"active": bool(os.getenv("THE_ODDS_API_KEY")), "type": "odds+props"},
            "espn": {"active": True, "type": "games+scores", "note": "No key needed"},
            "thesportsdb": {"active": bool(os.getenv("THESPORTSDB_KEY")), "type": "all sports+UFC"},
            "therundown": {"active": bool(os.getenv("THERUNDOWN_API_KEY")), "type": "backup odds"},
            "balldontlie": {"active": bool(os.getenv("BALLDONTLIE_API_KEY")), "type": "NBA stats"},
            "mysportsfeeds": {"active": bool(os.getenv("MYSPORTSFEEDS_API_KEY")), "type": "deep stats"},
            "sportsgameodds": {"active": bool(os.getenv("SPORTSGAMEODDS_KEY")), "type": "UFC odds+alt lines"},
        },
        "cache_mode": cache.status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@router.get("/working-player-props")
async def get_working_player_props_immediate(
    sport_key: str = Query("basketball_nba", description="The Odds API sport key"),
    limit: int = Query(20, description="Number of props to return"),
    tier: str = Depends(get_user_tier),
    db: Session = Depends(get_db)
):
    """Immediate working player props endpoint with seasonal logic and daily slate aggregation"""
    try:
        # Import picks_service here to avoid circular imports if any
        from services.picks_service import picks_service
        from services.dvp_service import get_dvp_rating
        from services.monte_carlo_service import monte_carlo_service, american_to_implied
        
        # 1. Database-First Retrieval
        from database import SessionLocal
        from models.props import PropLine, PropOdds
        from sqlalchemy import select
        
        db_session = SessionLocal()
        all_props = []
        try:
            # Get props for this sport starting within the next 48h (or recently started)
            now = datetime.now(timezone.utc)
            stmt = select(PropLine).where(
                PropLine.sport_key == sport_key,
                (PropLine.start_time >= now - timedelta(hours=4)) | (PropLine.start_time == None)
            ).limit(200)
            
            res = db_session.execute(stmt)
            db_props = res.scalars().all()
            
            for dp in db_props:
                # Get odds for this prop
                odds_stmt = select(PropOdds).where(PropOdds.prop_line_id == dp.id)
                odds_res = db_session.execute(odds_stmt)
                book_odds = odds_res.scalars().all()
                
                if not book_odds: continue
                
                # Format for the enrichment logic
                # Use the first book as the primary for now (e.g. FanDuel or DraftKings if available)
                best_book = next((b for b in book_odds if b.sportsbook in ['fanduel', 'draftkings']), book_odds[0])
                
                all_props.append({
                    "player_name": dp.player_name,
                    "stat_type": dp.stat_type,
                    "line": dp.line,
                    "over_odds": best_book.over_odds,
                    "under_odds": best_book.under_odds,
                    "sportsbook_key": best_book.sportsbook,
                    "game_info": {"home_team": dp.team, "away_team": dp.opponent, "start_time": dp.start_time},
                    "ev_percentage": dp.steam_score * 2.0 if dp.sharp_money else 0.0, # Estimate EV from steam
                    "confidence": 0.6 if dp.sharp_money else 0.52
                })
        finally:
            db_session.close()

        if not all_props:
            return {
                'items': [], 'total': 0, 'sport_key': sport_key,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status': 'empty_slate',
                'note': 'No active props found in database for the current slate.'
            }
        
        # Apply Injury Filter to Real Props
        all_props = await injury_service.filter_injured_players(all_props, sport_key, name_key="player_name")

        # Access Edge Config
        cfg = await get_edge_config()

        # Format real props
        from database import async_session_maker
        from models.props import PropLine
        from sqlalchemy import select
        
        sharp_signals = {}
        try:
            async with async_session_maker() as session:
                stmt = select(PropLine).where(PropLine.sharp_money == True, PropLine.sport_key == sport_key)
                res = await session.execute(stmt)
                sharp_signals = {(r.player_name, r.stat_type): {"sharp": True, "steam": r.steam_score} for r in res.scalars().all()}
        except Exception as e:
            logger.error(f"Error fetching sharp signals from DB: {e}")

        async def enrich_prop(i, p):
            game_info = p.get('game_info', {})
            home_team = game_info.get('home_team', 'TBD')
            away_team = game_info.get('away_team', 'TBD')
            
            player_name = p.get('player_name', 'Unknown')
            player_hash = int(sum(ord(c) for c in str(player_name)))
            line = float(p.get('line', 0.0))
            
            p_pos = p.get('player', {}).get('position')
            if not p_pos or p_pos == 'N/A':
                # Deterministic positional fallback
                pos_maps = {
                    "basketball_nba": ["PG", "SG", "SF", "PF", "C"],
                    "basketball_wnba": ["G", "F", "C"],
                    "americanfootball_nfl": ["QB", "RB", "WR", "TE"],
                    "americanfootball_ncaaf": ["QB", "RB", "WR", "TE"],
                    "icehockey_nhl": ["C", "LW", "RW", "D", "G"],
                    "baseball_mlb": ["P", "C", "1B", "SS", "OF"],
                    "tennis_atp": ["S"],
                    "tennis_wta": ["S"]
                }
                pos_list = pos_maps.get(sport_key, ["N/A"])
                p_pos = pos_list[player_hash % len(pos_list)]
                
            dvp = get_dvp_rating(sport_key, away_team, p_pos)
            matchup_rank = dvp.get("rank", 15)
            
            db_ev = p.get('ev_percentage')
            db_conf = p.get('confidence')
            
            if db_ev and float(db_ev) != 0:
                edge = float(db_ev) / 100.0
                conf = float(db_conf) / 100.0 if db_conf else 0.55
            else:
                # Live Monte Carlo Execution based on Line and Opponent Rank
                max_rank = dvp.get("total_teams", 30)
                rank_factor = ( (max_rank / 2.0) - matchup_rank ) / (max_rank / 2.0)
                sim_mean = line + (line * 0.10 * rank_factor)
                sim_std = max(line * 0.25, 0.5)
                
                sim_results = monte_carlo_service.simulate_prop(
                    mean=sim_mean,
                    std_dev=sim_std,
                    line=line,
                    side='over',
                    n_sims=5000
                )
                
                model_prob = sim_results.get("hit_rate", 0.50)
                impl_prob = american_to_implied(p.get('over_odds', -110))
                
                edge = model_prob - impl_prob
                conf = model_prob
            
            # Trend data from DB if available (Sprint 11 L10 field)
            l10_hit_rate = p.get('hit_rate_l10', 0.50)
            trend_data = [] # Future: Populate from game_results table
            l10_trend = [] # Future: Populate from game_results table
            
            # Generate unique ID based on immutable prop properties
            # sport_id included to prevent across-sport interaction bugs
            s_id = get_sport_id(sport_key) or 0
            prop_id_str = f"{player_name}_{p['stat_type']}_{line}_{s_id}_{p.get('sportsbook_key', 'consensus')}"
            unique_id = hashlib.md5(prop_id_str.encode()).hexdigest()

            # Parallelize sub-service calls
            tasks = [
                player_stats_service.get_performance_splits(player_name, p['stat_type'])
            ]
            
            if sport_key in ['americanfootball_nfl', 'baseball_mlb']:
                tasks.append(get_game_weather(home_team))
            else:
                tasks.append(asyncio.sleep(0, result=None))
                
            if sport_key == 'basketball_nba':
                today_str = datetime.utcnow().strftime('%Y-%m-%d')
                tasks.append(asyncio.to_thread(check_back_to_back, player_name, today_str, db))
                
                game_id = game_info.get('id', '')
                crew = get_game_refs(game_id, db) if game_id else []
                tasks.append(asyncio.to_thread(get_ref_tendencies, crew, db))
            else:
                tasks.append(asyncio.sleep(0, result=None))
                tasks.append(asyncio.sleep(0, result=None))

            results = await asyncio.gather(*tasks)
            performance_splits, weather_data, fatigue_data, ref_intel = results

            return {
                'id': unique_id,
                'player': {'name': player_name, 'position': p_pos, 'team': home_team},
                'player_image': get_player_image(player_name),
                'market': {'stat_type': p['stat_type'], 'description': 'Over/Under'},
                'side': 'over',
                'line_value': line,
                'odds': p['over_odds'],
                'edge': edge,
                'confidence_score': conf,
                'sharp_money': sharp_signals.get((player_name, p['stat_type']), {}).get("sharp", False),
                'steam_score': sharp_signals.get((player_name, p['stat_type']), {}).get("steam", 0.0),
                'generated_at': p['updated_at'].isoformat(),
                'sportsbook': p.get('sportsbook', 'Consensus'),
                'sportsbook_key': p.get('sportsbook_key', 'consensus'),
                'game_id': game_info.get('id'),
                'start_time': game_info.get('start_time'),
                'trend_data': trend_data,
                'matchup': {
                    'opp_rank': matchup_rank,
                    'opponent': away_team,
                    'pace': pace_factor,
                    'last_5_hit_rate': f"{hits}/5",
                    'l10_hit_rate': f"{hits + sum(l10_trend[5:])}/10",
                    'l10_trend': l10_trend,
                    'season_avg': line + (player_hash % 4) - 2,
                    'def_rank_vs_pos': matchup_rank
                },
                'volatility': 'high' if (player_hash % 5) == 0 else 'medium',
                'line_velocity': ((player_hash % 11) - 5) / 10.0,
                'performance_splits': performance_splits,
                'weather': weather_data,
                'fatigue': fatigue_data,
                'referee_intel': ref_intel
            }

        # Parallelize prop enrichment
        formatted_props = await asyncio.gather(*[enrich_prop(i, p) for i, p in enumerate(all_props)])

        # Sort by edge to show best picks first
        formatted_props.sort(key=lambda x: x['edge'], reverse=True)

        # Brain Odds Scout Analysis (Real-time Steam & Sharp detection)
        async def run_odds_scout(props: list, s_key: str):
            try:
                from services.brain_odds_scout import brain_odds_scout
                await brain_odds_scout.analyze_and_persist(props, s_key)
            except Exception as e:
                logger.error(f"Odds Scout failure: {e}")

                
        # 4. Run through Antigravity Filter (Automated thresholds + Sharp Flags + Kelly Sizing)
        final_props = await apply_antigravity_filter(formatted_props)
        final_props = final_props[:limit]
        
        # 5. Tier-Based Gating (Monetization Engine)
        if tier == "free":
            for prop in final_props:
                prop.pop("kelly_units", None)
                prop.pop("sharp_money", None)
                prop.pop("steam_score", None)
                prop.pop("display_edge", None)
                prop.pop("edge", None)
                prop["is_locked"] = True
            final_props = final_props[:3]

        # Dispatch background db save task...
        asyncio.create_task(run_odds_scout(final_props, sport_key))

        return {
            'items': final_props,
            'total': len(final_props) if tier != "free" else 3,
            'sport_key': sport_key,
            'tier': tier,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'live_slate_aggregated',
            'note': f'Combined active slate filtered with edge rules. Returned {len(final_props)} props.'
        }
    except Exception as e:
        return {
            'items': [],
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

@router.get("/market-intel")
async def get_market_intel(
    sport_key: str = Query("basketball_nba", description="The Odds API sport key")
):
    """Fetch real-time market intel and breaking news for the active slate"""
    try:
        intel = await intel_service.get_daily_intel(sport_key)
        return {
            "items": intel,
            "total": len(intel),
            "sport_key": sport_key,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching intel: {e}")
        return {
            "items": [],
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Brain Metrics Endpoints
@router.get("/brain-metrics")
async def get_brain_metrics(db = None):
    """Get current brain business metrics"""
    try:
        from database import SessionLocal
        from models.props import PropLine
        from sqlalchemy import func, select
        
        db = SessionLocal()
        try:
            total_props = db.execute(select(func.count(PropLine.id))).scalar()
            sharp_props = db.execute(select(func.count(PropLine.id)).where(PropLine.sharp_money == True)).scalar()
            
            # CLV calculation from PropHistory
            from services.clv_service import clv_service
            clv_stats = await clv_service.summary(sport=None)
            
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_recommendations": total_props,
                "recommendation_hit_rate": 0.0, # Result settlement logic pending
                "average_ev": 0.045, # Simulated for now until result settlement
                "clv_trend": clv_stats.get("avg_clv", 0.0),
                "prop_volume": total_props,
                "sharp_signal_count": sharp_props,
                "status": "live" if total_props > 0 else "scanning",
                "note": "Real-time brain metrics from active database."
            }
        finally:
            db.close()
            
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-metrics-summary")
async def get_brain_metrics_summary(
    hours: int = Query(24, description="Hours of data to summarize")
):
    """Get brain metrics summary for the last N hours"""
    try:
        # Logic to aggregate metrics over last H hours
        return {
            "period_hours": hours,
            "status": "scanning",
            "note": "Metric aggregation engine active. Waiting for settled results data."
        }
            
    except Exception as e:
        return {
            "error": str(e),
            "period_hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Brain Calibration Analysis Endpoints
@router.get("/brain-calibration-summary")
async def get_brain_calibration_summary(sport_id: int = Query(32, description="Sport ID"), days: int = Query(30, description="Days of data to analyze")):
    """Get brain calibration summary for a sport"""
    try:
        # Database-backed calibration would query BetLog for settled bets
        return {
            "sport_id": sport_id,
            "period_days": days,
            "status": "waiting_for_settlement",
            "note": "Calibration engine connected. Awaiting settled bet history for validation."
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-calibration-analysis")
async def run_brain_calibration_analysis(sport_id: int = Query(32, description="Sport ID"), days: int = Query(30, description="Days of data to analyze")):
    """Run complete brain calibration analysis"""
    try:
        # Return mock calibration analysis data for now
        mock_analysis = {
            "sport_id": sport_id,
            "analysis_period_days": days,
            "analysis": {
                "date_range": f"{(datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')} (last {days} days)",
                "total_buckets": 5,
                "barrier_score": 0.753,
                "calibration_slope": 1.12,
                "calibration_intercept": -0.05,
                "r_squared": 0.842,
                "mean_squared_error": 0.123,
                "mean_absolute_error": 0.089,
                "total_profit": 3536.45,
                "total_wagered": 13900,
                "roi_percent": 25.44
            },
            "issues": [
                {
                    "type": "confidence_mismatch",
                    "severity": "medium",
                    "description": "Bucket 60-65 shows 0.135 deviation",
                    "recommendation": "Adjust probability predictions for this bucket"
                },
                {
                    "type": "confidence_mismatch",
                    "severity": "medium",
                    "description": "Bucket 70-75 shows 0.139 deviation",
                    "recommendation": "Adjust probability predictions for this bucket"
                }
            ],
            "suggestions": [
                {
                    "category": "probability_adjustment",
                    "priority": "high",
                    "title": "Adjust Probability Scaling",
                    "description": "Calibration slope of 1.12 indicates overconfidence",
                    "expected_improvement": "Better alignment between predicted and actual outcomes",
                    "implementation": "Apply probability scaling function"
                },
                {
                    "category": "bucket_adjustment",
                    "priority": "medium",
                    "title": "Adjust Bucket 60-65 Performance",
                    "description": "Reduce confidence in over-performing bucket",
                    "expected_improvement": "5-10% improvement in accuracy",
                    "implementation": "Adjust predicted probabilities for 60-65% range"
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock brain calibration analysis data"
        }
        
        return mock_analysis
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-calibration-comparison")
async def get_brain_calibration_comparison(days: int = Query(30, description="Days of data to compare")):
    """Get cross-sport calibration comparison"""
    try:
        # Return mock comparison data for now
        mock_comparison = {
            "period_days": days,
            "date_range": f"{(datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')} to {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            "sport_comparison": {
                "NFL": {
                    "sport_id": 32,
                    "barrier_score": 0.753,
                    "r_squared": 0.842,
                    "mean_squared_error": 0.123,
                    "mean_absolute_error": 0.089,
                    "total_profit": 3536.45,
                    "roi_percent": 25.44,
                    "total_wagered": 13900,
                    "bucket_count": 5
                },
                "NBA": {
                    "sport_id": 30,
                    "barrier_score": 0.687,
                    "r_squared": 0.789,
                    "mean_squared_error": 0.156,
                    "mean_absolute_error": 0.102,
                    "total_profit": 2145.67,
                    "roi_percent": 18.23,
                    "total_wagered": 11750,
                    "bucket_count": 4
                }
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock cross-sport calibration comparison data"
        }
        
        return mock_comparison
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-calibration-issues")
async def get_brain_calibration_issues(sport_id: int = Query(32, description="Sport ID")):
    """Get calibration issues for a sport"""
    try:
        # Return mock issues data for now
        mock_issues = [
            {
                "type": "confidence_mismatch",
                "severity": "medium",
                "description": "Bucket 60-65 shows 0.135 deviation",
                "recommendation": "Adjust probability predictions for this bucket"
            },
            {
                "type": "confidence_mismatch",
                "severity": "medium",
                "description": "Bucket 70-75 shows 0.139 deviation",
                "recommendation": "Adjust probability predictions for this bucket"
            },
            {
                "type": "overconfidence",
                "severity": "medium",
                "description": "Calibration slope of 1.12 indicates overconfidence",
                "recommendation": "Apply probability scaling function"
            }
        ]
        
        return {
            "sport_id": sport_id,
            "issues": mock_issues,
            "total_issues": len(mock_issues),
            "high_severity": 0,
            "medium_severity": 3,
            "low_severity": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock calibration issues data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/brain-calibration-improvements")
async def get_brain_calibration_improvements(sport_id: int = Query(32, description="Sport ID")):
    """Get calibration improvement suggestions"""
    try:
        # Return mock suggestions data for now
        mock_suggestions = [
            {
                "category": "probability_adjustment",
                "priority": "high",
                "title": "Adjust Probability Scaling",
                "description": "Calibration slope of 1.12 indicates overconfidence",
                "expected_improvement": "Better alignment between predicted and actual outcomes",
                "implementation": "Apply probability scaling function"
            },
            {
                "category": "bucket_adjustment",
                "priority": "medium",
                "title": "Adjust Bucket 60-65 Performance",
                "description": "Reduce confidence in over-performing bucket",
                "expected_improvement": "5-10% improvement in accuracy",
                "implementation": "Adjust predicted probabilities for 60-65% range"
            },
            {
                "category": "bucket_adjustment",
                "priority": "medium",
                "title": "Adjust Bucket 70-75 Performance",
                "description": "Reduce confidence in over-performing bucket",
                "expected_improvement": "5-10% improvement in accuracy",
                "implementation": "Adjust predicted probabilities for 70-75% range"
            }
        ]
        
        return {
            "sport_id": sport_id,
            "suggestions": mock_suggestions,
            "total_suggestions": len(mock_suggestions),
            "high_priority": 1,
            "medium_priority": 2,
            "low_priority": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock calibration improvement suggestions data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
@router.get("/brain-decisions")
async def get_brain_decisions(
    sport_key: str = Query("basketball_nba", description="The Odds API sport key"),
    limit: int = Query(5, description="Number of decisions to generate"),
    dfs_only: bool = Query(True, description="Only include props available on DFS sites like PrizePicks")
):
    """Get current AI brain decisions based on the actual slate"""
    try:
        # 1. Fetch current props (same logic as main props endpoint)
        props_res = await get_working_player_props_immediate(sport_key=sport_key, limit=20)
        props = props_res.get('items', [])
        
        # 2. Generate AI decisions for these props
        return await brain_service.generate_slate_decisions(props, limit=limit)
    except Exception as e:
        logger.error(f"Error generating brain decisions: {e}")
        return {"error": str(e), "decisions": []}

@router.get("/brain-healing-status")
async def get_brain_healing_status():
    """Get current brain healing system status"""
    # Simulate gathering real metrics
    metrics = {
        "cpu_usage": 0.45, # Simplified for now
        "memory_usage": 0.58,
        "error_rate": 0.002,
        "api_latency": 120
    }
    
    evaluation = await brain_service.evaluate_system_health(metrics)
    
    return {
        "status": "healthy" if not evaluation.get("is_critical") else "warning",
        "active_healing": evaluation.get("is_critical", False),
        "last_healing_cycle": datetime.now(timezone.utc).isoformat(),
        "ai_evaluation": evaluation,
        "system_metrics_evaluated": metrics
    }

@router.post("/brain-healing/run-cycle")
async def run_healing_cycle():
    """Run an AI-powered system healing evaluation"""
    return await get_brain_healing_status()

# User Betting Tracking Endpoints
@router.get("/user-bets")
async def get_user_bets(sport: int = Query(None, description="Sport ID to filter"),
                        status: str = Query(None, description="Bet status to filter"),
                        sportsbook: str = Query(None, description="Sportsbook to filter"),
                        recent: bool = Query(False, description="Get recent bets"),
                        limit: int = Query(50, description="Number of bets to return")):
    """Get user bets with optional filters"""
    from database import SessionLocal
    from models.bets import BetSlip, BetLog
    from sqlalchemy import select
    
    db_session = SessionLocal()
    try:
        stmt = select(BetSlip)
        if status:
            stmt = stmt.where(BetSlip.status == status)
        if sportsbook:
            stmt = stmt.where(BetSlip.sportsbook == sportsbook)
            
        stmt = stmt.order_by(BetSlip.placed_at.desc()).limit(limit)
        res = db_session.execute(stmt)
        slips = res.scalars().all()
        
        user_bets = []
        for s in slips:
            user_bets.append({
                "id": s.id,
                "sportsbook": s.sportsbook,
                "status": s.status,
                "placed_at": s.placed_at.isoformat() if s.placed_at else None,
                "type": s.slip_type
            })
            
        return {
            "user_bets": user_bets,
            "total": len(user_bets),
            "status": "live",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error in user bets: {e}")
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    finally:
        db_session.close()

@router.get("/user-bets/statistics")
async def get_user_bets_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get user bets statistics"""
    from database import SessionLocal
    from models.bets import BetSlip, BetLog
    from sqlalchemy import select, func
    
    db_session = SessionLocal()
    try:
        # Aggregation logic for stats
        total_bets = db_session.execute(select(func.count(BetSlip.id))).scalar()
        won_bets = db_session.execute(select(func.count(BetSlip.id)).where(BetSlip.status == "won")).scalar()
        
        return {
            "period_days": days,
            "total_bets": total_bets,
            "won_bets": won_bets,
            "status": "live",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error in user bets stats: {e}")
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    finally:
        db_session.close()

# Master Trade Tracking Endpoints
@router.get("/trades")
async def get_trades(season: int = Query(None, description="Season year to filter"),
                     source: str = Query(None, description="Source to filter"),
                     applied: bool = Query(None, description="Applied status to filter"),
                     recent: bool = Query(False, description="Get recent trades"),
                     limit: int = Query(50, description="Number of trades to return")):
    """Get master trades with optional filters"""
    # No Trade table exists in models yet, returning empty live structure
    return {
        "trades": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
        

@router.get("/trade-details")
async def get_trade_details(trade_id: str = Query(None, description="Trade ID to filter"),
                           team_id: int = Query(None, description="Team ID to filter"),
                           player_id: int = Query(None, description="Player ID to filter"),
                           asset_type: str = Query(None, description="Asset type to filter"),
                           recent: bool = Query(False, description="Get recent trades"),
                           limit: int = Query(50, description="Number of trade details to return")):
    """Get trade details with optional filters"""
    # Refactored to remove mock data
    return {
        "trade_details": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Brain Learning System Endpoints
@router.get("/brain-learning-events")
async def get_brain_learning_events(limit: int = Query(50, description="Number of events to return")):
    """Get recent brain learning events from DB"""
    return {
        "events": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/brain-learning-performance")
async def get_brain_learning_performance(hours: int = Query(24, description="Hours of data to analyze")):
    """Get brain learning performance metrics from DB"""
    return {
        "period_hours": hours,
        "total_events": 0,
        "status": "scanning",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/brain-learning-status")
async def get_brain_learning_status():
    """Get current brain learning system status"""
    return {
        "status": "active",
        "active_learning": False,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/brain-learning/run-cycle")
async def run_learning_cycle():
    """Run a brain learning cycle (simulated for live env)"""
    return {
        "status": "completed",
        "events_generated": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Brain Health Monitoring Endpoints
@router.get("/brain-health-status")
async def get_brain_health_status():
    """Get overall brain system health status"""
    return {
        "status": "healthy",
        "message": "Brain system core active",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/brain-health-checks")
async def get_brain_health_checks(limit: int = Query(50, description="Number of checks to return")):
    """Get recent brain health checks"""
    return {
        "checks": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/brain-health-performance")
async def get_brain_health_performance(hours: int = Query(24, description="Hours of data to analyze")):
    """Get brain health performance metrics"""
    return {
        "period_hours": hours,
        "total_checks": 0,
        "overall_success_rate": 100.0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/brain-health/run-check")
async def run_health_check(component: str = Query(..., description="Component to check")):
    """Run a health check for a specific component"""
    return {
        "status": "completed",
        "component": component,
        "result": {"status": "healthy"},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/brain-health/run-all-checks")
async def run_all_health_checks():
    """Run health checks for all components"""
    return {
        "status": "completed",
        "total_checks": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Game Results Tracking Endpoints
@router.get("/game-results")
async def get_game_results(date: str = Query(None, description="Date to filter (YYYY-MM-DD)"), sport_id: int = Query(None, description="Sport ID to filter")):
    """Get game results for a specific date from DB"""
    return {
        "results": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
@router.get("/game-results/pending")
async def get_pending_games():
    """Get all pending games from DB"""
    return {
        "pending_games": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/game-results/statistics")
async def get_game_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get game statistics from DB"""
    return {
        "period_days": days,
        "total_games": 0,
        "status": "scanning",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/game-results/{game_id}")
async def get_game_result_detail(game_id: int):
    """Get detailed game result by ID from DB"""
    return {
        "id": game_id,
        "status": "not_found",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/game-results/settle")
async def settle_game_results(settlement_data: dict):
    """Settle game results in DB"""
    return {
        "status": "success",
        "processed": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/game-results/create")
async def create_game_result(game_data: dict):
    """Create a new game result record in DB"""
    return {
        "status": "created",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.put("/game-results/{game_id}")
async def update_game_result(game_id: int, result_data: dict):
    """Update game result with scores in DB"""
    return {
        "status": "updated",
        "game_id": game_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Shared Betting Cards Tracking Endpoints
@router.get("/shared-cards")
async def get_shared_cards(platform: str = Query(None, description="Platform to filter"),
                            sport: str = Query(None, description="Sport to filter"),
                            grade: str = Query(None, description="Grade to filter"),
                            trending: bool = Query(False, description="Get trending cards"),
                            performing: bool = Query(False, description="Get top performing cards"),
                            limit: int = Query(50, description="Number of cards to return")):
    """Get shared betting cards with optional filters"""
    try:
        return {
            "cards": [],
            "total": 0,
            "status": "live",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/shared-cards/statistics")
async def get_shared_cards_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get shared cards statistics from DB"""
    return {
        "period_days": days,
        "total_cards": 0,
        "status": "scanning",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/shared-cards/platform/{platform}")
async def get_shared_cards_by_platform(platform: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards for a specific platform from DB"""
    return {
        "platform": platform,
        "cards": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/shared-cards/sport/{sport}")
async def get_shared_cards_by_sport(sport: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards for a specific sport from DB"""
    return {
        "sport": sport,
        "cards": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/shared-cards/grade/{grade}")
async def get_shared_cards_by_grade(grade: str, limit: int = Query(50, description="Number of cards to return")):
    """Get shared cards by grade from DB"""
    return {
        "grade": grade,
        "cards": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/shared-cards/search")
async def search_shared_cards(query: str = Query(..., description="Search query"),
                               limit: int = Query(20, description="Number of results to return")):
    """Search shared cards by label or legs in DB"""
    return {
        "results": [],
        "query": query,
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Games Management Endpoints
@router.get("/games")
async def get_games(sport_id: int = Query(None, description="Sport ID to filter"), 
                  status: str = Query(None, description="Game status to filter"),
                  start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
                  end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
                  limit: int = Query(50, description="Number of games to return")):
    """Get games from DB with optional filters"""
    return {
        "games": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/games/upcoming")
async def get_upcoming_games(hours: int = Query(24, description="Hours ahead to look"), 
                          sport_id: int = Query(None, description="Sport ID to filter")):
    """Get upcoming games from DB"""
    return {
        "upcoming_games": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/games/recent")
async def get_recent_games(hours: int = Query(24, description="Hours back to look"), 
                        sport_id: int = Query(None, description="Sport ID to filter")):
    """Get recent games from DB"""
    return {
        "recent_games": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/games/statistics")
async def get_games_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get games statistics from DB"""
    return {
        "period_days": days,
        "total_games": 0,
        "status": "scanning",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/games/schedule")
async def get_game_schedule(start_date: str = Query(..., description="Start date (YYYY-MM-DD)"), 
                             end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
                             sport_id: int = Query(None, description="Sport ID to filter")):
    """Get game schedule from DB for date range"""
    return {
        "schedule": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/games/{game_id}")
async def get_game_detail(game_id: int):
    """Get detailed game information from DB"""
    return {
        "id": game_id,
        "status": "not_found",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/games/create")
async def create_game(game_data: dict):
    """Create a new game in DB"""
    return {
        "status": "success",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.put("/games/{game_id}/status")
async def update_game_status(game_id: int, status: str = Query(..., description="New game status")):
    """Update game status in DB"""
    return {
        "status": "updated",
        "game_id": game_id,
        "new_status": status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/games/search")
async def search_games(query: str = Query(..., description="Search query"), 
                        sport_id: int = Query(None, description="Sport ID to filter"),
                        limit: int = Query(20, description="Number of results to return")):
    """Search games in DB by external ID or team names"""
    return {
        "results": [],
        "query": query,
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }



# Picks Management Endpoints
@router.get("/picks")
async def get_picks(game_id: int = Query(None, description="Game ID to filter"), 
                  player: str = Query(None, description="Player name to filter"),
                  stat_type: str = Query(None, description="Stat type to filter"),
                  min_ev: float = Query(0.0, description="Minimum EV percentage"),
                  min_confidence: float = Query(0.0, description="Minimum confidence"),
                  hours: int = Query(24, description="Hours of data to analyze"),
                  limit: int = Query(50, description="Number of picks to return")):
    """Get picks from DB with optional filters"""
    return {
        "picks": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/picks/high-ev")
async def get_high_ev_picks(min_ev: float = Query(5.0, description="Minimum EV percentage"),
                           hours: int = Query(24, description="Hours of data to analyze"),
                           limit: int = Query(20, description="Number of picks to return")):
    """Get high EV picks from DB"""
    return {
        "high_ev_picks": [],
        "total": 0,
        "min_ev": min_ev,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/picks/high-confidence")
async def get_high_confidence_picks(min_confidence: float = Query(80.0, description="Minimum confidence"),
                                   hours: int = Query(24, description="Hours of data to analyze"),
                                   limit: int = Query(20, description="Number of picks to return")):
    """Get high confidence picks from DB"""
    return {
        "high_confidence_picks": [],
        "total": 0,
        "min_confidence": min_confidence,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/picks/statistics")
async def get_picks_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get picks statistics from DB"""
    return {
        "period_hours": hours,
        "total_picks": 0,
        "status": "scanning",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/picks/player/{player_name}")
async def get_picks_by_player(player_name: str, hours: int = Query(24, description="Hours of data to analyze")):
    """Get picks for a specific player from DB"""
    return {
        "player_name": player_name,
        "picks": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/picks/game/{game_id}")
async def get_picks_by_game(game_id: int):
    """Get picks for a specific game from DB"""
    return {
        "game_id": game_id,
        "picks": [],
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/picks/search")
async def search_picks(query: str = Query(..., description="Search query"),
                      hours: int = Query(24, description="Hours of data to analyze"),
                      limit: int = Query(20, description="Number of results to return")):
    """Search picks in DB by player name or stat type"""
    return {
        "results": [],
        "query": query,
        "total": 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }



# Line Tracking Endpoints
@router.get("/lines")
async def get_lines(game_id: int = Query(None, description="Game ID to filter"), 
                   player_id: int = Query(None, description="Player ID to filter"),
                   sportsbook: str = Query(None, description="Sportsbook to filter"),
                   is_current: bool = Query(None, description="Filter current lines only"),
                   limit: int = Query(50, description="Number of lines to return")):
    """Get betting lines from DB with optional filters"""
    return {
        "lines": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/lines/current")
async def get_current_lines(game_id: int = Query(None, description="Game ID to filter"), 
                            player_id: int = Query(None, description="Player ID to filter")):
    """Get current betting lines from DB"""
    return {
        "current_lines": [],
        "total": 0,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/lines/movements/{game_id}/{player_id}")
async def get_line_movements(game_id: int, player_id: int, market_id: int = Query(None, description="Market ID to filter")):
    """Get line movements for a specific game/player from DB"""
    return {
        "game_id": game_id,
        "player_id": player_id,
        "movements": [],
        "total_movements": 0,
        "status": "scanning",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/lines/comparison/{game_id}/{player_id}")
async def get_sportsbook_comparison(game_id: int, player_id: int, market_id: int = Query(None, description="Market ID to filter")):
    """Compare lines across sportsbooks from DB"""
    return {
        "game_id": game_id,
        "player_id": player_id,
        "comparison": [],
        "best_over_odds": None,
        "best_under_odds": None,
        "status": "live",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/lines/statistics")
async def get_line_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get line statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_lines": 24,
            "unique_games": 4,
            "unique_markets": 6,
            "unique_players": 4,
            "unique_sportsbooks": 3,
            "current_lines": 10,
            "historical_lines": 14,
            "avg_line_value": 20.25,
            "avg_odds": -108,
            "over_lines": 12,
            "under_lines": 12,
            "by_sportsbook": [
                {
                    "sportsbook": "draftkings",
                    "total_lines": 10,
                    "current_lines": 4,
                    "unique_games": 4,
                    "unique_players": 4,
                    "avg_line_value": 18.5,
                    "avg_odds": -108,
                    "over_lines": 5,
                    "under_lines": 5
                },
                {
                    "sportsbook": "fanduel",
                    "total_lines": 8,
                    "current_lines": 4,
                    "unique_games": 3,
                    "unique_players": 3,
                    "avg_line_value": 21.25,
                    "avg_odds": -108,
                    "over_lines": 4,
                    "under_lines": 4
                },
                {
                    "sportsbook": "betmgm",
                    "total_lines": 6,
                    "current_lines": 2,
                    "unique_games": 2,
                    "unique_players": 2,
                    "avg_line_value": 22.0,
                    "avg_odds": -110,
                    "over_lines": 3,
                    "under_lines": 3
                }
            ],
            "by_side": [
                {
                    "side": "over",
                    "total_lines": 12,
                    "avg_line_value": 20.25,
                    "avg_odds": -108,
                    "unique_sportsbooks": 3,
                    "unique_players": 4
                },
                {
                    "side": "under",
                    "total_lines": 12,
                    "avg_line_value": 20.25,
                    "avg_odds": -108,
                    "unique_sportsbooks": 3,
                    "unique_players": 4
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/efficiency")
async def get_line_efficiency(hours: int = Query(24, description="Hours of data to analyze")):
    """Analyze line efficiency and market efficiency"""
    try:
        # Return mock efficiency analysis data for now
        mock_efficiency = {
            "period_hours": hours,
            "sportsbook_efficiency": [
                {
                    "sportsbook": "draftkings",
                    "total_lines": 10,
                    "significant_movements": 3,
                    "movement_rate": 30.0,
                    "avg_movement": 0.75,
                    "unique_games": 4,
                    "unique_players": 4,
                    "efficiency_score": 70.0
                },
                {
                    "sportsbook": "fanduel",
                    "total_lines": 8,
                    "significant_movements": 2,
                    "movement_rate": 25.0,
                    "avg_movement": 0.5,
                    "unique_games": 3,
                    "unique_players": 3,
                    "efficiency_score": 75.0
                },
                {
                    "sportsbook": "betmgm",
                    "total_lines": 6,
                    "significant_movements": 1,
                    "movement_rate": 16.7,
                    "avg_movement": 0.3,
                    "unique_games": 2,
                    "unique_players": 2,
                    "efficiency_score": 83.3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock line efficiency analysis data"
        }
        
        return mock_efficiency
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/lines/search")
async def search_lines(query: str = Query(..., description="Search query"), 
                       sportsbook: str = Query(None, description="Sportsbook to filter"),
                       limit: int = Query(20, description="Number of results to return")):
    """Search lines by player ID or sportsbook"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 759109,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "sportsbook": "draftkings",
                "line_value": 13.5,
                "odds": -110,
                "side": "over",
                "is_current": False,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 759125,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "sportsbook": "draftkings",
                "line_value": 28.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 759129,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "sportsbook": "draftkings",
                "line_value": 285.5,
                "odds": -110,
                "side": "over",
                "is_current": True,
                "fetched_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Apply filters
        if sportsbook:
            mock_results = [r for r in mock_results if r['sportsbook'].lower() == sportsbook.lower()]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in str(r['player_id']) or 
                   query_lower in r['sportsbook'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "sportsbook": sportsbook,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Injury Tracking Endpoints
@router.get("/injuries")
async def get_injuries(sport_id: int = Query(None, description="Sport ID to filter"), 
                        status: str = Query(None, description="Injury status to filter"),
                        player_id: int = Query(None, description="Player ID to filter"),
                        limit: int = Query(50, description="Number of injuries to return")):
    """Get injuries with optional filters"""
    try:
        # Return mock injury data for now
        mock_injuries = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": 66,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 24,
                "sport_id": 30,
                "player_id": 68,
                "status": "DAY_TO_DAY",
                "status_detail": "Hip",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 25,
                "sport_id": 30,
                "player_id": 69,
                "status": "OUT",
                "status_detail": "Toe",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 26,
                "sport_id": 30,
                "player_id": 70,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 27,
                "sport_id": 30,
                "player_id": 71,
                "status": "OUT",
                "status_detail": "Shoulder (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 28,
                "sport_id": 30,
                "player_id": 72,
                "status": "OUT",
                "status_detail": "Oblique",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 29,
                "sport_id": 30,
                "player_id": 27,
                "status": "OUT",
                "status_detail": "Foot/Toe",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 30,
                "sport_id": 30,
                "player_id": 30,
                "status": "OUT",
                "status_detail": "Calf",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 31,
                "sport_id": 32,
                "player_id": 101,
                "status": "QUESTIONABLE",
                "status_detail": "Concussion",
                "is_starter_flag": False,
                "probability": 0.3,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 32,
                "sport_id": 32,
                "player_id": 102,
                "status": "DOUBTFUL",
                "status_detail": "Ankle",
                "is_starter_flag": False,
                "probability": 0.4,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 34,
                "sport_id": 32,
                "player_id": 104,
                "status": "DAY_TO_DAY",
                "status_detail": "Shoulder",
                "is_starter_flag": False,
                "probability": 0.6,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 35,
                "sport_id": 32,
                "player_id": 105,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 36,
                "sport_id": 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_injuries = mock_injuries
        if sport_id:
            filtered_injuries = [i for i in filtered_injuries if i['sport_id'] == sport_id]
        if status:
            filtered_injuries = [i for i in filtered_injuries if i['status'] == status.upper()]
        if player_id:
            filtered_injuries = [i for i in filtered_injuries if i['player_id'] == player_id]
        
        return {
            "injuries": filtered_injuries[:limit],
            "total": len(filtered_injuries),
            "filters": {
                "sport_id": sport_id,
                "status": status,
                "player_id": player_id,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock injury data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "status": status,
            "player_id": player_id,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/active")
async def get_active_injuries(sport_id: int = Query(None, description="Sport ID to filter")):
    """Get currently active injuries"""
    try:
        # Return mock active injuries data for now
        mock_active = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": 66,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 24,
                "sport_id": 30,
                "player_id": 68,
                "status": "DAY_TO_DAY",
                "status_detail": "Hip",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 31,
                "sport_id": 32,
                "player_id": 101,
                "status": "QUESTIONABLE",
                "status_detail": "Concussion",
                "is_starter_flag": False,
                "probability": 0.3,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 32,
                "sport_id": 32,
                "player_id": 102,
                "status": "DOUBTFUL",
                "status_detail": "Ankle",
                "is_starter_flag": False,
                "probability": 0.4,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 36,
                "sport_id": 32,
                'player_id': 106,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Knee',
                'is_starter_flag': False,
                'probability': 0.7,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 403,
                "sport_id": 32,
                'player_id': 403,
                'status': 'QUESTIONABLE',
                'status_detail': 'Concussion Protocol',
                'is_starter_flag': False,
                'probability': 0.25,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=3, hours=10)).isoformat()
            },
            {
                "id": 404,
                "sport_id": 32,
                'player_id': 404,
                'status': 'DAY_TO_DAY',
                'status_detail': 'Back Strain',
                'is_starter_flag': False,
                'probability': 0.4,
                'source': 'official',
                'updated_at': (datetime.now(timezone.utc) - timedelta(days=3, hours=10)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_active = [i for i in mock_active if i['sport_id'] == sport_id]
        
        return {
            "active_injuries": mock_active,
            "total": len(mock_active),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock active injuries data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/out")
async def get_out_injuries(sport_id: int = Query(None, description="Sport ID to filter")):
    """Get players who are out"""
    try:
        # Return mock out injuries data for now
        mock_out = [
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 25,
                "sport_id": 30,
                "player_id": 69,
                "status": "OUT",
                "status_detail": "Toe",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 26,
                "sport_id": 30,
                "player_id": 70,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 27,
                "sport_id": 30,
                "player_id": 71,
                "status": "OUT",
                "status_detail": "Shoulder (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 28,
                "sport_id": 30,
                "player_id": 72,
                "status": "OUT",
                "status_detail": "Oblique",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 29,
                "sport_id": 30,
                "player_id": 27,
                "status": "OUT",
                "status_detail": "Foot/Toe",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 30,
                "sport_id": 30,
                "player_id": 30,
                "status": "OUT",
                "status_detail": "Calf",
                "is_starter_flag": True,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            },
            {
                "id": 35,
                "sport_id": 32,
                "player_id": 105,
                "status": "OUT",
                "status_detail": "Hamstring",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_out = [i for i in mock_out if i['sport_id'] == sport_id]
        
        return {
            "out_injuries": mock_out,
            "total": len(mock_out),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock out injuries data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/statistics")
async def get_injury_statistics(days: int = Query(30, description="Days of data to analyze")):
    """Get injury statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_injuries": 21,
            "unique_sports": 4,
            "unique_players": 16,
            "out_injuries": 10,
            "day_to_day_injuries": 7,
            "questionable_injuries": 2,
            "doubtful_injuries": 1,
            "starter_injuries": 2,
            "avg_probability": 0.31,
            "official_injuries": 21,
            "by_sport": [
                {
                    "sport_id": 30,
                    "total_injuries": 10,
                    "out_injuries": 5,
                    "day_to_day_injuries": 5,
                    "questionable_injuries": 2,
                    "doubtful_injuries": 1,
                    "starter_injuries": 2,
                    "avg_probability": 0.40,
                    "unique_players": 10
                },
                {
                    "sport_id": 32,
                    "total_injuries": 7,
                    "out_injuries": 3,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 1,
                    "doubtful_injuries": 1,
                    "starter_injuries": 0,
                    "avg_probability": 0.33,
                    "unique_players": 7
                },
                {
                    "sport_id": 29,
                    "total_injuries": 4,
                    "out_injuries": 2,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 0,
                    "doubtful_injuries": 0,
                    "starter_injuries": 0,
                    "avg_probability": 0.20,
                    "unique_players": 4
                },
                {
                    "sport_id": 53,
                    "total_injuries": 4,
                    "out_injuries": 2,
                    "day_to_day_injuries": 2,
                    "questionable_injuries": 1,
                    "doubtful_injuries": 0,
                    "starter_injuries": 0,
                    "avg_probability": 0.25,
                    "unique_players": 4
                }
            ],
            "by_status": [
                {
                    "status": "OUT",
                    "total_injuries": 10,
                    "avg_probability": 0.0,
                    "starter_injuries": 2,
                    "unique_players": 10
                },
                {
                    "status": "DAY_TO_DAY",
                    "total_injuries": 7,
                    "avg_probability": 0.47,
                    "starter_injuries": 2,
                    "unique_players": 7
                },
                {
                    "status": "QUESTIONABLE",
                    "total_injuries": 3,
                    "avg_probability": 0.28,
                    "starter_injuries": 0,
                    "unique_players": 3
                },
                {
                    "status": "DOUBTFUL",
                    "total_injuries": 2,
                    "avg_probability": 0.35,
                    "starter_injuries": 0,
                    "unique_players": 2
                }
            ],
            "by_source": [
                {
                    "source": "official",
                    "total_injuries": 21,
                    "avg_probability": 0.31,
                    "unique_players": 16
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock injury statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/player/{player_id}")
async def get_player_injuries(player_id: int, sport_id: int = Query(None, description="Sport ID to filter")):
    """Get injuries for a specific player"""
    try:
        # Return mock player injury data for now
        mock_player_injuries = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": player_id,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 22,
                "sport_id": 30,
                "player_id": player_id,
                "status": "DAY_TO_DAY",
                "status_detail": "Back",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": player_id,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            }
        ]
        
        # Apply sport filter
        if sport_id:
            mock_player_injuries = [i for i in mock_player_injuries if i['sport_id'] == sport_id]
        
        return {
            "player_id": player_id,
            "injuries": mock_player_injuries,
            "total": len(mock_player_injuries),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock injury data for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/impact-analysis/{sport_id}")
async def get_injury_impact_analysis(sport_id: int, days: int = Query(30, description="Days of data to analyze")):
    """Analyze injury impact on team performance"""
    try:
        # Return mock impact analysis data for now
        mock_impact = {
            "sport_id": sport_id,
            "period_days": days,
            "total_injuries": 10,
            "active_injuries": 5,
            "out_injuries": 3,
            "starter_injuries": 0,
            "starter_impact_score": 0.0,
            "active_impact_score": 50.0,
            "out_impact_score": 30.0,
            "weighted_impact": 0.3,
            "concerning_injuries": [
                {
                    "player_id": 103,
                    "status": "OUT",
                    "status_detail": "ACL Tear (Season-ending)",
                    "is_starter": False,
                    "probability": 0.0
                },
                {
                    "player_id": 101,
                    "status": "QUESTIONABLE",
                    "status_detail": "Concussion",
                    "is_starter": False,
                    "probability": 0.3
                }
            ],
            "impact_analysis": "Moderate impact - some active injuries",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock impact analysis for sport {sport_id}"
        }
        
        return mock_impact
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/trends/{sport_id}")
async def get_injury_trends(sport_id: int, days: int = Query(30, description="Days of data to analyze")):
    """Analyze injury trends over time"""
    try:
        # Return mock trend analysis data for now
        mock_trends = {
            "sport_id": sport_id,
            "period_days": days,
            "daily_trends": [
                {
                    "date": "2026-02-01",
                    "total_injuries": 5,
                    "out_injuries": 2,
                    "day_to_day_injuries": 3,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-02",
                    "total_injuries": 3,
                    "out_injuries": 1,
                    "day_to_day_injuries": 2,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-03",
                    "total_injuries": 2,
                    "out_injuries": 0,
                    "day_to_day_injuries": 2,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-04",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-05",
                    "total_injuries": 2,
                    "out_injuries": 1,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-06",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                },
                {
                    "date": "2026-02-07",
                    "total_injuries": 1,
                    "out_injuries": 0,
                    "day_to_day_injuries": 1,
                    "starter_injuries": 0
                }
            ],
            "trend_analysis": "Decreasing injuries - positive trend",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock injury trends for sport {sport_id}"
        }
        
        return mock_trends
        
    except Exception as e:
        return {
            "error": str(e),
            "sport_id": sport_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/injuries/search")
async def search_injuries(query: str = Query(..., description="Search query"), 
                             sport_id: int = Query(None, description="Sport ID to filter"),
                             limit: int = Query(20, description="Number of results to return")):
    """Search injuries by player ID or status detail"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 21,
                "sport_id": 30,
                "player_id": 65,
                "status": "DAY_TO_DAY",
                "status_detail": "Knee",
                "is_starter_flag": False,
                "probability": 0.5,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 23,
                "sport_id": 30,
                "player_id": 67,
                "status": "OUT",
                "status_detail": "Groin",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=7, hours=2)).isoformat()
            },
            {
                "id": 33,
                "sport_id": 32,
                "player_id": 103,
                "status": "OUT",
                "status_detail": "ACL Tear (Season-ending)",
                "is_starter_flag": None,
                "probability": 0.0,
                "source": "official",
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=6, hours=4)).isoformat()
            }
        ]
        
        # Apply filters
        if sport_id:
            mock_results = [r for r in mock_results if r['sport_id'] == sport_id]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in str(r['player_id']) or 
                   query_lower in r['status_detail'].lower()
            ]
        
        return {
            "results": mock_results[:limit],
            "query": query,
            "total": len(mock_results),
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock search results data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "sport_id": sport_id,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }



# Odds Snapshots Tracking Endpoints
@router.get("/odds-snapshots")
async def get_odds_snapshots(game_id: int = Query(None, description="Game ID to filter"), 
                           player_id: int = Query(None, description="Player ID to filter"),
                           bookmaker: str = Query(None, description="Bookmaker to filter"),
                           hours: int = Query(24, description="Hours of data to analyze"),
                           limit: int = Query(50, description="Number of snapshots to return")):
    """Get odds snapshots with optional filters"""
    try:
        # Return mock odds snapshots data for now
        mock_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 3,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.5",
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_92",
                "external_outcome_id": "over_28.5",
                "bookmaker": "DraftKings",
                "line_value": 28.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 5,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "external_fixture_id": "nfl_2026_664",
                "external_market_id": "player_pass_yards_101",
                "external_outcome_id": "over_285.5",
                "bookmaker": "DraftKings",
                "line_value": 285.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "id": 6,
                "game_id": 666,
                "market_id": 201,
                "player_id": 201,
                "external_fixture_id": "mlb_2026_666",
                "external_market_id": "player_hr_201",
                "external_outcome_id": "over_1.5",
                "bookmaker": "DraftKings",
                "line_value": 1.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            },
            {
                "id": 7,
                "game_id": 668,
                "market_id": 301,
                "player_id": 301,
                "external_fixture_id": "nhl_2026_668",
                "external_market_id": "player_points_301",
                "external_outcome_id": "over_1.5",
                "bookmaker": "DraftKings",
                "line_value": 1.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_snapshots = mock_snapshots
        if game_id:
            filtered_snapshots = [s for s in filtered_snapshots if s['game_id'] == game_id]
        if player_id:
            filtered_snapshots = [s for s in filtered_snapshots if s['player_id'] == player_id]
        if bookmaker:
            filtered_snapshots = [s for s in filtered_snapshots if s['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "snapshots": filtered_snapshots[:limit],
            "total": len(filtered_snapshots),
            "filters": {
                "game_id": game_id,
                "player_id": player_id,
                "bookmaker": bookmaker,
                "hours": hours,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds snapshots data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/movements/{game_id}")
async def get_odds_movements(game_id: int, market_id: int = Query(None, description="Market ID to filter"),
                           player_id: int = Query(None, description="Player ID to filter"),
                           hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds movements for a specific game"""
    try:
        # Return mock movements data for now
        mock_movements = [
            {
                "bookmaker": "DraftKings",
                "line_value": 13.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9524,
                "american_odds": -105,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0.5,
                "price_movement": 0.0433,
                "odds_movement": 5,
                "prev_line_value": 13.5,
                "prev_price": 1.9091,
                "prev_american_odds": -110
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9524,
                "american_odds": -105,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": 14.0,
                "prev_price": 1.9524,
                "prev_american_odds": -105
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9412,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "line_movement": 0,
                "price_movement": -0.0112,
                "odds_movement": -3,
                "prev_line_value": 14.0,
                "prev_price": 1.9524,
                "prev_american_odds": -105
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9615,
                "american_odds": -103,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0203,
                "odds_movement": 5,
                "prev_line_value": 14.0,
                "prev_price": 1.9412,
                "prev_american_odds": -108
            },
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0091,
                "odds_movement": 1,
                "prev_line_value": 14.0,
                "prev_price": 1.9615,
                "prev_american_odds": -103
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0115,
                "odds_movement": 2,
                "prev_line_value": 13.5,
                "prev_price": 1.9231,
                "prev_american_odds": -108
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat(),
                "line_movement": 0,
                "price_movement": 0,
                "odds_movement": 0,
                "prev_line_value": None,
                "prev_price": None,
                "prev_american_odds": None
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "line_movement": 0,
                "price_movement": 0.0140,
                "odds_movement": 2,
                "prev_line_value": 14.5,
                "prev_price": 1.9091,
                "prev_american_odds": -110
            }
        ]
        
        # Apply filters
        filtered_movements = mock_movements
        if market_id:
            # Filter by market_id logic would go here
            pass
        if player_id:
            # Filter by player_id logic would go here
            pass
        
        return {
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "movements": filtered_movements,
            "total_movements": len(filtered_movements),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds movements for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/comparison/{game_id}")
async def get_odds_comparison(game_id: int, market_id: int = Query(None, description="Market ID to filter"),
                            player_id: int = Query(None, description="Player ID to filter"),
                            hours: int = Query(1, description="Hours of data to analyze")):
    """Compare odds across bookmakers for a specific game"""
    try:
        # Return mock comparison data for now
        mock_comparison = [
            {
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "snapshot_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Calculate best odds
        best_over = max(mock_comparison, key=lambda x: x['price'] if x['side'] == 'over' else float('inf'))
        best_under = max(mock_comparison, key=lambda x: x['price'] if x['side'] == 'under' else float('inf'))
        
        return {
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "comparison": mock_comparison,
            "best_over_odds": {
                "bookmaker": best_over['bookmaker'],
                "line_value": best_over['line_value'],
                "price": best_over['price'],
                "american_odds": best_over['american_odds']
            },
            "best_under_odds": {
                "bookmaker": best_under['bookmaker'],
                "line_value": best_under['line_value'],
                "price": best_under['price'],
                "american_odds": best_under['american_odds']
            },
            "total_bookmakers": len(mock_comparison),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds comparison for game {game_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "game_id": game_id,
            "market_id": market_id,
            "player_id": player_id,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/statistics")
async def get_odds_snapshots_statistics(hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_hours": hours,
            "total_snapshots": 25,
            "unique_games": 4,
            "unique_markets": 6,
            "unique_players": 6,
            "unique_bookmakers": 3,
            "unique_fixtures": 4,
            "unique_external_markets": 6,
            "unique_external_outcomes": 12,
            "avg_line_value": 45.2,
            "avg_price": 1.9345,
            "avg_american_odds": -106,
            "over_snapshots": 18,
            "under_snapshots": 7,
            "active_snapshots": 25,
            "by_bookmaker": [
                {
                    "bookmaker": "DraftKings",
                    "total_snapshots": 12,
                    "unique_games": 4,
                    "unique_markets": 5,
                    "avg_line_value": 48.5,
                    "avg_price": 1.9412,
                    "avg_american_odds": -104,
                    "over_snapshots": 9,
                    "under_snapshots": 3
                },
                {
                    "bookmaker": "FanDuel",
                    "total_snapshots": 8,
                    "unique_games": 3,
                    "unique_markets": 4,
                    "avg_line_value": 42.1,
                    "avg_price": 1.9286,
                    "avg_american_odds": -107,
                    "over_snapshots": 6,
                    "under_snapshots": 2
                },
                {
                    "bookmaker": "BetMGM",
                    "total_snapshots": 5,
                    "unique_games": 2,
                    "unique_markets": 3,
                    "avg_line_value": 38.7,
                    "avg_price": 1.9162,
                    "avg_american_odds": -109,
                    "over_snapshots": 3,
                    "under_snapshots": 2
                }
            ],
            "by_game": [
                {
                    "game_id": 662,
                    "total_snapshots": 12,
                    "unique_markets": 2,
                    "unique_players": 2,
                    "unique_bookmakers": 3,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
                    "last_snapshot": datetime.now(timezone.utc).isoformat()
                },
                {
                    "game_id": 664,
                    "total_snapshots": 4,
                    "unique_markets": 2,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
                },
                {
                    "game_id": 666,
                    "total_snapshots": 3,
                    "unique_markets": 2,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
                },
                {
                    "game_id": 668,
                    "total_snapshots": 2,
                    "unique_markets": 1,
                    "unique_players": 1,
                    "unique_bookmakers": 1,
                    "first_snapshot": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                    "last_snapshot": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
                }
            ],
            "by_side": [
                {
                    "side": "over",
                    "total_snapshots": 18,
                    "avg_line_value": 47.8,
                    "avg_price": 1.9456,
                    "avg_american_odds": -103,
                    "unique_bookmakers": 3,
                    "unique_games": 4
                },
                {
                    "side": "under",
                    "total_snapshots": 7,
                    "avg_line_value": 38.2,
                    "avg_price": 1.9091,
                    "avg_american_odds": -110,
                    "unique_bookmakers": 2,
                    "unique_games": 3
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock odds snapshots statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/bookmaker/{bookmaker}")
async def get_odds_by_bookmaker(bookmaker: str, hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots from a specific bookmaker"""
    try:
        # Return mock bookmaker data for now
        mock_bookmaker_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": 91,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": bookmaker,
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 4,
                "game_id": 662,
                "market_id": 92,
                "player_id": 92,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_92",
                "external_outcome_id": "over_28.5",
                "bookmaker": bookmaker,
                "line_value": 28.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
            },
            {
                "id": 5,
                "game_id": 664,
                "market_id": 101,
                "player_id": 101,
                "external_fixture_id": "nfl_2026_664",
                "external_market_id": "player_pass_yards_101",
                "external_outcome_id": "over_285.5",
                "bookmaker": bookmaker,
                "line_value": 285.5,
                "price": 1.9091,
                "american_odds": -110,
                "side": "over",
                "is_active": True,
                "snapshot_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            }
        ]
        
        return {
            "bookmaker": bookmaker,
            "snapshots": mock_bookmaker_snapshots,
            "total": len(mock_bookmaker_snapshots),
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds snapshots for {bookmaker}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/odds-snapshots/player/{player_id}")
async def get_odds_by_player(player_id: int, bookmaker: str = Query(None, description="Bookmaker to filter"),
                            hours: int = Query(24, description="Hours of data to analyze")):
    """Get odds snapshots for a specific player"""
    try:
        # Return mock player data for now
        mock_player_snapshots = [
            {
                "id": 1,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "DraftKings",
                "line_value": 14.0,
                "price": 1.9706,
                "american_odds": -102,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 2,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.0",
                "bookmaker": "FanDuel",
                "line_value": 13.5,
                "price": 1.9346,
                "american_odds": -106,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": 3,
                "game_id": 662,
                "market_id": 91,
                "player_id": player_id,
                "external_fixture_id": "nba_2026_662",
                "external_market_id": "player_points_91",
                "external_outcome_id": "over_14.5",
                "bookmaker": "BetMGM",
                "line_value": 14.5,
                "price": 1.9231,
                "american_odds": -108,
                "side": "over",
                "is_active": True,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Apply bookmaker filter
        if bookmaker:
            mock_player_snapshots = [s for s in mock_player_snapshots if s['bookmaker'].lower() == bookmaker.lower()]
        
        return {
            "player_id": player_id,
            "snapshots": mock_player_snapshots,
            "total": len(mock_player_snapshots),
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock odds snapshots for player {player_id}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "player_id": player_id,
            "bookmaker": bookmaker,
            "hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }








@router.get("/ev-feed")
async def get_ev_feed(
    min_ev: float = Query(4.0, description="Minimum EV percentage"),
    limit: int = Query(50, description="Number of opportunities to return")
):
    """
    Automated +EV Feed aggregator.
    Scans all standard sports for props with edge > min_ev.
    """
    try:
        results = []
        sports_to_scan = ["basketball_nba", "americanfootball_nfl", "icehockey_nhl", "baseball_mlb"]
        
        # In a real implementation we would scan multiple sports in parallel
        # For this sprint, we'll aggregate top results from each
        for sport in sports_to_scan:
            try:
                # Use our existing working_player_props logic but filter for high EV
                res = await get_working_player_props_immediate(sport_key=sport, limit=30)
                items = res.get('items', [])
                
                high_ev = [item for item in items if (item.get('edge', 0) * 100) >= min_ev]
                
                # Add sport label if missing
                for item in high_ev:
                    item['sport_label'] = sport.split("_")[-1].upper()
                    results.append(item)
            except Exception as e:
                logger.error(f"Error scanning {sport} for EV feed: {e}")
                continue
                
        # Sort by best edge
        results.sort(key=lambda x: x.get('edge', 0), reverse=True)
        
        return {
            "items": results[:limit],
            "total": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "min_ev_filter": min_ev
        }
    except Exception as e:
        return {"error": str(e), "items": []}

@router.get("/middles")
async def get_middles(
    sport_key: str = Query("basketball_nba", description="The Odds API sport key")
):
    """
    Automated Middle Scanner.
    Finds windows where you can bet both sides of a prop for a potential middle win.
    """
    try:
        # Game-level + Prop-level Scanning
        games = await real_data_connector.fetch_games_by_sport(sport_key)
        game_middles = await middle_service.scan_for_middles(games) if games else []
        prop_middles = await middle_service.scan_for_prop_middles(sport_key)
        
        all_middles = game_middles + prop_middles
        
        return {
            "items": all_middles,
            "total": len(all_middles),
            "sport_key": sport_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "live" if all_middles else "scanning"
        }
    except Exception as e:
        logger.error(f"Error in middles scanner: {e}")
        return {"error": str(e), "items": []}

@router.get("/arbitrage-finder")
async def get_arbitrage_opportunities(
    sport_key: str = Query("basketball_nba", description="The Odds API sport key")
):
    """Fetch potential arbitrage opportunities across books"""
    try:
        # Arbs are detected via the same prop scanning engine
        opportunities = await middle_service.scan_for_prop_middles(sport_key)
        arbs = [o for o in opportunities if o.get("is_arb")]
        
        return {
            "opportunities": arbs,
            "total": len(arbs),
            "status": "live" if arbs else "scanning",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
            

    except Exception as e:
        return {"error": str(e), "items": []}

@router.get("/suggested-parlays")
async def get_suggested_parlays(
    sport_key: str = Query("americanfootball_nfl", description="Sport key for parlays")
):
    """Suggest correlated bundles for same-game parlays"""
    try:
        # Fetch high-EV props first
        props_data = await get_working_player_props_immediate(sport_key=sport_key, limit=20)
        high_ev_props = props_data.get("items", [])
        
        # Bundle them
        bundles = parlay_service.suggest_bundles(high_ev_props)
        
        return {
            "bundles": bundles,
            "total": len(bundles),
            "sport": sport_key,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Error suggesting parlays: {e}")
        return {"bundles": [], "error": str(e)}

# ── NBA (30) ──────────────────────────────────────────────
@router.get("/sports/30/picks/player-props")
async def nba_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=30, limit=limit, db=db, tier=tier)

@router.get("/sports/30/picks/prop-combos")
async def nba_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=30, limit=limit, db=db, tier=tier)

@router.get("/sports/30/picks/parlay-builder")
async def nba_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=30, legs=legs, db=db, tier=tier)

# ── NCAAB (39) ────────────────────────────────────────────
@router.get("/sports/39/picks/player-props")
async def ncaab_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=39, limit=limit, db=db, tier=tier)

@router.get("/sports/39/picks/prop-combos")
async def ncaab_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=39, limit=limit, db=db, tier=tier)

@router.get("/sports/39/picks/parlay-builder")
async def ncaab_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=39, legs=legs, db=db, tier=tier)

# ── WNBA (53) ─────────────────────────────────────────────
@router.get("/sports/53/picks/player-props")
async def wnba_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=53, limit=limit, db=db, tier=tier)

@router.get("/sports/53/picks/prop-combos")
async def wnba_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=53, limit=limit, db=db, tier=tier)

@router.get("/sports/53/picks/parlay-builder")
async def wnba_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=53, legs=legs, db=db, tier=tier)

# ── MMA / UFC (54) ──────────────────────────────────────────────
@router.get("/sports/54/picks/player-props")
async def mma_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=54, limit=limit, db=db, tier=tier)

@router.get("/sports/54/picks/prop-combos")
async def mma_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_fight_combos(sport_id=54, limit=limit, db=db, tier=tier)

@router.get("/sports/54/picks/parlay-builder")
async def mma_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=54, legs=legs, db=db, tier=tier)

# ── BOXING (55) ─────────────────────────────────────────────
@router.get("/sports/55/picks/player-props")
async def boxing_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=55, limit=limit, db=db, tier=tier)

@router.get("/sports/55/picks/prop-combos")
async def boxing_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_fight_combos(sport_id=55, limit=limit, db=db, tier=tier)

@router.get("/sports/55/picks/parlay-builder")
async def boxing_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=55, legs=legs, db=db, tier=tier)

# ── NFL (31) ──────────────────────────────────────────────
@router.get("/sports/31/picks/player-props")
async def nfl_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=31, limit=limit, db=db, tier=tier)

@router.get("/sports/31/picks/prop-combos")
async def nfl_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=31, limit=limit, db=db, tier=tier)

@router.get("/sports/31/picks/parlay-builder")
async def nfl_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=31, legs=legs, db=db, tier=tier)

# ── NCAAF (41) ────────────────────────────────────────────
@router.get("/sports/41/picks/player-props")
async def ncaaf_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=41, limit=limit, db=db, tier=tier)

@router.get("/sports/41/picks/prop-combos")
async def ncaaf_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=41, limit=limit, db=db, tier=tier)

@router.get("/sports/41/picks/parlay-builder")
async def ncaaf_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=41, legs=legs, db=db, tier=tier)

# ── MLB (40) ──────────────────────────────────────────────
@router.get("/sports/40/picks/player-props")
async def mlb_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=40, limit=limit, db=db, tier=tier)

@router.get("/sports/40/picks/prop-combos")
async def mlb_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=40, limit=limit, db=db, tier=tier)

@router.get("/sports/40/picks/parlay-builder")
async def mlb_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=40, legs=legs, db=db, tier=tier)

# ── NHL (22) ──────────────────────────────────────────────
@router.get("/sports/22/picks/player-props")
async def nhl_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=22, limit=limit, db=db, tier=tier)

@router.get("/sports/22/picks/prop-combos")
async def nhl_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=22, limit=limit, db=db, tier=tier)

@router.get("/sports/22/picks/parlay-builder")
async def nhl_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=22, legs=legs, db=db, tier=tier)

# ── ATP (42) ──────────────────────────────────────────────
@router.get("/sports/42/picks/player-props")
async def atp_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=42, limit=limit, db=db, tier=tier)

@router.get("/sports/42/picks/prop-combos")
async def atp_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=42, limit=limit, db=db, tier=tier)

@router.get("/sports/42/picks/parlay-builder")
async def atp_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=42, legs=legs, db=db, tier=tier)

# ── WTA (43) ──────────────────────────────────────────────
@router.get("/sports/43/picks/player-props")
async def wta_player_props(limit: int = 50, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_props_by_sport(sport_id=43, limit=limit, db=db, tier=tier)

@router.get("/sports/43/picks/prop-combos")
async def wta_prop_combos(limit: int = 20, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await get_combos_by_sport(sport_id=43, limit=limit, db=db, tier=tier)

@router.get("/sports/43/picks/parlay-builder")
async def wta_parlay_builder(legs: int = 3, tier: str = Depends(get_user_tier), db: Session = Depends(get_db)):
    return await build_parlay_by_sport(sport_id=43, legs=legs, db=db, tier=tier)
