from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Perplex Edge API",
    description="Sports Betting Analytics Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Perplex Edge API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "perplex-edge-api"}

@app.get("/api/picks/stats")
async def get_picks_stats():
    # Demo data - replace with real database queries
    return {
        "total_picks": 156,
        "wins": 89,
        "losses": 67,
        "win_rate": 57.05,
        "total_profit_loss": 2340.50,
        "roi": 15.0,
        "message": "Demo data - database not available"
    }

@app.get("/api/picks")
async def get_picks():
    # Demo picks data
    return {
        "picks": [
            {
                "id": 1,
                "sport": "basketball_nba",
                "player": "LeBron James",
                "bet_type": "points",
                "line": 25.5,
                "odds": -110,
                "expected_value": 2.5,
                "result": "win",
                "timestamp": "2026-02-11T10:00:00Z"
            },
            {
                "id": 2,
                "sport": "basketball_nba",
                "player": "Kevin Durant",
                "bet_type": "points",
                "line": 28.5,
                "odds": -105,
                "expected_value": 1.8,
                "result": "win",
                "timestamp": "2026-02-11T10:00:00Z"
            },
            {
                "id": 3,
                "sport": "basketball_nba",
                "player": "Stephen Curry",
                "bet_type": "points",
                "line": 24.5,
                "odds": -115,
                "expected_value": 3.2,
                "result": "loss",
                "timestamp": "2026-02-11T10:00:00Z"
            },
            {
                "id": 4,
                "sport": "basketball_nba",
                "player": "Giannis Antetokounmpo",
                "bet_type": "points",
                "line": 29.5,
                "odds": -110,
                "expected_value": 2.1,
                "result": "win",
                "timestamp": "2026-02-11T10:00:00Z"
            }
        ],
        "count": 4
    }

@app.get("/api/clv/stats")
async def get_clv_stats():
    # Demo CLV data
    return {
        "total_clv": 245.67,
        "avg_clv_per_pick": 1.57,
        "positive_clv_picks": 89,
        "negative_clv_picks": 67,
        "clv_win_rate": 57.05,
        "total_picks": 156,
        "message": "Demo CLV data - database not available"
    }

@app.get("/api/arbitrage/all-sports")
async def get_arbitrage_opportunities():
    # Demo arbitrage data
    return {
        "opportunities": [],
        "total_found": 0,
        "message": "No arbitrage opportunities available"
    }

@app.get("/api/odds/nba")
async def get_nba_odds():
    # Demo NBA odds data
    return {
        "games": [],
        "count": 0,
        "message": "No NBA games available today"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
