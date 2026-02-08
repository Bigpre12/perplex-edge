"""API endpoints for personal bet tracking."""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.bets import(BetCreate,
 BetSettle,
 BetUpdate,
 BetFilters,
 BetResponse,
 BetList,
 BetStatsResponse,
 CLVHistoryResponse,
 QuickBetFromPick,
 BetStatusEnum,)
from app.services.bets_service import(create_bet,
 create_bet_from_pick,
 get_bet,
 list_bets,
 settle_bet,
 delete_bet,
 get_bet_stats,
 get_clv_history,)
from app.models import UserBet, Sport, Player

router = APIRouter(prefix = " / bets", tags = ["bets"])

# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 
# Bet CRUD Endpoints
# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 

@router.post("", response_model = BetResponse)
async def log_bet(bet_data: BetCreate,
 db: AsyncSession = Depends(get_db),):
 """
 Log a new bet.

 Records a bet you've placed for tracking ROI and CLV.
 """
 # Validate sport exists
 sport = await db.get(Sport, bet_data.sport_id)
 if not sport:
 raise HTTPException(status_code = 400, detail = f"Sport {bet_data.sport_id} not found")

 # Validate player exists if provided
 if bet_data.player_id:
 player = await db.get(Player, bet_data.player_id)
 if not player:
 raise HTTPException(status_code = 400, detail = f"Player {bet_data.player_id} not found")

 bet = await create_bet(db, bet_data)

 # Build response
 return BetResponse(id = bet.id,
 sport_id = bet.sport_id,
 sport_name = sport.name,
 game_id = bet.game_id,
 player_id = bet.player_id,
 player_name = None, # Would need to fetch
 market_type = bet.market_type,
 side = bet.side,
 line_value = bet.line_value,
 sportsbook = bet.sportsbook,
 opening_odds = bet.opening_odds,
 stake = bet.stake,
 status = bet.status.value,
 actual_value = bet.actual_value,
 closing_odds = bet.closing_odds,
 closing_line = bet.closing_line,
 clv_cents = bet.clv_cents,
 profit_loss = bet.profit_loss,
 placed_at = bet.placed_at,
 settled_at = bet.settled_at,
 notes = bet.notes,
 model_pick_id = bet.model_pick_id,
 created_at = bet.created_at,
 updated_at = bet.updated_at,)

@router.post(" / from - pick", response_model = BetResponse)
async def log_bet_from_pick(data: QuickBetFromPick,
 db: AsyncSession = Depends(get_db),):
 """
 Quick - log a bet from a model pick.

 Copies pick details(line, odds, player, etc.) and creates a bet record.
 Great for quickly logging when you follow a model recommendation.
 """
 try:
 bet = await create_bet_from_pick(db, data)
 except ValueError as e:
 raise HTTPException(status_code = 400, detail = str(e))

 # Get sport name
 sport = await db.get(Sport, bet.sport_id)

 return BetResponse(id = bet.id,
 sport_id = bet.sport_id,
 sport_name = sport.name if sport else None,
 game_id = bet.game_id,
 player_id = bet.player_id,
 player_name = None,
 market_type = bet.market_type,
 side = bet.side,
 line_value = bet.line_value,
 sportsbook = bet.sportsbook,
 opening_odds = bet.opening_odds,
 stake = bet.stake,
 status = bet.status.value,
 actual_value = bet.actual_value,
 closing_odds = bet.closing_odds,
 closing_line = bet.closing_line,
 clv_cents = bet.clv_cents,
 profit_loss = bet.profit_loss,
 placed_at = bet.placed_at,
 settled_at = bet.settled_at,
 notes = bet.notes,
 model_pick_id = bet.model_pick_id,
 created_at = bet.created_at,
 updated_at = bet.updated_at,)

