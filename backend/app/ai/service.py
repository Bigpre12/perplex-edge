"""
AI recommendation service for Perplex Edge.

Orchestrates between the database (existing props/picks) and the AI client
to produce actionable recommendations. This is the main entry point for
the API endpoint.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.ai.client import AIClient, AIClientError
from app.ai.models import (
    AIContext,
    AIRequestPayload,
    AIRecommendationsResponse,
    PropLine,
    RiskProfile,
)
from app.core.config import get_settings
from app.models import ModelPick, Player, Game, Market, Team, Sport

logger = logging.getLogger(__name__)

# Stat types hidden from the UI
HIDDEN_STAT_TYPES = {"STL", "BLK"}


async def get_ai_recommendations(
    db: AsyncSession,
    sport_id: int,
    date: Optional[str] = None,
    risk_profile: str = "moderate",
    min_ev: float = 0.03,
    books: Optional[list[str]] = None,
    markets: Optional[list[str]] = None,
    max_props: int = 30,
) -> AIRecommendationsResponse:
    """
    Fetch today's top props from the DB and send them to the AI for analysis.

    Args:
        db: Database session
        sport_id: Sport to analyze
        date: ISO date string (defaults to today ET)
        risk_profile: conservative / moderate / aggressive
        min_ev: Minimum EV threshold for filtering
        books: Optional list of preferred sportsbooks
        markets: Optional list of stat types to include
        max_props: Maximum props to send to AI (controls cost/latency)

    Returns:
        AIRecommendationsResponse with individual and parlay recommendations
    """
    settings = get_settings()

    if not settings.ai_enabled and not settings.ai_api_key:
        return AIRecommendationsResponse(
            sport="",
            league="",
            date=date or "",
            warnings=["AI integration is disabled. Set AI_ENABLED=true and AI_API_KEY to enable."],
        )

    # Resolve sport
    sport = await db.get(Sport, sport_id)
    if not sport:
        return AIRecommendationsResponse(
            sport="",
            league="",
            date=date or "",
            warnings=[f"Sport {sport_id} not found"],
        )

    sport_name = sport.name or ""
    league_code = sport.league_code or ""

    # Resolve date range (Eastern time)
    from zoneinfo import ZoneInfo
    eastern = ZoneInfo("America/New_York")
    now_et = datetime.now(eastern)
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=eastern)
        except ValueError:
            target_date = now_et
    else:
        target_date = now_et
        date = target_date.strftime("%Y-%m-%d")

    day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    today_utc = day_start.astimezone(timezone.utc).replace(tzinfo=None)
    tomorrow_utc = day_end.astimezone(timezone.utc).replace(tzinfo=None)
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Aliases
    PlayerTeam = aliased(Team)
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)

    # Build query for today's top props
    # Use relaxed filters: active picks for any upcoming or recent games
    conditions = [
        ModelPick.sport_id == sport_id,
        Game.sport_id == sport_id,
        ModelPick.player_id.isnot(None),
        ModelPick.is_active == True,
        Market.stat_type.notin_(HIDDEN_STAT_TYPES),
    ]

    if markets:
        conditions.append(Market.stat_type.in_([m.upper() for m in markets]))

    query = (
        select(ModelPick, Player, PlayerTeam, Game, HomeTeam, AwayTeam, Market)
        .join(Player, ModelPick.player_id == Player.id)
        .outerjoin(PlayerTeam, Player.team_id == PlayerTeam.id)
        .join(Game, ModelPick.game_id == Game.id)
        .join(HomeTeam, Game.home_team_id == HomeTeam.id)
        .join(AwayTeam, Game.away_team_id == AwayTeam.id)
        .join(Market, ModelPick.market_id == Market.id)
        .where(and_(*conditions))
        .order_by(ModelPick.expected_value.desc())
        .limit(max_props)
    )

    result = await db.execute(query)
    rows = result.all()

    if not rows:
        return AIRecommendationsResponse(
            sport=sport_name,
            league=league_code,
            date=date,
            warnings=["No props found matching filters for AI analysis"],
        )

    # Convert DB rows to PropLine models
    props: list[PropLine] = []
    for pick, player, player_team, game, home_team, away_team, market in rows:
        team_name = player_team.name if player_team else None
        opponent = away_team.name if player_team and player_team.id == home_team.id else home_team.name

        props.append(PropLine(
            game_id=game.id,
            player_name=player.name,
            player_id=player.id,
            team=team_name,
            opponent=opponent,
            stat_type=market.stat_type or "",
            line=pick.line_value or 0,
            side=pick.side or "over",
            odds=None,  # Could be enriched from Lines table
            implied_probability=pick.implied_probability,
            model_probability=pick.model_probability,
            model_ev=pick.expected_value,
            confidence=pick.confidence_score,
            book=None,
            game_time=game.start_time.isoformat() if game.start_time else None,
        ))

    # Build AI request
    context = AIContext(
        sport=sport_name,
        league=league_code,
        date=date,
        risk_profile=RiskProfile(risk_profile),
        min_ev_threshold=min_ev,
        books=books,
    )

    payload = AIRequestPayload(props=props, context=context)

    # Call AI
    try:
        client = AIClient()
        response = await client.analyze_props(payload)
        response.generated_at = datetime.now(timezone.utc).isoformat()
        return response
    except AIClientError as e:
        logger.error("ai_service_error", error=str(e), sport=sport_name)
        return AIRecommendationsResponse(
            sport=sport_name,
            league=league_code,
            date=date,
            warnings=[f"AI analysis failed: {e.message}"],
        )
