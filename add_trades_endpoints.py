#!/usr/bin/env python3
"""
ADD TRADES ENDPOINTS - Add master trade tracking endpoints
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta

async def add_trades_endpoints():
    """Add master trade tracking endpoints to immediate working router"""
    
    # Read the current file
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "r") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Define the trades endpoints
    trades_code = '''

# Master Trade Tracking Endpoints
@router.get("/trades")
async def get_trades(season: int = Query(None, description="Season year to filter"),
                     source: str = Query(None, description="Source to filter"),
                     applied: bool = Query(None, description="Applied status to filter"),
                     recent: bool = Query(False, description="Get recent trades"),
                     limit: int = Query(50, description="Number of trades to return")):
    """Get master trades with optional filters"""
    try:
        # Return mock trades data for now
        mock_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": 2024,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            },
            {
                "id": 3,
                "trade_date": "2024-02-18",
                "season_year": 2024,
                "description": "The Indiana Pacers and Portland Trail Blazers completed a trade sending rising star Tyrese Haliburton to Portland in exchange for veteran scorer Damian Lillard. The Pacers get immediate championship help while the Trail Blazers build around their new young star.",
                "headline": "Pacers Send Haliburton to Trail Blazers for Lillard",
                "source_url": "https://www.bleacherreport.com/nba/articles/pacers-send-haliburton-to-trail-blazers-for-lillard",
                "source": "Bleacher Report",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": "NFL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            },
            {
                "id": 5,
                "trade_date": "2024-03-22",
                "season_year": 2024,
                "description": "The Carolina Panthers traded running back Christian McCaffrey to the San Francisco 49ers in exchange for veteran linebacker Bobby Wagner. The 49ers add an elite offensive weapon while the Panthers strengthen their defense.",
                "headline": "Panthers Trade McCaffrey to 49ers for Wagner",
                "source_url": "https://www.espn.com/nfl/story/_/id/23456789/panthers-trade-mccaffrey-to-49ers-for-wagner",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=28)).isoformat()
            },
            {
                "id": 6,
                "trade_date": "2024-07-31",
                "season_year": 2024,
                "description": "The New York Mets traded power-hitting first baseman Pete Alonso to the Los Angeles Dodgers in exchange for ace pitcher Jacob deGrom. The Dodgers add a middle-of-the-order bat while the Mets acquire a frontline starter.",
                "headline": "Mets Trade Alonso to Dodgers for deGrom",
                "source_url": "https://www.mlb.com/trade-news/mets-trade-alonso-to-dodgers-for-degrom",
                "source": "MLB.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
            },
            {
                "id": 7,
                "trade_date": "2024-07-28",
                "season_year": 2024,
                "description": "The Los Angeles Angels traded superstar Mike Trout to the San Diego Padres in exchange for All-Star third baseman Manny Machado. The Padres add a generational talent while the Angels get a proven power hitter.",
                "headline": "Angels Trade Trout to Padres for Machado",
                "source_url": "https://www.baseballamerica.com/mlb/angels-trade-trout-to-padres-for-machado",
                "source": "Baseball America",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=32)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=32)).isoformat()
            },
            {
                "id": 8,
                "trade_date": "2024-03-08",
                "season_year": 2024,
                "description": "The Edmonton Oilers traded elite center Connor McDavid to the Toronto Maple Leafs in exchange for power forward Nathan MacKinnon. The Maple Leafs get their franchise center while the Oilers add a dominant power forward.",
                "headline": "Oilers Trade McDavid to Maple Leafs for MacKinnon",
                "source_url": "https://www.tsn.ca/nhl/oilers-trade-mcdavid-to-maple-leafs-for-mackinnon",
                "source": "TSN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=38)).isoformat()
            },
            {
                "id": 9,
                "trade_date": "2024-03-12",
                "season_year": 2024,
                "description": "The Tampa Bay Lightning traded elite goaltender Andrei Vasilevskiy to the Colorado Avalanche in exchange for offensive defenseman Victor Hedman. The Avalanche add a Vezina-caliber goalie while the Lightning get a top-pairing defenseman.",
                "headline": "Lightning Trade Vasilevskiy to Avalanche for Hedman",
                "source_url": "https://www.nhl.com/news/lightning-trade-vasilevskiy-to-avalanche-for-hedman",
                "source": "NHL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 10,
                "trade_date": "2024-02-28",
                "season_year": 2024,
                "description": "The Indiana Pacers acquired a 2025 first-round draft pick from the Cleveland Cavaliers in exchange for young center Walker Kessler. The Pacers add future assets while the Cavaliers get immediate help in the paint.",
                "headline": "Pacers Acquire 2025 First-Round Pick from Cavaliers",
                "source_url": "https://www.theathletic.com/nba/pacers-acquire-2025-first-round-pick-from-cavaliers",
                "source": "The Athletic",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
            }
        ]
        
        # Apply filters
        filtered_trades = mock_trades
        if season:
            filtered_trades = [t for t in filtered_trades if t['season_year'] == season]
        if source:
            filtered_trades = [t for t in filtered_trades if t['source'] == source]
        if applied is not None:
            filtered_trades = [t for t in filtered_trades if t['is_applied'] == applied]
        
        # Apply sorting
        if recent:
            filtered_trades = sorted(filtered_trades, key=lambda x: x['trade_date'], reverse=True)
        
        return {
            "trades": filtered_trades[:limit],
            "total": len(filtered_trades),
            "filters": {
                "season": season,
                "source": source,
                "applied": applied,
                "recent": recent,
                "limit": limit
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/statistics")
async def get_trades_statistics(days: int = Query(365, description="Days of data to analyze")):
    """Get master trades statistics"""
    try:
        # Return mock statistics data for now
        mock_stats = {
            "period_days": days,
            "total_trades": 14,
            "unique_seasons": 1,
            "unique_sources": 7,
            "applied_trades": 14,
            "pending_trades": 0,
            "earliest_trade": "2024-02-08",
            "latest_trade": "2024-07-31",
            "avg_description_length": 245.7,
            "avg_headline_length": 52.3,
            "season_stats": [
                {
                    "season_year": 2024,
                    "total_trades": 14,
                    "applied_trades": 14,
                    "unique_sources": 7
                }
            ],
            "source_stats": [
                {
                    "source": "ESPN",
                    "total_trades": 3,
                    "unique_seasons": 1,
                    "applied_trades": 3
                },
                {
                    "source": "NBA.com",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "Bleacher Report",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "NFL.com",
                    "total_trades": 2,
                    "unique_seasons": 1,
                    "applied_trades": 2
                },
                {
                    "source": "MLB.com",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "TSN",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                },
                {
                    "source": "The Athletic",
                    "total_trades": 1,
                    "unique_seasons": 1,
                    "applied_trades": 1
                }
            ],
            "month_stats": [
                {
                    "trade_month": "2024-07-01T00:00:00+00:00",
                    "total_trades": 2,
                    "unique_seasons": 1,
                    "applied_trades": 2
                },
                {
                    "trade_month": "2024-03-01T00:00:00+00:00",
                    "total_trades": 5,
                    "unique_seasons": 1,
                    "applied_trades": 5
                },
                {
                    "trade_month": "2024-02-01T00:00:00+00:00",
                    "total_trades": 7,
                    "unique_seasons": 1,
                    "applied_trades": 7
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock trades statistics data"
        }
        
        return mock_stats
        
    except Exception as e:
        return {
            "error": str(e),
            "days": days,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/season/{season}")
async def get_trades_by_season(season: int):
    """Get trades for a specific season"""
    try:
        # Return mock season-specific data for now
        mock_season_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": season,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": season,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "season": season,
            "trades": mock_season_trades,
            "total": len(mock_season_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trades for season {season}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "season": season,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/source/{source}")
async def get_trades_by_source(source: str):
    """Get trades from a specific source"""
    try:
        # Return mock source-specific data for now
        mock_source_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": source,
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": source,
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            }
        ]
        
        return {
            "source": source,
            "trades": mock_source_trades,
            "total": len(mock_source_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": f"Mock trades from {source}"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/applied")
async def get_applied_trades():
    """Get applied trades"""
    try:
        # Return mock applied trades data for now
        mock_applied_trades = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 2,
                "trade_date": "2024-02-13",
                "season_year": 2024,
                "description": "The Toronto Raptors and Denver Nuggets agreed to a trade that sends point guard Kyle Lowry to Denver in exchange for center Nikola Jokic. The deal addresses both teams needs with the Raptors getting a dominant big man and the Nuggets adding veteran leadership.",
                "headline": "Raptors Trade Lowry to Nuggets for Jokic",
                "source_url": "https://www.nba.com/news/raptors-trade-lowry-to-nuggets-for-jokic",
                "source": "NBA.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=25)).isoformat()
            }
        ]
        
        return {
            "trades": mock_applied_trades,
            "total": len(mock_applied_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock applied trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/pending")
async def get_pending_trades():
    """Get pending trades"""
    try:
        # Return mock pending trades data for now
        mock_pending_trades = [
            {
                "id": 11,
                "trade_date": "2024-08-15",
                "season_year": 2024,
                "description": "The Los Angeles Lakers and Miami Heat are discussing a potential trade that would send Anthony Davis to Miami in exchange for Bam Adebayo and future draft picks. The deal is still in negotiation stages.",
                "headline": "Lakers and Heat Discussing Davis for Adebayo Trade",
                "source_url": "https://www.espn.com/nba/story/_/id/34567890/lakers-heat-discussing-davis-for-adebayo-trade",
                "source": "ESPN",
                "is_applied": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
            },
            {
                "id": 12,
                "trade_date": "2024-08-12",
                "season_year": 2024,
                "description": "The Dallas Cowboys and San Francisco 49ers are in talks about a trade that would send Dak Prescott to San Francisco in exchange for Trey Lance and multiple draft picks. The trade is pending league approval.",
                "headline": "Cowboys and 49ers in Trade Talks for Prescott",
                "source_url": "https://www.nfl.com/news/cowboys-49ers-in-trade-talks-for-prescott",
                "source": "NFL.com",
                "is_applied": False,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat()
            }
        ]
        
        return {
            "trades": mock_pending_trades,
            "total": len(mock_pending_trades),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "note": "Mock pending trades data"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@router.get("/trades/search")
async def search_trades(query: str = Query(..., description="Search query"),
                        limit: int = Query(20, description="Number of results to return")):
    """Search trades by headline or description"""
    try:
        # Return mock search results for now
        mock_results = [
            {
                "id": 1,
                "trade_date": "2024-02-08",
                "season_year": 2024,
                "description": "The Phoenix Suns and Boston Celtics completed a blockbuster trade involving star players Kevin Durant and Devin Booker. The Suns acquired the elite scoring guard Booker in exchange for the veteran forward Durant, reshaping both teams championship aspirations.",
                "headline": "Blockbuster: Suns Trade Durant to Celtics for Booker",
                "source_url": "https://www.espn.com/nba/story/_/id/12345678/suns-trade-durant-to-celtics-booker",
                "source": "ESPN",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            },
            {
                "id": 4,
                "trade_date": "2024-03-15",
                "season_year": 2024,
                "description": "The Green Bay Packers traded future Hall of Fame quarterback Aaron Rodgers to the Las Vegas Raiders in exchange for star wide receiver Davante Adams. The Raiders get their franchise quarterback while the Packers add a proven weapon for their new QB.",
                "headline": "Packers Trade Rodgers to Raiders for Adams",
                "source_url": "https://www.nfl.com/news/packers-trade-rodgers-to-raiders-for-adams",
                "source": "NFL.com",
                "is_applied": True,
                "created_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat(),
                "updated_at": (datetime.now(timezone.utc) - timedelta(days=35)).isoformat()
            }
        ]
        
        # Apply search filter
        if query:
            query_lower = query.lower()
            mock_results = [
                r for r in mock_results 
                if query_lower in r['headline'].lower() or 
                   query_lower in r['description'].lower()
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
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
'''
    
    # Add the endpoints before the anomaly endpoints
    if "# Brain Anomaly Detection Endpoints" in content:
        content = content.replace("# Brain Anomaly Detection Endpoints", trades_code + "\n# Brain Anomaly Detection Endpoints")
    else:
        # Add at the end
        content += trades_code
    
    # Write the updated content back
    try:
        with open("c:/Users/preio/preio/perplex-edge/backend/app/api/immediate_working.py", "w") as f:
            f.write(content)
        print("Trades endpoints added successfully")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(add_trades_endpoints())
