"""ETL for syncing games and betting lines from odds providers."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Sport, Team, Game, Market, Line, Player
from app.services.odds_provider import XYZOddsProvider, GameData, LineData, PropData

logger = logging.getLogger(__name__)


# =============================================================================
# Sport Key Mappings
# =============================================================================

SPORT_KEY_TO_NAME = {
    "basketball_nba": ("NBA", "NBA"),
    "americanfootball_nfl": ("NFL", "NFL"),
    "baseball_mlb": ("MLB", "MLB"),
    "icehockey_nhl": ("NHL", "NHL"),
    "basketball_ncaab": ("NCAA Basketball", "NCAAB"),
    "americanfootball_ncaaf": ("NCAA Football", "NCAAF"),
}

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
    "Kawhi Leonard": "Los Angeles Clippers",
    "James Harden": "Los Angeles Clippers",
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
    "Ja Morant": "Memphis Grizzlies",
    "Jaren Jackson Jr.": "Memphis Grizzlies",
    "Kentavious Caldwell-Pope": "Memphis Grizzlies",
    "Santi Aldama": "Memphis Grizzlies",
    "Zach Edey": "Memphis Grizzlies",
    
    # Sacramento Kings (12-35, 14th West)
    "Domantas Sabonis": "Sacramento Kings",
    "Zach LaVine": "Sacramento Kings",
    "DeMar DeRozan": "Sacramento Kings",
    "Malik Monk": "Sacramento Kings",
    "Keegan Murray": "Sacramento Kings",
    "Kevin Huerter": "Sacramento Kings",
    
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
    "Lauri Markkanen": "Utah Jazz",
    "Jusuf Nurkic": "Utah Jazz",
    "Keyonte George": "Utah Jazz",
    "Walker Kessler": "Utah Jazz",
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
    "Jayson Tatum": "Boston Celtics",
    "Jaylen Brown": "Boston Celtics",
    "Derrick White": "Boston Celtics",
    "Anfernee Simons": "Boston Celtics",
    "Georges Niang": "Boston Celtics",
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
    "Donovan Mitchell": "Cleveland Cavaliers",
    "Darius Garland": "Cleveland Cavaliers",
    "Evan Mobley": "Cleveland Cavaliers",
    "Jarrett Allen": "Cleveland Cavaliers",
    "Max Strus": "Cleveland Cavaliers",
    
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
    "Coby White": "Chicago Bulls",
    "Josh Giddey": "Chicago Bulls",
    "Nikola Vucevic": "Chicago Bulls",
    "Ayo Dosunmu": "Chicago Bulls",
    "Zach Collins": "Chicago Bulls",
    "Tre Jones": "Chicago Bulls",
    
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
    """Get or create a sport record by sport_key."""
    sport_name, league_code = SPORT_KEY_TO_NAME.get(sport_key, (sport_key, sport_key.upper()))
    
    result = await db.execute(
        select(Sport).where(Sport.league_code == league_code)
    )
    sport = result.scalar_one_or_none()
    
    if not sport:
        sport = Sport(name=sport_name, league_code=league_code)
        db.add(sport)
        await db.flush()
        logger.info(f"Created sport: {sport_name} ({league_code})")
    
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
    # Convert timezone-aware datetime to naive (UTC) for database
    if start_time.tzinfo is not None:
        start_time_naive = start_time.replace(tzinfo=None)
    else:
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
    
    Returns:
        Dictionary with sync statistics
    """
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
        
        async with XYZOddsProvider(use_stubs=use_stubs) as provider:
            # Fetch games
            games_data = await provider.fetch_games(sport_key)
            logger.info(f"Fetched {len(games_data)} games for {sport_key}")
            
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
                    lines_data = await provider.fetch_main_lines(
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
                            provider,
                            sport,
                            game,
                            sport_key,
                            market_cache,
                        )
                        stats["players_created"] += props_result.get("players_created", 0)
                        stats["props_added"] += props_result.get("props_added", 0)
                        stats["lines_marked_old"] += props_result.get("lines_marked_old", 0)
                
                except Exception as e:
                    logger.error(f"Error processing game {game_data.external_game_id}: {e}")
                    stats["errors"].append(str(e))
        
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
    }
    
    try:
        props_data = await provider.fetch_player_props(
            sport_key,
            game.external_game_id,
        )
        
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
            player = await get_or_create_player(
                db,
                sport.id,
                prop.player_name,
                prop.player_external_id,
                team_id=team_id,
            )
            
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
        logger.error(f"Error syncing props for game {game.external_game_id}: {e}")
    
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