@router.get("", response_model = BetList)
async def get_bets(sport_id: Optional[int] = Query(None, description = "Filter by sport"),
 sportsbook: Optional[str] = Query(None, description = "Filter by sportsbook"),
 market_type: Optional[str] = Query(None, description = "Filter by market type"),
 status: Optional[BetStatusEnum] = Query(None, description = "Filter by status"),
 player_id: Optional[int] = Query(None, description = "Filter by player"),
 date_from: Optional[datetime] = Query(None, description = "Filter from date"),
 date_to: Optional[datetime] = Query(None, description = "Filter to date"),
 page: int = Query(1, ge = 1, description = "Page number"),
 page_size: int = Query(50, ge = 1, le = 200, description = "Items per page"),
 db: AsyncSession = Depends(get_db),):
 """
 List all logged bets with filtering and pagination.

 Filter by sport, sportsbook, market type, status, player, or date range.
 """
 filters = BetFilters(sport_id = sport_id,
 sportsbook = sportsbook,
 market_type = market_type,
 status = status,
 player_id = player_id,
 date_from = date_from,
 date_to = date_to,
 page = page,
 page_size = page_size,)

 return await list_bets(db, filters)

# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 
# Statistics Endpoints
# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 

@router.get(" / stats / summary", response_model = BetStatsResponse)
async def get_stats_summary(sport_id: Optional[int] = Query(None, description = "Filter by sport"),
 days_back: Optional[int] = Query(None, description = "Only include last N days"),
 db: AsyncSession = Depends(get_db),):
 """
 Get comprehensive betting statistics.

 Returns:
 - Overall ROI and win rate
 - Record(won / lost / pushed / voided)
 - CLV analysis(how often you beat the close)
 - ROI breakdown by market type
 - ROI breakdown by sportsbook
 - ROI breakdown by sport
 - Top and worst performing players(min 5 bets)
 """
 return await get_bet_stats(db, sport_id = sport_id, days_back = days_back)

@router.get(" / stats / clv - history", response_model = CLVHistoryResponse)
async def get_clv_history_chart(sport_id: Optional[int] = Query(None, description = "Filter by sport"),
 days_back: int = Query(30, description = "Days of history to include"),
 db: AsyncSession = Depends(get_db),):
 """
 Get CLV history for charting.

 Returns daily cumulative CLV over time, useful for visualizing
 whether you're consistently beating closing lines.
 """
 return await get_clv_history(db, sport_id = sport_id, days_back = days_back)

# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 
# Utility Endpoints
# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 

@router.get(" / sportsbooks")
async def list_sportsbooks(db: AsyncSession = Depends(get_db)):
 """
 Get list of all sportsbooks used in logged bets.

 Useful for populating filter dropdowns.
 """
 from sqlalchemy import select, distinct

 result = await db.execute(select(distinct(UserBet.sportsbook)).order_by(UserBet.sportsbook))
 sportsbooks = [row[0] for row in result.all()]

 # Add common defaults if not present
 defaults = ["FanDuel", "DraftKings", "PrizePicks", "Fliff", "BetMGM", "Caesars"]
 for sb in defaults:
 if sb not in sportsbooks:
 sportsbooks.append(sb)

 return {"sportsbooks": sorted(sportsbooks)}

@router.get(" / market - types")
async def list_market_types(db: AsyncSession = Depends(get_db)):
 """
 Get list of all market types used in logged bets.

 Useful for populating filter dropdowns.
 """
 from sqlalchemy import select, distinct

 result = await db.execute(select(distinct(UserBet.market_type)).order_by(UserBet.market_type))
 market_types = [row[0] for row in result.all()]

 # Add common defaults
 defaults = [
 "spread", "total", "moneyline",
 "player_points", "player_rebounds", "player_assists",
 "player_threes", "player_pra", "player_pts_rebs", "player_pts_asts",
 ]
 for mt in defaults:
 if mt not in market_types:
 market_types.append(mt)

 return {"market_types": sorted(market_types)}

# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 
# Session Report Endpoint
# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 

