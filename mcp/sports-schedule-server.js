#!/usr/bin/env node
/**
 * MCP Server for Sports Schedules + Live Odds
 * 
 * Provides real-time NBA and NCAAB game schedules via BALLDONTLIE API
 * and live betting odds/player props via The Odds API.
 * 
 * IMPORTANT: All odds tools fetch FRESH data on every call - no caching.
 * Previous results may be stale; always re-invoke for current lines.
 * 
 * Setup:
 * 1. Get API keys from https://balldontlie.io and https://the-odds-api.com
 * 2. Set BALLDONTLIE_API_KEY and ODDS_API_KEY in environment or mcp.json
 * 3. Register in Cursor: Settings → Tools & MCP → New MCP Server
 */

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require("@modelcontextprotocol/sdk/types.js");

// API Keys
const BALLDONTLIE_KEY = process.env.BALLDONTLIE_API_KEY;
const ODDS_API_KEY = process.env.ODDS_API_KEY;

// Base URLs
const BALLDONTLIE_URL = "https://api.balldontlie.io/v1";
const ODDS_API_URL = "https://api.the-odds-api.com/v4";

// Sport keys for The Odds API
const SPORT_KEYS = {
  nba: "basketball_nba",
  ncaab: "basketball_ncaab",
  nfl: "americanfootball_nfl",
};

// Backwards compatibility
const API_KEY = BALLDONTLIE_KEY;
const BASE_URL = BALLDONTLIE_URL;

