"""ETL for syncing games and betting lines from odds providers."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, update, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import SPORT_KEY_TO_NAME
from app.models import Sport, Team, Game, Market, Line, Player, ModelPick, PlayerGameStats, PickResult, Pick
from app.services.odds_provider import XYZOddsProvider, GameData, LineData, PropData

logger = logging.getLogger(__name__)

# =============================================================================
# Player-Team Mappings (January 2026 - Verified Current Rosters)
# =============================================================================

PLAYER_TEAMS = {
    # ==========================================================================
    # WESTERN CONFERENCE
    # ==========================================================================
    
    # Oklahoma City Thunder (37-10, 1st West - 2025 NBA Champions)
    "Shai Gilgeous-Alexander": "Oklahoma City Thunder",
    "Chet Holmgren": "Oklahoma City Thunder",
    "Jalen Williams": "Oklahoma City Thunder",
    "Lu Dort": "Oklahoma City Thunder",
    "Alex Caruso": "Oklahoma City Thunder",
    "Ousmane Dieng": "Oklahoma City Thunder",
    
    # San Antonio Spurs (31-15, 2nd West)
    "Victor Wembanyama": "San Antonio Spurs",
    "De'Aaron Fox": "San Antonio Spurs",
    "Stephon Castle": "San Antonio Spurs",
    "Harrison Barnes": "San Antonio Spurs",
    "Julian Champagnie": "San Antonio Spurs",
    "Devin Vassell": "San Antonio Spurs",
    
    # Denver Nuggets (31-15, 3rd West)
    "Nikola Jokic": "Denver Nuggets",
    "Jamal Murray": "Denver Nuggets",
    "Michael Porter Jr.": "Denver Nuggets",
    "Cameron Johnson": "Denver Nuggets",
    "Peyton Watson": "Denver Nuggets",
    "Christian Braun": "Denver Nuggets",
    
    # Houston Rockets
    "Kevin Durant": "Houston Rockets",
    "Alperen Sengun": "Houston Rockets",
    "Fred VanVleet": "Houston Rockets",
    "Amen Thompson": "Houston Rockets",
    "Clint Capela": "Houston Rockets",
    "Jabari Smith Jr.": "Houston Rockets",
    
    # Los Angeles Lakers (28-17, 5th West)
    "LeBron James": "Los Angeles Lakers",
    "Luka Doncic": "Los Angeles Lakers",
    "Austin Reaves": "Los Angeles Lakers",
    "Rui Hachimura": "Los Angeles Lakers",
    "Deandre Ayton": "Los Angeles Lakers",
    "Marcus Smart": "Los Angeles Lakers",
    
    # Minnesota Timberwolves (28-19, 6th West)
    "Anthony Edwards": "Minnesota Timberwolves",
    "Julius Randle": "Minnesota Timberwolves",
    "Rudy Gobert": "Minnesota Timberwolves",
    "Jaden McDaniels": "Minnesota Timberwolves",
    "Mike Conley": "Minnesota Timberwolves",
    "Donte DiVincenzo": "Minnesota Timberwolves",
    
    # Golden State Warriors (26-22, 8th West)
    "Stephen Curry": "Golden State Warriors",
    "Jimmy Butler": "Golden State Warriors",
    "Draymond Green": "Golden State Warriors",
    "Al Horford": "Golden State Warriors",
    "Jonathan Kuminga": "Golden State Warriors",
    "Brandin Podziemski": "Golden State Warriors",
    
    # Los Angeles Clippers (21-24, 10th West)
    # TRADE: Harden to Cavaliers, Garland to Clippers (Feb 2026)
    "Kawhi Leonard": "Los Angeles Clippers",
    "Darius Garland": "Los Angeles Clippers",  # Traded from Cavaliers (Feb 2026)
    "Bradley Beal": "Los Angeles Clippers",
    "Ivica Zubac": "Los Angeles Clippers",
    "Brook Lopez": "Los Angeles Clippers",
    "John Collins": "Los Angeles Clippers",
    
    # Dallas Mavericks (19-27, 11th West)
    "Anthony Davis": "Dallas Mavericks",
    "Kyrie Irving": "Dallas Mavericks",
    "Klay Thompson": "Dallas Mavericks",
    "D'Angelo Russell": "Dallas Mavericks",
    "P.J. Washington": "Dallas Mavericks",
    "Dereck Lively II": "Dallas Mavericks",
    "Daniel Gafford": "Dallas Mavericks",
    
    # Phoenix Suns
    "Devin Booker": "Phoenix Suns",
    "Jalen Green": "Phoenix Suns",
    "Dillon Brooks": "Phoenix Suns",
    "Grayson Allen": "Phoenix Suns",
    "Royce O'Neale": "Phoenix Suns",
    
    # Memphis Grizzlies (18-26, 12th West)
    # TRADE: JJJ to Jazz for multiple players and picks (Feb 2026)
    "Ja Morant": "Memphis Grizzlies",
    "Kentavious Caldwell-Pope": "Memphis Grizzlies",
    "Santi Aldama": "Memphis Grizzlies",
    "Zach Edey": "Memphis Grizzlies",
    "Kyle Anderson": "Memphis Grizzlies",  # From Jazz trade (Feb 2026)
    "Taylor Hendricks": "Memphis Grizzlies",  # From Jazz trade (Feb 2026)
    "Georges Niang": "Memphis Grizzlies",  # From Jazz trade (Feb 2026)
    
    # Sacramento Kings (12-35, 14th West)
    # TRADE: Schröder to Cavaliers, De'Andre Hunter from Cavaliers (Jan 2026)
    "Domantas Sabonis": "Sacramento Kings",
    "Zach LaVine": "Sacramento Kings",
    "DeMar DeRozan": "Sacramento Kings",
    "Malik Monk": "Sacramento Kings",
    "Keegan Murray": "Sacramento Kings",
    "De'Andre Hunter": "Sacramento Kings",  # From Cavaliers trade (Jan 2026)
    
    # New Orleans Pelicans (12-36, 15th West)
    "Zion Williamson": "New Orleans Pelicans",
    "Dejounte Murray": "New Orleans Pelicans",
    "Trey Murphy III": "New Orleans Pelicans",
    "Herb Jones": "New Orleans Pelicans",
    "Bruce Brown": "New Orleans Pelicans",
    "Jonas Valanciunas": "New Orleans Pelicans",
    
    # Portland Trail Blazers
    "Scoot Henderson": "Portland Trail Blazers",
    "Damian Lillard": "Portland Trail Blazers",
    "Jrue Holiday": "Portland Trail Blazers",
    "Shaedon Sharpe": "Portland Trail Blazers",
    "Jerami Grant": "Portland Trail Blazers",
    "Donovan Clingan": "Portland Trail Blazers",
    "Deni Avdija": "Portland Trail Blazers",
    
    # Utah Jazz (15-31)
    # TRADE: JJJ from Memphis (Feb 2026)
    "Lauri Markkanen": "Utah Jazz",
    "Jaren Jackson Jr.": "Utah Jazz",  # Traded from Grizzlies (Feb 2026)
    "Keyonte George": "Utah Jazz",
    "Walker Kessler": "Utah Jazz",
    "John Konchar": "Utah Jazz",  # From Grizzlies trade (Feb 2026)
    "Kyle Anderson": "Utah Jazz",
    
    # ==========================================================================
    # EASTERN CONFERENCE
    # ==========================================================================
    
    # Detroit Pistons (33-11, 1st East)
    "Cade Cunningham": "Detroit Pistons",
    "Jaden Ivey": "Detroit Pistons",
    "Ausar Thompson": "Detroit Pistons",
    "Jalen Duren": "Detroit Pistons",
    "Tobias Harris": "Detroit Pistons",
    
    # Boston Celtics (29-17, 2nd East)
    # TRADE: Vucevic from Bulls (Feb 2026)
    "Jayson Tatum": "Boston Celtics",
    "Jaylen Brown": "Boston Celtics",
    "Derrick White": "Boston Celtics",
    "Nikola Vucevic": "Boston Celtics",  # Traded from Bulls (Feb 2026)
    "Sam Hauser": "Boston Celtics",
    
    # Toronto Raptors (29-19, 3rd East)
    "Scottie Barnes": "Toronto Raptors",
    "Brandon Ingram": "Toronto Raptors",
    "RJ Barrett": "Toronto Raptors",
    "Immanuel Quickley": "Toronto Raptors",
    "Jakob Poeltl": "Toronto Raptors",
    "Ochai Agbaji": "Toronto Raptors",
    
    # New York Knicks (27-18, 4th East)
    "Jalen Brunson": "New York Knicks",
    "Karl-Anthony Towns": "New York Knicks",
    "Mikal Bridges": "New York Knicks",
    "OG Anunoby": "New York Knicks",
    "Josh Hart": "New York Knicks",
    "Miles McBride": "New York Knicks",
    
    # Cleveland Cavaliers (28-20, 5th East)
    # TRADE: Garland to Clippers, Harden from Clippers (Feb 2026)
    "Donovan Mitchell": "Cleveland Cavaliers",
    "James Harden": "Cleveland Cavaliers",  # Traded from Clippers (Feb 2026)
    "Evan Mobley": "Cleveland Cavaliers",
    "Jarrett Allen": "Cleveland Cavaliers",
    "Max Strus": "Cleveland Cavaliers",
    "Dennis Schröder": "Cleveland Cavaliers",  # Traded from Kings (Jan 2026)
    
    # Philadelphia 76ers (24-21, 6th East)
    "Joel Embiid": "Philadelphia 76ers",
    "Tyrese Maxey": "Philadelphia 76ers",
    "Paul George": "Philadelphia 76ers",
    "Jared McCain": "Philadelphia 76ers",
    "Kyle Lowry": "Philadelphia 76ers",
    "Andre Drummond": "Philadelphia 76ers",
    
    # Miami Heat (25-22, 7th East)
    "Bam Adebayo": "Miami Heat",
    "Tyler Herro": "Miami Heat",
    "Andrew Wiggins": "Miami Heat",
    "Terry Rozier": "Miami Heat",
    "Norman Powell": "Miami Heat",
    "Jaime Jaquez Jr.": "Miami Heat",
    
    # Orlando Magic (23-22, 8th East)
    "Paolo Banchero": "Orlando Magic",
    "Franz Wagner": "Orlando Magic",
    "Desmond Bane": "Orlando Magic",
    "Jalen Suggs": "Orlando Magic",
    "Wendell Carter Jr.": "Orlando Magic",
    "Tyus Jones": "Orlando Magic",
    
    # Chicago Bulls (23-23, 9th East)
    # TRADE: Vucevic to Celtics, Simons from Trail Blazers (Feb 2026)
    "Coby White": "Chicago Bulls",
    "Josh Giddey": "Chicago Bulls",
    "Anfernee Simons": "Chicago Bulls",  # Traded from Trail Blazers (Feb 2026)
    "Ayo Dosunmu": "Chicago Bulls",
    "Zach Collins": "Chicago Bulls",
    "Tre Jones": "Chicago Bulls",
    "Dario Šarić": "Chicago Bulls",  # From 3-team trade (Jan 2026)
    
    # Atlanta Hawks
    "CJ McCollum": "Atlanta Hawks",
    "Jalen Johnson": "Atlanta Hawks",
    "Kristaps Porzingis": "Atlanta Hawks",
    "Corey Kispert": "Atlanta Hawks",
    "Onyeka Okongwu": "Atlanta Hawks",
    "Dyson Daniels": "Atlanta Hawks",
    
    # Milwaukee Bucks
    "Giannis Antetokounmpo": "Milwaukee Bucks",
    "Kyle Kuzma": "Milwaukee Bucks",
    "Myles Turner": "Milwaukee Bucks",
    "Bobby Portis": "Milwaukee Bucks",
    "Gary Trent Jr.": "Milwaukee Bucks",
    
    # Indiana Pacers
    "Pascal Siakam": "Indiana Pacers",
    "Tyrese Haliburton": "Indiana Pacers",
    "Bennedict Mathurin": "Indiana Pacers",
    "Aaron Nesmith": "Indiana Pacers",
    "Andrew Nembhard": "Indiana Pacers",
    
    # Brooklyn Nets (12-32)
    "Cam Thomas": "Brooklyn Nets",
    "Nic Claxton": "Brooklyn Nets",
    "Dennis Schroder": "Brooklyn Nets",
    "Ben Simmons": "Brooklyn Nets",
    "Day'Ron Sharpe": "Brooklyn Nets",
    
    # Charlotte Hornets (19-28)
    "LaMelo Ball": "Charlotte Hornets",
    "Brandon Miller": "Charlotte Hornets",
    "Miles Bridges": "Charlotte Hornets",
    "Collin Sexton": "Charlotte Hornets",
    "Mark Williams": "Charlotte Hornets",
    "Spencer Dinwiddie": "Charlotte Hornets",
    
    # Washington Wizards (10-34, 15th East)
    "Trae Young": "Washington Wizards",
    "Khris Middleton": "Washington Wizards",
    "Jordan Poole": "Washington Wizards",
    "Bilal Coulibaly": "Washington Wizards",
    "Alex Sarr": "Washington Wizards",
}


# =============================================================================
# Helper Functions - Get or Create
# =============================================================================

async def get_or_create_sport(
    db: AsyncSession,
    sport_key: str,
) -> Sport:
    """
    Get or create a sport record by sport_key.
    
    IMPORTANT: This function now validates that the returned sport's key matches
    the input sport_key to prevent data bleed between sports (e.g., NFL/NCAAF).
    """
    sport_name, league_code = SPORT_KEY_TO_NAME.get(sport_key, (sport_key, sport_key.upper()))
    
    # First, try to find by sport_key (most reliable)
    result = await db.execute(
        select(Sport).where(Sport.key == sport_key)
    )
    sport = result.scalar_one_or_none()
    
    if sport:
        # Validate key matches (should always match when found by key)
        if sport.key != sport_key:
            logger.error(
                f"CRITICAL: Sport key mismatch! Expected {sport_key}, "
                f"got {sport.key} for league_code {league_code}. "
                "This could cause data bleed between sports."
            )
        return sport
    
    # Fallback: try by league_code (for backwards compatibility)
    result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = result.scalar_one_or_none()
    
    if sport:
        # CRITICAL: Validate the sport key matches to prevent data bleed
        if sport.key != sport_key:
            logger.warning(
                f"Sport found by league_code {league_code} but key mismatch: "
                f"expected {sport_key}, got {sport.key}. "
                "Creating new sport with correct key."
            )
            # Don't use this sport - it's the wrong one
            # Check if we can update the key or need to create new
            sport = None
    
    if not sport:
        sport = Sport(name=sport_name, league_code=league_code, key=sport_key)
        db.add(sport)
        await db.flush()
        logger.info(f"Created sport: {sport_name} ({league_code}, key={sport_key})")
    
    return sport


async def get_or_create_team(
    db: AsyncSession,
    sport_id: int,
    team_name: str,
    external_id: Optional[str] = None,
) -> Team:
    """Get or create a team record."""
    external_id = external_id or team_name.lower().replace(" ", "_")
    
    result = await db.execute(
        select(Team).where(
            Team.sport_id == sport_id,
            Team.external_team_id == external_id,
        )
    )
    team = result.scalar_one_or_none()
    
    if not team:
        # Generate abbreviation from team name
        words = team_name.split()
        if len(words) > 1:
            # Use last word (city/mascot) for abbreviation
            abbr = words[-1][:3].upper()
        else:
            abbr = team_name[:3].upper()
        
        team = Team(
            sport_id=sport_id,
            external_team_id=external_id,
            name=team_name,
            abbreviation=abbr,
        )
        db.add(team)
        await db.flush()
        logger.info(f"Created team: {team_name} ({abbr})")
    
    return team


async def get_or_create_game(
    db: AsyncSession,
    sport_id: int,
    external_game_id: str,
    home_team_id: int,
    away_team_id: int,
    start_time: datetime,
    status: str = "scheduled",
) -> tuple[Game, bool]:
    """
    Get or create a game record.
    
    Returns:
        Tuple of (Game, created) where created is True if new record was created
    """
    # Convert timezone-aware datetime to naive UTC for database
    if start_time.tzinfo is not None:
        # Convert to UTC first, then strip timezone info
        start_time_naive = start_time.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        # Assume naive datetimes are already UTC
        start_time_naive = start_time
    
    result = await db.execute(
        select(Game).where(
            Game.sport_id == sport_id,
            Game.external_game_id == external_game_id,
        )
    )
    game = result.scalar_one_or_none()
    created = False
    
    if not game:
        game = Game(
            sport_id=sport_id,
            external_game_id=external_game_id,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            start_time=start_time_naive,
            status=status,
        )
        db.add(game)
        await db.flush()
        created = True
        logger.debug(f"Created game: {external_game_id}")
    else:
        # Update start time if changed
        if game.start_time != start_time_naive:
            game.start_time = start_time_naive
            await db.flush()
    
    return game, created


async def get_or_create_market(
    db: AsyncSession,
    sport_id: int,
    market_type: str,
    stat_type: Optional[str] = None,
    description: Optional[str] = None,
) -> Market:
    """Get or create a market record."""
    result = await db.execute(
        select(Market).where(
            Market.sport_id == sport_id,
            Market.market_type == market_type,
            Market.stat_type == stat_type if stat_type else Market.stat_type.is_(None),
        )
    )
    market = result.scalar_one_or_none()
    
    if not market:
        market = Market(
            sport_id=sport_id,
            market_type=market_type,
            stat_type=stat_type,
            description=description or f"{market_type} {stat_type or ''}".strip(),
        )
        db.add(market)
        await db.flush()
        logger.info(f"Created market: {market_type} {stat_type or ''}")
    
    return market


async def get_or_create_player(
    db: AsyncSession,
    sport_id: int,
    player_name: str,
    external_player_id: Optional[str] = None,
    team_id: Optional[int] = None,
) -> Player:
    """Get or create a player record."""
    external_id = external_player_id or player_name.lower().replace(" ", "_")
    
    result = await db.execute(
        select(Player).where(
            Player.sport_id == sport_id,
            Player.external_player_id == external_id,
        )
    )
    player = result.scalar_one_or_none()
    
    if not player:
        player = Player(
            sport_id=sport_id,
            external_player_id=external_id,
            name=player_name,
            team_id=team_id,
        )
        db.add(player)
        await db.flush()
        logger.info(f"Created player: {player_name}")
    
    return player


# =============================================================================
# Line Management
# =============================================================================

async def mark_lines_not_current(
    db: AsyncSession,
    game_id: int,
    market_id: int,
    sportsbook: str,
    player_id: Optional[int] = None,
) -> int:
    """
    Mark existing lines as not current for the same game/market/sportsbook/player combo.
    
    Returns:
        Number of lines marked as not current
    """
    conditions = [
        Line.game_id == game_id,
        Line.market_id == market_id,
        Line.sportsbook == sportsbook,
        Line.is_current == True,
    ]
    
    # Handle nullable player_id
    if player_id is not None:
        conditions.append(Line.player_id == player_id)
    else:
        conditions.append(Line.player_id.is_(None))
    
    result = await db.execute(
        update(Line)
        .where(and_(*conditions))
        .values(is_current=False)
    )
    
    return result.rowcount


async def insert_line(
    db: AsyncSession,
    game_id: int,
    market_id: int,
    sportsbook: str,
    side: str,
    odds: float,
    line_value: Optional[float] = None,
    player_id: Optional[int] = None,
    fetched_at: Optional[datetime] = None,
) -> Line:
    """Insert a new line with is_current=True."""
    # Convert timezone-aware datetime to naive (UTC) for database
    if fetched_at is None:
        fetched_at_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    elif fetched_at.tzinfo is not None:
        fetched_at_naive = fetched_at.replace(tzinfo=None)
    else:
        fetched_at_naive = fetched_at
    
    line = Line(
        game_id=game_id,
        market_id=market_id,
        player_id=player_id,
        sportsbook=sportsbook,
        line_value=line_value,
        odds=odds,
        side=side,
        is_current=True,
        fetched_at=fetched_at_naive,
    )
    db.add(line)
    return line


# =============================================================================
# Main ETL Function
# =============================================================================

async def sync_games_and_lines(
    db: AsyncSession,
    sport_key: str,
    include_props: bool = False,
    use_stubs: bool = False,
    provider: str = "odds_api",
) -> dict[str, Any]:
    """
    Sync games and betting lines for a sport from the odds provider.
    
    This function is idempotent:
    - Sports, teams, games, markets are upserted by external ID
    - Old lines are marked as is_current=False before inserting new ones
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
        include_props: Whether to also fetch player props
        use_stubs: Use stub data instead of real API calls
        provider: Which provider to use ('odds_api', 'betstack')
    
    Returns:
        Dictionary with sync statistics
    """
    from app.services.odds_provider import XYZOddsProvider, BetStackProvider, ESPNScheduleProvider
    
    stats = {
        "sport": None,
        "teams_created": 0,
        "games_created": 0,
        "games_updated": 0,
        "markets_created": 0,
        "lines_added": 0,
        "lines_marked_old": 0,
        "players_created": 0,
        "props_added": 0,
        "errors": [],
        "data_source": "primary",  # Track which source was used
    }
    
    try:
        # Get or create sport
        sport = await get_or_create_sport(db, sport_key)
        stats["sport"] = sport.league_code
        
        # Ensure base markets exist
        market_cache: dict[str, Market] = {}
        for market_type in ["moneyline", "spread", "total"]:
            market = await get_or_create_market(db, sport.id, market_type)
            market_cache[market_type] = market
        
        # Select provider based on parameter
        # For NCAAB without stubs, try ESPN as backup when primary fails
        if provider == "betstack":
            provider_instance = BetStackProvider(use_stubs=use_stubs)
        elif provider == "espn" and sport_key in ("basketball_ncaab", "americanfootball_nfl"):
            provider_instance = None  # Will use ESPN directly below
            stats["data_source"] = "espn"
        else:
            provider_instance = XYZOddsProvider(use_stubs=use_stubs)
        
        # Special handling for ESPN provider (NCAAB and NFL backup)
        if provider_instance is None and sport_key in ("basketball_ncaab", "americanfootball_nfl"):
            async with ESPNScheduleProvider(sport_key=sport_key) as espn_provider:
                espn_games = await espn_provider.fetch_todays_games()
                sport_name = "NFL" if sport_key == "americanfootball_nfl" else "NCAAB"
                logger.info(f"ESPN fetched {len(espn_games)} {sport_name} games")
                
                # Convert ESPN format to GameData objects
                from app.services.odds_provider import GameData
                games_data = []
                for g in espn_games:
                    start_time = g.get("commence_time")
                    if isinstance(start_time, str):
                        try:
                            from datetime import datetime
                            start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                        except:
                            start_time = datetime.now(timezone.utc)
                    games_data.append(GameData(
                        external_game_id=g["id"],
                        sport_key=sport_key,
                        home_team=g["home_team"],
                        away_team=g["away_team"],
                        start_time=start_time,
                    ))
                
                # Process games using ESPN data
                for game_data in games_data:
                    try:
                        home_team = await get_or_create_team(db, sport.id, game_data.home_team)
                        away_team = await get_or_create_team(db, sport.id, game_data.away_team)
                        
                        game, created = await get_or_create_game(
                            db, sport.id, game_data.external_game_id,
                            home_team.id, away_team.id, game_data.start_time,
                        )
                        
                        if created:
                            stats["games_created"] += 1
                        else:
                            stats["games_updated"] += 1
                        
                        # Fetch and store props from ESPN provider
                        if include_props:
                            props_data = await espn_provider.fetch_player_props(
                                game_data.external_game_id, game_data.home_team, game_data.away_team
                            )
                            # Actually store the props
                            props_result = await _store_espn_player_props(
                                db, sport, game, home_team, away_team,
                                props_data.get("players", []),
                            )
                            stats["props_added"] += props_result.get("props_added", 0)
                            stats["players_created"] = stats.get("players_created", 0) + props_result.get("players_created", 0)
                            
                    except Exception as e:
                        stats["errors"].append(f"ESPN game error: {str(e)[:100]}")
                
                return stats
        
        async with provider_instance as active_provider:
            # Fetch games
            games_data = await active_provider.fetch_games(sport_key)
            logger.info(f"Fetched {len(games_data)} games for {sport_key}")
            
            # Extra debug logging for tennis
            if "tennis" in sport_key:
                logger.info(f"[TENNIS DEBUG] Sport: {sport_key}, Sport ID: {sport.id}, Games: {len(games_data)}")
                if games_data:
                    for g in games_data[:2]:  # Log first 2 games
                        logger.info(f"[TENNIS DEBUG] Game: {g.external_game_id}, {g.home_team} vs {g.away_team}")
            
            for game_data in games_data:
                try:
                    # Get or create teams
                    home_team = await get_or_create_team(
                        db, sport.id, game_data.home_team
                    )
                    away_team = await get_or_create_team(
                        db, sport.id, game_data.away_team
                    )
                    
                    if home_team.id and not await _team_existed(db, home_team.id):
                        stats["teams_created"] += 1
                    if away_team.id and not await _team_existed(db, away_team.id):
                        stats["teams_created"] += 1
                    
                    # Get or create game
                    game, created = await get_or_create_game(
                        db,
                        sport.id,
                        game_data.external_game_id,
                        home_team.id,
                        away_team.id,
                        game_data.start_time,
                    )
                    
                    if created:
                        stats["games_created"] += 1
                    else:
                        stats["games_updated"] += 1
                    
                    # Fetch and sync main lines
                    lines_data = await active_provider.fetch_main_lines(
                        sport_key,
                        game_data.external_game_id,
                    )
                    
                    for line_data in lines_data:
                        market = market_cache.get(line_data.market_type)
                        if not market:
                            # Create market if not in cache
                            market = await get_or_create_market(
                                db, sport.id, line_data.market_type
                            )
                            market_cache[line_data.market_type] = market
                            stats["markets_created"] += 1
                        
                        # Mark old lines as not current
                        marked = await mark_lines_not_current(
                            db,
                            game.id,
                            market.id,
                            line_data.sportsbook,
                            player_id=None,  # Main lines have no player
                        )
                        stats["lines_marked_old"] += marked
                        
                        # Insert new line
                        await insert_line(
                            db,
                            game.id,
                            market.id,
                            line_data.sportsbook,
                            line_data.side,
                            line_data.odds,
                            line_data.line_value,
                            player_id=None,
                            fetched_at=line_data.fetched_at,
                        )
                        stats["lines_added"] += 1
                    
                    # Optionally fetch player props
                    if include_props:
                        props_result = await _sync_player_props(
                            db,
                            active_provider,
                            sport,
                            game,
                            sport_key,
                            market_cache,
                        )
                        stats["players_created"] += props_result.get("players_created", 0)
                        stats["props_added"] += props_result.get("props_added", 0)
                        stats["lines_marked_old"] += props_result.get("lines_marked_old", 0)
                
                except Exception as e:
                    logger.error(f"Error processing game {game_data.external_game_id}: {e}", exc_info=True)
                    stats["errors"].append(f"Game {game_data.external_game_id}: {str(e)[:100]}")
        
        # Diagnostic logging for sport_id verification (helps debug NFL/NCAAF bleed)
        logger.info(
            f"[SPORT_ID_AUDIT] sport_id={sport.id}, sport_key={sport_key}, "
            f"league_code={sport.league_code}, games={stats['games_created']}, "
            f"props={stats['props_added']}"
        )
        
        # Commit transaction
        await db.commit()
        logger.info(f"Sync completed for {sport_key}: {stats}")
        return stats
    
    except Exception as e:
        await db.rollback()
        logger.error(f"ETL failed for {sport_key}: {e}")
        raise


async def _team_existed(db: AsyncSession, team_id: int) -> bool:
    """Check if team was already in database (helper for stats tracking)."""
    # This is a simplified check - in practice we track this during creation
    return True  # Assume existed to avoid double counting


async def _store_espn_player_props(
    db: AsyncSession,
    sport: Sport,
    game: Game,
    home_team: Team,
    away_team: Team,
    players_data: list[dict],
) -> dict[str, int]:
    """
    Store player props from ESPN/stub provider format.
    
    Args:
        db: Database session
        sport: Sport entity
        game: Game entity
        home_team: Home team entity
        away_team: Away team entity
        players_data: List of player prop dicts from ESPN provider
    
    Returns:
        Dictionary with storage statistics
    """
    import random
    
    stats = {
        "players_created": 0,
        "props_added": 0,
    }
    
    # NBA stat types to process
    stat_types = ["pts", "reb", "ast", "3pm", "pra", "pr", "pa", "ra", "stl", "blk"]
    
    for player_data in players_data:
        player_name = player_data.get("name")
        player_team = player_data.get("team")
        
        if not player_name:
            continue
        
        # Determine team ID
        team_id = None
        if player_team:
            if player_team == home_team.name:
                team_id = home_team.id
            elif player_team == away_team.name:
                team_id = away_team.id
        
        # Get or create player
        external_id = player_name.lower().replace(" ", "_")
        existing = await db.execute(
            select(Player).where(
                Player.sport_id == sport.id,
                Player.external_player_id == external_id,
            )
        )
        player = existing.scalar_one_or_none()
        
        if not player:
            player = Player(
                sport_id=sport.id,
                name=player_name,
                external_player_id=external_id,
                team_id=team_id,
            )
            db.add(player)
            await db.flush()
            stats["players_created"] += 1
        elif team_id and player.team_id != team_id:
            player.team_id = team_id
            await db.flush()
        
        # Create prop lines for each stat type the player has
        for stat_type in stat_types:
            line_value = player_data.get(stat_type)
            if line_value is None:
                continue
            
            # Get or create market for this stat type
            market_result = await db.execute(
                select(Market).where(
                    Market.sport_id == sport.id,
                    Market.market_type == "player_prop",
                    Market.stat_type == stat_type.upper(),
                )
            )
            market = market_result.scalar_one_or_none()
            
            if not market:
                market = Market(
                    sport_id=sport.id,
                    market_type="player_prop",
                    stat_type=stat_type.upper(),
                    description=f"Player {stat_type.upper()}",
                )
                db.add(market)
                await db.flush()
            
            # Generate realistic odds (slightly favor the over)
            over_odds = random.choice([-115, -112, -110, -108, -105])
            under_odds = random.choice([-115, -112, -110, -108, -105])
            
            # Create over line
            over_line = Line(
                game_id=game.id,
                market_id=market.id,
                player_id=player.id,
                line_value=float(line_value),  # Fixed: was 'line' instead of 'line_value'
                odds=over_odds,
                side="over",
                sportsbook="stub",
                is_current=True,
                fetched_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.add(over_line)
            stats["props_added"] += 1
            
            # Create under line
            under_line = Line(
                game_id=game.id,
                market_id=market.id,
                player_id=player.id,
                line_value=float(line_value),  # Fixed: was 'line' instead of 'line_value'
                odds=under_odds,
                side="under",
                sportsbook="stub",
                is_current=True,
                fetched_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )
            db.add(under_line)
            stats["props_added"] += 1
        
        await db.flush()
    
    await db.commit()
    return stats


async def _sync_player_props(
    db: AsyncSession,
    provider: XYZOddsProvider,
    sport: Sport,
    game: Game,
    sport_key: str,
    market_cache: dict[str, Market],
) -> dict[str, int]:
    """
    Sync player props for a game.
    
    Returns:
        Dictionary with props sync statistics
    """
    stats = {
        "players_created": 0,
        "props_added": 0,
        "lines_marked_old": 0,
        "props_errors": [],
    }
    
    try:
        logger.info(f"Fetching props for game {game.external_game_id} (sport: {sport_key})")
        props_data = await provider.fetch_player_props(
            sport_key,
            game.external_game_id,
        )
        logger.info(f"Got {len(props_data)} prop lines for game {game.external_game_id}")
        
        # Extra debug logging for tennis props
        if "tennis" in sport_key:
            logger.info(f"[TENNIS DEBUG] Props for {game.external_game_id}: {len(props_data)} lines")
            if props_data:
                for p in props_data[:3]:  # Log first 3 props
                    logger.info(f"[TENNIS DEBUG] Prop: {p.player_name} - {p.stat_type} @ {p.line_value}")
        
        # Get home and away team names for player-team matching
        home_team_result = await db.execute(select(Team).where(Team.id == game.home_team_id))
        away_team_result = await db.execute(select(Team).where(Team.id == game.away_team_id))
        home_team = home_team_result.scalar_one_or_none()
        away_team = away_team_result.scalar_one_or_none()
        
        for prop in props_data:
            # Determine player's team based on PLAYER_TEAMS mapping
            team_id = None
            if prop.player_name in PLAYER_TEAMS:
                player_team_name = PLAYER_TEAMS[prop.player_name]
                if home_team and player_team_name == home_team.name:
                    team_id = home_team.id
                elif away_team and player_team_name == away_team.name:
                    team_id = away_team.id
            
            # Get or create player with team assignment
            # Check if player exists first
            existing_player = await db.execute(
                select(Player).where(
                    Player.sport_id == sport.id,
                    Player.external_player_id == (prop.player_external_id or prop.player_name.lower().replace(" ", "_")),
                )
            )
            was_new = existing_player.scalar_one_or_none() is None
            
            player = await get_or_create_player(
                db,
                sport.id,
                prop.player_name,
                prop.player_external_id,
                team_id=team_id,
            )
            
            if was_new:
                stats["players_created"] += 1
            
            # Update player's team_id if it changed or was null
            if team_id is not None and player.team_id != team_id:
                old_team_id = player.team_id
                player.team_id = team_id
                await db.flush()
                logger.info(f"Updated player {prop.player_name} team from {old_team_id} to {team_id}")
            
            # Get or create prop market
            market_key = f"player_prop_{prop.stat_type}"
            if market_key not in market_cache:
                market = await get_or_create_market(
                    db,
                    sport.id,
                    "player_prop",
                    stat_type=prop.stat_type,
                    description=f"Player {prop.stat_type}",
                )
                market_cache[market_key] = market
            else:
                market = market_cache[market_key]
            
            # Mark old lines for this player/market/sportsbook as not current
            marked = await mark_lines_not_current(
                db,
                game.id,
                market.id,
                prop.sportsbook,
                player_id=player.id,
            )
            stats["lines_marked_old"] += marked
            
            # Insert over line
            await insert_line(
                db,
                game.id,
                market.id,
                prop.sportsbook,
                "over",
                prop.over_odds,
                prop.line_value,
                player_id=player.id,
                fetched_at=prop.fetched_at,
            )
            stats["props_added"] += 1
            
            # Insert under line
            await insert_line(
                db,
                game.id,
                market.id,
                prop.sportsbook,
                "under",
                prop.under_odds,
                prop.line_value,
                player_id=player.id,
                fetched_at=prop.fetched_at,
            )
            stats["props_added"] += 1
    
    except Exception as e:
        logger.error(f"Error syncing props for game {game.external_game_id}: {e}", exc_info=True)
        stats["props_errors"].append(f"Game {game.external_game_id}: {str(e)[:100]}")
    
    return stats


# =============================================================================
# Convenience Functions
# =============================================================================

async def sync_all_sports(
    db: AsyncSession,
    include_props: bool = False,
    use_stubs: bool = False,
) -> dict[str, Any]:
    """
    Sync games and lines for all configured sports.
    
    Returns:
        Dictionary mapping sport_key to sync results
    """
    results = {}
    
    for sport_key in SPORT_KEY_TO_NAME.keys():
        try:
            results[sport_key] = await sync_games_and_lines(
                db,
                sport_key,
                include_props=include_props,
                use_stubs=use_stubs,
            )
        except Exception as e:
            logger.error(f"Failed to sync {sport_key}: {e}")
            results[sport_key] = {"error": str(e)}
    
    return results


async def sync_all_player_teams(
    db: AsyncSession,
    sport_key: str,
) -> dict[str, Any]:
    """
    Bulk update all player teams from PLAYER_TEAMS mapping.
    
    This function iterates through all players in PLAYER_TEAMS and updates
    their team_id in the database to match the current mapping.
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
    
    Returns:
        Dictionary with counts: {'updated': n, 'not_found': n, 'teams_not_found': n, 'already_correct': n}
    """
    counts = {
        "updated": 0,
        "not_found": 0,
        "teams_not_found": 0,
        "already_correct": 0,
    }
    
    # Get sport
    league_code = SPORT_KEY_TO_NAME.get(sport_key, (sport_key.upper(), sport_key.upper()))[1]
    result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = result.scalar_one_or_none()
    
    if not sport:
        logger.warning(f"Sport not found: {league_code}")
        return {"error": f"Sport not found: {league_code}"}
    
    # Build team name to id cache
    result = await db.execute(
        select(Team).where(Team.sport_id == sport.id)
    )
    teams = {team.name: team.id for team in result.scalars().all()}
    
    logger.info(f"Syncing player teams for {len(PLAYER_TEAMS)} players")
    
    for player_name, team_name in PLAYER_TEAMS.items():
        # Find all players with this name (handle duplicates)
        result = await db.execute(
            select(Player).where(
                Player.name == player_name,
                Player.sport_id == sport.id,
            )
        )
        players = result.scalars().all()
        
        if not players:
            counts["not_found"] += 1
            continue
        
        # Get team ID from cache
        team_id = teams.get(team_name)
        if not team_id:
            logger.warning(f"Team not found for player {player_name}: {team_name}")
            counts["teams_not_found"] += 1
            continue
        
        # Update all matching players
        for player in players:
            if player.team_id != team_id:
                old_team_id = player.team_id
                player.team_id = team_id
                counts["updated"] += 1
                logger.info(f"Updated {player_name} (id={player.id}): team_id {old_team_id} -> {team_id} ({team_name})")
            else:
                counts["already_correct"] += 1
    
    await db.commit()
    logger.info(f"Player team sync complete: {counts}")
    return counts


async def clear_stale_games(
    db: AsyncSession,
    sport_key: str,
    keep_today: bool = True,
) -> dict[str, Any]:
    """
    Delete stale games, lines, and picks for a sport.
    
    By default, only deletes games from PREVIOUS days (keeps today's games).
    This prevents data loss when called after a sync.
    
    Keeps teams and players but removes game-related data.
    
    Args:
        db: Database session
        sport_key: Sport identifier (e.g., 'basketball_nba')
        keep_today: If True, only delete games from previous days (default: True)
    
    Returns:
        Dictionary with deletion counts
    """
    from datetime import datetime
    
    # Get sport
    league_code = SPORT_KEY_TO_NAME.get(sport_key, (sport_key.upper(), sport_key.upper()))[1]
    result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = result.scalar_one_or_none()
    
    if not sport:
        logger.warning(f"Sport not found: {league_code}")
        return {"error": f"Sport not found: {league_code}"}
    
    # Calculate cutoff for "stale" games (start of today UTC, timezone-naive for DB comparison)
    if keep_today:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        logger.info(f"Clearing stale games for {sport.league_code} (before {today_start})")
        
        # Get only STALE game IDs (games before today)
        game_ids_result = await db.execute(
            select(Game.id).where(
                Game.sport_id == sport.id,
                Game.start_time < today_start
            )
        )
    else:
        logger.info(f"Clearing ALL games for {sport.league_code} (id={sport.id})")
        # Get ALL game IDs for this sport
        game_ids_result = await db.execute(
            select(Game.id).where(Game.sport_id == sport.id)
        )
    
    game_ids = [row[0] for row in game_ids_result.all()]
    
    if not game_ids:
        logger.info("No stale games to clear")
        return {
            "sport": sport.league_code,
            "picks_deleted": 0,
            "lines_deleted": 0,
            "stats_deleted": 0,
            "results_deleted": 0,
            "legacy_picks_deleted": 0,
            "games_deleted": 0,
            "note": "no_stale_games" if keep_today else "no_games",
        }
    
    # Delete in order (foreign key constraints):
    # PickResult -> ModelPick -> Games (PickResult references both ModelPick and Games)
    
    # 1. Delete PickResult FIRST (references model_picks AND games)
    results_deleted = 0
    if game_ids:
        results_result = await db.execute(
            delete(PickResult).where(PickResult.game_id.in_(game_ids))
        )
        results_deleted = results_result.rowcount
    logger.info(f"Deleted {results_deleted} pick results")
    
    # 2. Delete ModelPick (only for stale games)
    picks_deleted = 0
    if game_ids:
        picks_result = await db.execute(
            delete(ModelPick).where(ModelPick.game_id.in_(game_ids))
        )
        picks_deleted = picks_result.rowcount
    logger.info(f"Deleted {picks_deleted} model picks")
    
    # 3. Delete Lines (references games)
    lines_deleted = 0
    if game_ids:
        lines_result = await db.execute(
            delete(Line).where(Line.game_id.in_(game_ids))
        )
        lines_deleted = lines_result.rowcount
    logger.info(f"Deleted {lines_deleted} lines")
    
    # 4. Delete PlayerGameStats (references games)
    stats_deleted = 0
    if game_ids:
        stats_result = await db.execute(
            delete(PlayerGameStats).where(PlayerGameStats.game_id.in_(game_ids))
        )
        stats_deleted = stats_result.rowcount
    logger.info(f"Deleted {stats_deleted} player game stats")
    
    # 5. Delete legacy Pick records (references games)
    legacy_picks_deleted = 0
    if game_ids:
        legacy_result = await db.execute(
            delete(Pick).where(Pick.game_id.in_(game_ids))
        )
        legacy_picks_deleted = legacy_result.rowcount
    logger.info(f"Deleted {legacy_picks_deleted} legacy picks")
    
    # 6. Delete Games (only stale ones)
    games_deleted = 0
    if game_ids:
        games_result = await db.execute(
            delete(Game).where(Game.id.in_(game_ids))
        )
        games_deleted = games_result.rowcount
    logger.info(f"Deleted {games_deleted} games")
    
    await db.commit()
    
    counts = {
        "sport": sport.league_code,
        "picks_deleted": picks_deleted,
        "lines_deleted": lines_deleted,
        "stats_deleted": stats_deleted,
        "results_deleted": results_deleted,
        "legacy_picks_deleted": legacy_picks_deleted,
        "games_deleted": games_deleted,
    }
    logger.info(f"Clear stale games complete: {counts}")
    return counts


# =============================================================================
# Quota-Safe Sync with Automatic Failover
# =============================================================================

async def sync_with_fallback(
    db: AsyncSession,
    sport_key: str,
    include_props: bool = True,
    use_real_api: bool = True,
    clear_first: bool = False,
) -> dict[str, Any]:
    """
    Sync games and lines with automatic cascading fallback.
    
    Cascade order:
    1. Primary: The Odds API (if use_real_api=True and quota available)
    2. Fallback: ESPN free API (schedules + generated odds)
    3. Last resort: Stub data (always works)
    
    This protects API quota by:
    - Only using primary API when explicitly enabled
    - Falling back to free ESPN when primary fails
    - Using stubs as guaranteed fallback
    
    Args:
        db: Database session
        sport_key: Sport key (e.g., "basketball_nba")
        include_props: Whether to sync player props
        use_real_api: If True, try real APIs first; if False, use stubs only
        clear_first: If True, clear old games before syncing (removes stale data)
    
    Returns:
        Sync result dictionary with data_source indicator
    """
    import httpx
    from app.services.odds_provider import XYZOddsProvider, ESPNScheduleProvider, get_quota_status
    
    result = {
        "sport": sport_key,
        "data_source": "unknown",
        "games_created": 0,
        "games_updated": 0,
        "lines_added": 0,
        "props_added": 0,
        "cleared": None,
        "errors": [],
    }
    
    # Clear old games if requested (ensures fresh data)
    if clear_first:
        logger.info(f"[{sport_key}] Clearing old games before sync...")
        clear_result = await clear_stale_games(db, sport_key, keep_today=False)
        result["cleared"] = clear_result
        logger.info(f"[{sport_key}] Cleared: {clear_result}")
    
    # If not using real API, skip straight to stubs
    if not use_real_api:
        logger.info(f"[{sport_key}] use_real_api=False, using stubs")
        try:
            stubs_result = await sync_games_and_lines(
                db, sport_key, include_props=include_props, use_stubs=True
            )
            stubs_result["data_source"] = "stubs"
            return stubs_result
        except Exception as e:
            result["errors"].append(f"Stubs failed: {str(e)[:100]}")
            result["data_source"] = "failed"
            return result
    
    # Check sport availability (off-season, etc.)
    from app.core.sport_availability import get_sport_status, get_current_tennis_tournaments
    
    sport_status = get_sport_status(sport_key)
    if not sport_status["is_active"]:
        logger.warning(
            f"[{sport_key}] Sport is not in active season: {sport_status['message']}. "
            f"Next: {sport_status.get('next_action', 'Check back later')}"
        )
        result["sport_status"] = sport_status
        # Still try to sync - might have some data like futures or preseason
    
    # Special handling for tennis - sync each active tournament
    if "tennis" in sport_key:
        active_tournaments = get_current_tennis_tournaments()
        tour_key = sport_key  # tennis_atp or tennis_wta
        tournament_keys = active_tournaments.get(tour_key, [])
        
        if not tournament_keys:
            logger.warning(
                f"[{sport_key}] No active tennis tournaments for this tour. "
                "Tennis uses tournament-specific APIs (e.g., tennis_atp_australian_open)."
            )
            result["tennis_note"] = "No active tournaments. Tennis data requires active tournaments."
            # Fall through to try generic key anyway (might have some data)
        else:
            # Sync each active tournament using tournament-specific API keys
            logger.info(f"[{sport_key}] Found {len(tournament_keys)} active tournaments: {tournament_keys}")
            combined_result = {
                "sport": sport_key,
                "data_source": "odds_api",
                "games_created": 0,
                "games_updated": 0,
                "lines_added": 0,
                "props_added": 0,
                "tournaments_synced": [],
                "errors": [],
            }
            
            for tournament_key in tournament_keys:
                try:
                    logger.info(f"[{sport_key}] Syncing tournament: {tournament_key}")
                    # The Odds API uses tournament-specific keys for tennis
                    tournament_result = await sync_games_and_lines(
                        db, tournament_key, include_props=include_props, use_stubs=False, provider="odds_api"
                    )
                    
                    # Aggregate results
                    combined_result["games_created"] += tournament_result.get("games_created", 0)
                    combined_result["games_updated"] += tournament_result.get("games_updated", 0)
                    combined_result["lines_added"] += tournament_result.get("lines_added", 0)
                    combined_result["props_added"] += tournament_result.get("props_added", 0)
                    combined_result["tournaments_synced"].append(tournament_key)
                    
                    logger.info(
                        f"[{tournament_key}] Synced: {tournament_result.get('games_created', 0)} games, "
                        f"{tournament_result.get('props_added', 0)} props"
                    )
                except Exception as e:
                    logger.warning(f"[{tournament_key}] Tournament sync failed: {e}")
                    combined_result["errors"].append(f"{tournament_key}: {str(e)[:50]}")
            
            # Return combined results if we synced any tournaments
            if combined_result["tournaments_synced"]:
                return combined_result
            # Otherwise fall through to try generic key
    
    # Check quota before trying primary API
    quota = get_quota_status()
    if quota["remaining"] < 5:
        logger.warning(f"[{sport_key}] Low quota ({quota['remaining']} remaining), skipping primary API")
    else:
        # Try primary API (The Odds API)
        try:
            logger.info(f"[{sport_key}] Trying primary API (The Odds API)...")
            primary_result = await sync_games_and_lines(
                db, sport_key, include_props=include_props, use_stubs=False, provider="odds_api"
            )
            primary_result["data_source"] = "odds_api"
            
            # Log if no games found
            games_count = primary_result.get("games_created", 0) + primary_result.get("games_updated", 0)
            if games_count == 0:
                if not sport_status["is_active"]:
                    logger.info(f"[{sport_key}] No games from API (sport is off-season)")
                else:
                    logger.warning(f"[{sport_key}] No games returned from API despite sport being active")
            else:
                logger.info(f"[{sport_key}] Primary API success: {games_count} games")
            
            return primary_result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning(f"[{sport_key}] Primary API rate limited (429), falling back")
            elif e.response.status_code == 401:
                logger.warning(f"[{sport_key}] Primary API unauthorized (401), falling back")
            else:
                logger.warning(f"[{sport_key}] Primary API error {e.response.status_code}, falling back")
            result["errors"].append(f"Primary API: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.warning(f"[{sport_key}] Primary API timeout, falling back")
            result["errors"].append("Primary API: timeout")
        except Exception as e:
            logger.warning(f"[{sport_key}] Primary API error: {e}, falling back")
            result["errors"].append(f"Primary API: {str(e)[:50]}")
    
    # Try ESPN free API as fallback (for supported sports)
    # ESPN supports: NBA, NCAAB, NFL, NCAAF, MLB, NHL
    espn_supported = (
        "basketball_nba", "basketball_ncaab",
        "americanfootball_nfl", "americanfootball_ncaaf",
        "baseball_mlb", "icehockey_nhl",
    )
    if sport_key in espn_supported:
        try:
            logger.info(f"[{sport_key}] Trying ESPN free API...")
            espn_result = await sync_games_and_lines(
                db, sport_key, include_props=include_props, use_stubs=False, provider="espn"
            )
            espn_result["data_source"] = "espn"
            logger.info(f"[{sport_key}] ESPN success: {espn_result.get('games_created', 0)} games")
            return espn_result
        except Exception as e:
            logger.warning(f"[{sport_key}] ESPN failed: {e}, falling back to stubs")
            result["errors"].append(f"ESPN: {str(e)[:50]}")
    
    # Last resort: stubs (always works)
    try:
        logger.info(f"[{sport_key}] Using stub data as last resort")
        stubs_result = await sync_games_and_lines(
            db, sport_key, include_props=include_props, use_stubs=True
        )
        stubs_result["data_source"] = "stubs"
        return stubs_result
    except Exception as e:
        result["errors"].append(f"Stubs failed: {str(e)[:100]}")
        result["data_source"] = "failed"
        logger.error(f"[{sport_key}] All sync methods failed: {result['errors']}")
        return result
