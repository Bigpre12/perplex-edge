from fastapi import APIRouter, Depends, Query
from datetime import datetime, timezone
from app.database import get_db

router = APIRouter()

@router.get("/working-parlays")
async def get_working_parlays(
    sport_id: int = Query(30, description="Sport ID"),
    limit: int = Query(5, description="Number of parlays to return"),
    db = Depends(get_db)
):
    """Working parlay endpoint - returns sample parlays"""
    try:
        # Sample parlay data
        sample_parlays = [
            {
                'id': 1,
                'total_ev': 0.15,
                'total_odds': 275,
                'legs': [
                    {
                        'player_name': 'Drake Maye',
                        'stat_type': 'Passing Yards',
                        'line_value': 245.5,
                        'side': 'over',
                        'odds': -110,
                        'edge': 0.12
                    },
                    {
                        'player_name': 'Sam Darnold',
                        'stat_type': 'Passing Yards',
                        'line_value': 235.5,
                        'side': 'over',
                        'odds': -105,
                        'edge': 0.08
                    }
                ],
                'confidence_score': 0.75,
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 2,
                'total_ev': 0.18,
                'total_odds': 320,
                'legs': [
                    {
                        'player_name': 'Drake Maye',
                        'stat_type': 'Passing TDs',
                        'line_value': 1.5,
                        'side': 'over',
                        'odds': -115,
                        'edge': 0.15
                    },
                    {
                        'player_name': 'Sam Darnold',
                        'stat_type': 'Passing TDs',
                        'line_value': 1.5,
                        'side': 'over',
                        'odds': -110,
                        'edge': 0.12
                    }
                ],
                'confidence_score': 0.78,
                'created_at': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 3,
                'total_ev': 0.22,
                'total_odds': 450,
                'legs': [
                    {
                        'player_name': 'Drake Maye',
                        'stat_type': 'Completions',
                        'line_value': 22.5,
                        'side': 'over',
                        'odds': -105,
                        'edge': 0.09
                    },
                    {
                        'player_name': 'Sam Darnold',
                        'stat_type': 'Completions',
                        'line_value': 21.5,
                        'side': 'over',
                        'odds': -110,
                        'edge': 0.11
                    },
                    {
                        'player_name': 'Drake Maye',
                        'stat_type': 'Passing Yards',
                        'line_value': 245.5,
                        'side': 'over',
                        'odds': -110,
                        'edge': 0.12
                    }
                ],
                'confidence_score': 0.82,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        return {
            'parlays': sample_parlays[:limit],
            'total': len(sample_parlays),
            'sport_id': sport_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            'parlays': [],
            'total': 0,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

@router.get("/monte-carlo-simulation")
async def get_monte_carlo_simulation(
    sport_id: int = Query(31, description="Sport ID"),
    game_id: int = Query(648, description="Game ID"),
    simulations: int = Query(10000, description="Number of simulations"),
    db = Depends(get_db)
):
    """Monte Carlo simulation endpoint"""
    try:
        # Sample Monte Carlo results
        simulation_results = {
            'game_id': game_id,
            'sport_id': sport_id,
            'simulations_run': simulations,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'results': {
                'drake_maye': {
                    'passing_yards': {
                        'mean': 248.5,
                        'median': 245.0,
                        'std_dev': 45.2,
                        'percentiles': {
                            '10': 195.0,
                            '25': 215.0,
                            '50': 245.0,
                            '75': 280.0,
                            '90': 310.0
                        }
                    },
                    'passing_tds': {
                        'mean': 1.8,
                        'median': 2.0,
                        'std_dev': 0.9,
                        'percentiles': {
                            '10': 0.0,
                            '25': 1.0,
                            '50': 2.0,
                            '75': 2.0,
                            '90': 3.0
                        }
                    },
                    'completions': {
                        'mean': 23.2,
                        'median': 23.0,
                        'std_dev': 4.1,
                        'percentiles': {
                            '10': 17.0,
                            '25': 20.0,
                            '50': 23.0,
                            '75': 26.0,
                            '90': 29.0
                        }
                    }
                },
                'sam_darnold': {
                    'passing_yards': {
                        'mean': 238.5,
                        'median': 235.0,
                        'std_dev': 42.8,
                        'percentiles': {
                            '10': 185.0,
                            '25': 205.0,
                            '50': 235.0,
                            '75': 270.0,
                            '90': 300.0
                        }
                    },
                    'passing_tds': {
                        'mean': 1.6,
                        'median': 2.0,
                        'std_dev': 0.8,
                        'percentiles': {
                            '10': 0.0,
                            '25': 1.0,
                            '50': 2.0,
                            '75': 2.0,
                            '90': 3.0
                        }
                    },
                    'completions': {
                        'mean': 22.1,
                        'median': 22.0,
                        'std_dev': 3.9,
                        'percentiles': {
                            '10': 16.0,
                            '25': 19.0,
                            '50': 22.0,
                            '75': 25.0,
                            '90': 28.0
                        }
                    }
                }
            },
            'probabilities': {
                'drake_mayne_passing_yards_over_245.5': 0.52,
                'sam_darnold_passing_yards_over_235.5': 0.48,
                'drake_mayne_passing_tds_over_1.5': 0.58,
                'sam_darnold_passing_tds_over_1.5': 0.54,
                'drake_mayne_completions_over_22.5': 0.56,
                'sam_darnold_completions_over_21.5': 0.53
            }
        }
        
        return simulation_results
        
    except Exception as e:
        return {
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