// Helper to make authenticated requests
async function apiRequest(endpoint, params = {}) {
  const url = new URL(`${BASE_URL}${endpoint}`);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) url.searchParams.append(key, value);
  });

  const response = await fetch(url.toString(), {
    headers: {
      Authorization: API_KEY,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// Format game data into compact structure
function formatGame(game, league) {
  return {
    id: game.id,
    league: league,
    start_time: game.datetime || game.date,
    status: game.status,
    home_team: {
      id: game.home_team?.id,
      name: game.home_team?.full_name || game.home_team?.name,
      abbreviation: game.home_team?.abbreviation,
    },
    away_team: {
      id: game.away_team?.id,
      name: game.away_team?.full_name || game.away_team?.name,
      abbreviation: game.away_team?.abbreviation,
    },
    home_score: game.home_team_score,
    away_score: game.visitor_team_score || game.away_team_score,
    venue: game.venue || null,
  };
}

// Get NBA schedule for a date
async function getNbaSchedule(date) {
  const data = await apiRequest("/nba/games", {
    dates: [date],
    per_page: 100,
  });

  return {
    date: date,
    league: "NBA",
    games: (data.data || []).map((g) => formatGame(g, "NBA")),
    total: data.data?.length || 0,
  };
}

// Get NCAAB schedule for a date
async function getNcaabSchedule(date) {
  const data = await apiRequest("/cbb/games", {
    dates: [date],
    per_page: 100,
  });

  return {
    date: date,
    league: "NCAAB",
    games: (data.data || []).map((g) => formatGame(g, "NCAAB")),
    total: data.data?.length || 0,
  };
}

// Get player stats for a game (useful for prop modeling)
async function getNbaPlayerStats(gameId) {
  const data = await apiRequest("/nba/stats", {
    game_ids: [gameId],
    per_page: 100,
  });

  return {
    game_id: gameId,
    stats: (data.data || []).map((s) => ({
      player_id: s.player?.id,
      player_name: `${s.player?.first_name} ${s.player?.last_name}`,
      team: s.team?.abbreviation,
      minutes: s.min,
      points: s.pts,
      rebounds: s.reb,
      assists: s.ast,
      steals: s.stl,
      blocks: s.blk,
      turnovers: s.turnover,
      fg_pct: s.fg_pct,
      fg3_pct: s.fg3_pct,
      ft_pct: s.ft_pct,
    })),
  };
}

// Get team roster (for prop lines)
async function getNbaTeamRoster(teamId) {
  const data = await apiRequest("/nba/players", {
    team_ids: [teamId],
    per_page: 100,
  });

  return {
    team_id: teamId,
    players: (data.data || []).map((p) => ({
      id: p.id,
      name: `${p.first_name} ${p.last_name}`,
      position: p.position,
      height: p.height,
      weight: p.weight,
      jersey_number: p.jersey_number,
    })),
  };
}

// =============================================================================
// THE ODDS API - Live Odds & Player Props (Always Fresh - No Caching)
// =============================================================================

/**
 * Make authenticated request to The Odds API.
 * IMPORTANT: No caching - every call hits the API fresh.
 */
async function oddsApiRequest(endpoint, params = {}) {
  if (!ODDS_API_KEY) {
    throw new Error("ODDS_API_KEY not configured. Get your key at https://the-odds-api.com");
  }

  const url = new URL(`${ODDS_API_URL}${endpoint}`);
  url.searchParams.append("apiKey", ODDS_API_KEY);
  url.searchParams.append("dateFormat", "iso");
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (Array.isArray(value)) {
        url.searchParams.append(key, value.join(","));
      } else {
        url.searchParams.append(key, value);
      }
    }
  });

  const response = await fetch(url.toString(), {
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Odds API error ${response.status}: ${errorText.slice(0, 200)}`);
  }

  // Log remaining quota from headers
  const remaining = response.headers.get("x-requests-remaining");
  const used = response.headers.get("x-requests-used");
  if (remaining) {
    console.error(`Odds API quota: ${used} used, ${remaining} remaining`);
  }

  return response.json();
}

/**
 * Get live odds for games - ALWAYS FRESH.
 * Fetches current spreads, totals, and moneylines from The Odds API.
 */
async function getLiveOdds(sport, markets = ["h2h", "spreads", "totals"], bookmakers = null) {
  const sportKey = SPORT_KEYS[sport.toLowerCase()] || sport;
  
  const params = {
    regions: "us",
    markets: markets,
    oddsFormat: "american",
  };
  
  if (bookmakers && bookmakers.length > 0) {
    params.bookmakers = bookmakers;
  }

  const data = await oddsApiRequest(`/sports/${sportKey}/odds`, params);

  return {
    sport: sport.toUpperCase(),
    sport_key: sportKey,
    fetched_at: new Date().toISOString(),
    games: (data || []).map((game) => ({
      id: game.id,
      sport_key: game.sport_key,
      commence_time: game.commence_time,
      home_team: game.home_team,
      away_team: game.away_team,
      bookmakers: (game.bookmakers || []).map((book) => ({
        key: book.key,
        title: book.title,
        last_update: book.last_update,
        markets: (book.markets || []).map((market) => ({
          key: market.key,
          last_update: market.last_update,
          outcomes: market.outcomes,
        })),
      })),
    })),
    total_games: data?.length || 0,
  };
}

/**
 * Get player props for a specific event - ALWAYS FRESH.
 * Fetches player prop markets from The Odds API.
 */
async function getPlayerProps(sport, eventId, markets = null) {
  const sportKey = SPORT_KEYS[sport.toLowerCase()] || sport;
  
  // Default prop markets by sport
  const defaultMarkets = {
    basketball_nba: ["player_points", "player_rebounds", "player_assists", "player_threes", "player_points_rebounds_assists"],
    basketball_ncaab: ["player_points", "player_rebounds", "player_assists"],
    americanfootball_nfl: ["player_pass_yds", "player_rush_yds", "player_reception_yds", "player_receptions", "player_anytime_td"],
  };
  
  const propsMarkets = markets || defaultMarkets[sportKey] || ["player_points"];

  const params = {
    regions: "us",
    markets: propsMarkets,
    oddsFormat: "american",
  };

  const data = await oddsApiRequest(`/sports/${sportKey}/events/${eventId}/odds`, params);

  // Format player props by player name
  const playerProps = {};
  
  for (const book of data.bookmakers || []) {
    for (const market of book.markets || []) {
      for (const outcome of market.outcomes || []) {
        const playerName = outcome.description || outcome.name;
        if (!playerProps[playerName]) {
          playerProps[playerName] = {
            name: playerName,
            props: [],
          };
        }
        
        playerProps[playerName].props.push({
          market: market.key,
          side: outcome.name,
          line: outcome.point,
          odds: outcome.price,
          bookmaker: book.key,
        });
      }
    }
  }

  return {
    sport: sport.toUpperCase(),
    event_id: eventId,
    fetched_at: new Date().toISOString(),
    home_team: data.home_team,
    away_team: data.away_team,
    commence_time: data.commence_time,
    players: Object.values(playerProps),
    total_props: Object.values(playerProps).reduce((sum, p) => sum + p.props.length, 0),
  };
}

/**
 * Compare lines across bookmakers - ALWAYS FRESH.
 * Finds line differences for arbitrage/value detection.
 */
async function compareBookLines(sport, market = "spreads", minDifference = 0) {
  const sportKey = SPORT_KEYS[sport.toLowerCase()] || sport;
  
  const data = await oddsApiRequest(`/sports/${sportKey}/odds`, {
    regions: "us",
    markets: [market],
    oddsFormat: "american",
  });

  const comparisons = [];

  for (const game of data || []) {
    const linesByTeam = {};
    
    for (const book of game.bookmakers || []) {
      for (const mkt of book.markets || []) {
        if (mkt.key !== market) continue;
        
        for (const outcome of mkt.outcomes || []) {
          const team = outcome.name;
          if (!linesByTeam[team]) {
            linesByTeam[team] = [];
          }
          linesByTeam[team].push({
            bookmaker: book.key,
            line: outcome.point || null,
            odds: outcome.price,
          });
        }
      }
    }

    // Find max differences
    for (const [team, lines] of Object.entries(linesByTeam)) {
      if (lines.length < 2) continue;
      
      const points = lines.filter(l => l.line !== null).map(l => l.line);
      const odds = lines.map(l => l.odds);
      
      const pointSpread = points.length > 0 ? Math.max(...points) - Math.min(...points) : 0;
      const oddsSpread = Math.max(...odds) - Math.min(...odds);
      
      if (pointSpread >= minDifference || (minDifference === 0 && oddsSpread > 0)) {
        comparisons.push({
          game: `${game.away_team} @ ${game.home_team}`,
          commence_time: game.commence_time,
          team: team,
          market: market,
          lines: lines.sort((a, b) => (b.line || 0) - (a.line || 0)),
          point_difference: pointSpread,
          odds_difference: oddsSpread,
          best_line: lines.reduce((best, curr) => 
            (curr.line || -999) > (best.line || -999) ? curr : best
          ),
          worst_line: lines.reduce((worst, curr) => 
            (curr.line || 999) < (worst.line || 999) ? curr : worst
          ),
        });
      }
    }
  }

  return {
    sport: sport.toUpperCase(),
    market: market,
    min_difference: minDifference,
    fetched_at: new Date().toISOString(),
    comparisons: comparisons.sort((a, b) => b.point_difference - a.point_difference),
    total_opportunities: comparisons.length,
  };
}

/**
 * Get all available sports from The Odds API.
 */
async function getAvailableSports() {
  const data = await oddsApiRequest("/sports");
  
  return {
    fetched_at: new Date().toISOString(),
    sports: (data || []).filter(s => s.active).map(s => ({
      key: s.key,
      group: s.group,
      title: s.title,
      description: s.description,
      has_outrights: s.has_outrights,
    })),
  };
}

// Create MCP Server
const server = new Server(
  {
    name: "sports-schedule",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Register tool list handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_nba_schedule",
        description:
          "Get NBA game schedule for a specific date. Returns game IDs, start times, teams, scores, and status.",
        inputSchema: {
          type: "object",
          properties: {
            date: {
              type: "string",
              description: "Date in YYYY-MM-DD format (e.g., 2026-01-30)",
            },
          },
          required: ["date"],
        },
      },
      {
        name: "get_ncaab_schedule",
        description:
          "Get NCAAB (college basketball) game schedule for a specific date. Returns game IDs, start times, teams, and status.",
        inputSchema: {
          type: "object",
          properties: {
            date: {
              type: "string",
              description: "Date in YYYY-MM-DD format (e.g., 2026-01-30)",
            },
          },
          required: ["date"],
        },
      },
      {
        name: "get_nba_player_stats",
        description:
          "Get player box score stats for a specific NBA game. Useful for prop modeling.",
        inputSchema: {
          type: "object",
          properties: {
            game_id: {
              type: "number",
              description: "NBA game ID from the schedule",
            },
          },
          required: ["game_id"],
        },
      },
      {
        name: "get_nba_team_roster",
        description: "Get current roster for an NBA team. Returns player names, positions, and IDs.",
        inputSchema: {
          type: "object",
          properties: {
            team_id: {
              type: "number",
              description: "NBA team ID",
            },
          },
          required: ["team_id"],
        },
      },
      {
        name: "get_todays_slate",
        description:
          "Get combined NBA and NCAAB schedules for today. Returns all games across both leagues.",
        inputSchema: {
          type: "object",
          properties: {},
          required: [],
        },
      },
      // =================================================================
      // LIVE ODDS TOOLS - Always fetch fresh data, no caching
      // =================================================================
      {
        name: "get_live_odds",
        description:
          "Get LIVE betting odds (spreads, totals, moneylines) for games. ALWAYS fetches fresh data from The Odds API - previous results may be stale. Use this for current lines.",
        inputSchema: {
          type: "object",
          properties: {
            sport: {
              type: "string",
              enum: ["nba", "ncaab", "nfl"],
              description: "Sport to get odds for (nba, ncaab, nfl)",
            },
            markets: {
              type: "array",
              items: { type: "string" },
              description: "Markets to fetch: h2h (moneyline), spreads, totals. Default: all three.",
            },
            bookmakers: {
              type: "array",
              items: { type: "string" },
              description: "Filter by bookmakers: draftkings, fanduel, betmgm, etc. Default: all US books.",
            },
          },
          required: ["sport"],
        },
      },
      {
        name: "get_player_props",
        description:
          "Get LIVE player prop lines for a specific game. ALWAYS fetches fresh data - previous results may be stale. Returns props like points, rebounds, assists, passing yards, etc.",
        inputSchema: {
          type: "object",
          properties: {
            sport: {
              type: "string",
              enum: ["nba", "ncaab", "nfl"],
              description: "Sport (nba, ncaab, nfl)",
            },
            event_id: {
              type: "string",
              description: "Event ID from get_live_odds response",
            },
            markets: {
              type: "array",
              items: { type: "string" },
              description: "Prop markets: player_points, player_rebounds, player_assists, player_pass_yds, player_rush_yds, etc.",
            },
          },
          required: ["sport", "event_id"],
        },
      },
      {
        name: "compare_book_lines",
        description:
          "Compare betting lines across multiple sportsbooks to find differences. ALWAYS fetches fresh data. Useful for finding value or arbitrage opportunities.",
        inputSchema: {
          type: "object",
          properties: {
            sport: {
              type: "string",
              enum: ["nba", "ncaab", "nfl"],
              description: "Sport to compare",
            },
            market: {
              type: "string",
              enum: ["spreads", "totals", "h2h"],
              description: "Market type to compare. Default: spreads",
            },
            min_difference: {
              type: "number",
              description: "Minimum point difference to show (e.g., 1.5 for spreads). Default: 0 (show all)",
            },
          },
          required: ["sport"],
        },
      },
      {
        name: "get_available_sports",
        description:
          "List all sports available on The Odds API with active betting markets.",
        inputSchema: {
          type: "object",
          properties: {},
          required: [],
        },
      },
    ],
  };
});

// Register tool call handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    let result;

    switch (name) {
      case "get_nba_schedule":
        result = await getNbaSchedule(args.date);
        break;

      case "get_ncaab_schedule":
        result = await getNcaabSchedule(args.date);
        break;

      case "get_nba_player_stats":
        result = await getNbaPlayerStats(args.game_id);
        break;

      case "get_nba_team_roster":
        result = await getNbaTeamRoster(args.team_id);
        break;

      case "get_todays_slate": {
        const today = new Date().toISOString().split("T")[0];
        const [nba, ncaab] = await Promise.all([
          getNbaSchedule(today),
          getNcaabSchedule(today),
        ]);
        result = {
          date: today,
          nba: nba,
          ncaab: ncaab,
          total_games: nba.total + ncaab.total,
        };
        break;
      }

      // =================================================================
      // LIVE ODDS TOOL HANDLERS - Always fresh, no caching
      // =================================================================
      case "get_live_odds":
        result = await getLiveOdds(
          args.sport,
          args.markets || ["h2h", "spreads", "totals"],
          args.bookmakers || null
        );
        break;

      case "get_player_props":
        result = await getPlayerProps(
          args.sport,
          args.event_id,
          args.markets || null
        );
        break;

      case "compare_book_lines":
        result = await compareBookLines(
          args.sport,
          args.market || "spreads",
          args.min_difference || 0
        );
        break;

      case "get_available_sports":
        result = await getAvailableSports();
        break;

      default:
        throw new Error(`Unknown tool: ${name}`);
    }

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
    };
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Run server
async function main() {
  if (!API_KEY) {
    console.error("Error: BALLDONTLIE_API_KEY environment variable not set");
    console.error("Get your API key at https://balldontlie.io");
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Sports Schedule MCP Server running...");
}

main().catch(console.error);