@router.get(" / reports / session")
async def get_session_report(date_from: Optional[datetime] = Query(None, description = "Start date(YYYY - MM - DD)"),
 date_to: Optional[datetime] = Query(None, description = "End date(YYYY - MM - DD)"),
 sport_id: Optional[int] = Query(None, description = "Filter by sport"),
 days_back: Optional[int] = Query(None, description = "Alternative: last N days"),
 db: AsyncSession = Depends(get_db),):
 """
 Get comprehensive session report with ROI / CLV breakdown.

 Returns:
 - Overall ROI, win rate, P / L, CLV
 - Breakdown by market type(spreads, totals, player props)
 - Breakdown by sportsbook(FanDuel, DraftKings, etc.)
 - Breakdown by sport(NBA, NCAAB, NFL)
 - Daily P / L curve for charting

 Use date_from / date_to for custom date range, or days_back for quick lookback.

 Example:
 - GET / api / bets / reports / session?days_back = 7(last week)
 - GET / api / bets / reports / session?date_from = 2026 - 01 - 01&date_to = 2026 - 01 - 31(January)
 """
 from app.services.bets_service import get_session_report as get_report
 from datetime import datetime as dt

 # Handle days_back shortcut
 if days_back is not None and date_from is None:
 date_from = dt.now() - timedelta(days = days_back)

 return await get_report(db,
 date_from = date_from,
 date_to = date_to,
 sport_id = sport_id,)

# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 
# Individual Bet Endpoints(must be AFTER all named routes)
# =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  =  = 

@router.get(" / {bet_id}", response_model = BetResponse)
async def get_single_bet(bet_id: int,
 db: AsyncSession = Depends(get_db),):
 """Get details of a single bet."""

 bet = await get_bet(db, bet_id)
 if not bet:
 raise HTTPException(status_code = 404, detail = f"Bet {bet_id} not found")

 # Get related data
 sport = await db.get(Sport, bet.sport_id)
 player = await db.get(Player, bet.player_id) if bet.player_id else None

 return BetResponse(id = bet.id,
 sport_id = bet.sport_id,
 sport_name = sport.name if sport else None,
 game_id = bet.game_id,
 player_id = bet.player_id,
 player_name = player.name if player else None,
 market_type = bet.market_type,
 side = bet.side,
 line_value = bet.line_value,
 sportsbook = bet.sportsbook,
 opening_odds = bet.opening_odds,
 stake = bet.stake,
 status = bet.status.value,
 actual_value = bet.actual_value,
 closing_odds = bet.closing_odds,
 closing_line = bet.closing_line,
 clv_cents = bet.clv_cents,
 profit_loss = bet.profit_loss,
 placed_at = bet.placed_at,
 settled_at = bet.settled_at,
 notes = bet.notes,
 model_pick_id = bet.model_pick_id,
 created_at = bet.created_at,
 updated_at = bet.updated_at,)

@router.patch(" / {bet_id} / settle", response_model = BetResponse)
async def settle_single_bet(bet_id: int,
 settle_data: BetSettle,
 db: AsyncSession = Depends(get_db),):
 """
 Settle a bet with the result.

 Provide the final status(won, lost, push, void) and optionally:
 - actual_value: The actual stat value for props
 - closing_odds: The closing odds at game start(for CLV)
 - closing_line: The closing line at game start

 CLV and P / L are automatically calculated.
 """
 try:
 bet = await settle_bet(db, bet_id, settle_data)
 except ValueError as e:
 raise HTTPException(status_code = 400, detail = str(e))

 # Get related data
 sport = await db.get(Sport, bet.sport_id)
 player = await db.get(Player, bet.player_id) if bet.player_id else None

 return BetResponse(id = bet.id,
 sport_id = bet.sport_id,
 sport_name = sport.name if sport else None,
 game_id = bet.game_id,
 player_id = bet.player_id,
 player_name = player.name if player else None,
 market_type = bet.market_type,
 side = bet.side,
 line_value = bet.line_value,
 sportsbook = bet.sportsbook,
 opening_odds = bet.opening_odds,
 stake = bet.stake,
 status = bet.status.value,
 actual_value = bet.actual_value,
 closing_odds = bet.closing_odds,
 closing_line = bet.closing_line,
 clv_cents = bet.clv_cents,
 profit_loss = bet.profit_loss,
 placed_at = bet.placed_at,
 settled_at = bet.settled_at,
 notes = bet.notes,
 model_pick_id = bet.model_pick_id,
 created_at = bet.created_at,
 updated_at = bet.updated_at,)

@router.delete(" / {bet_id}")
async def remove_bet(bet_id: int,
 db: AsyncSession = Depends(get_db),):
 """Delete a bet record."""

 deleted = await delete_bet(db, bet_id)
 if not deleted:
 raise HTTPException(status_code = 404, detail = f"Bet {bet_id} not found")

 return {"status": "deleted", "bet_id": bet_id}

