# Sports Schedule + Live Odds MCP Server

Real-time NBA, NCAAB, and NFL schedules via BALLDONTLIE API, plus **live betting odds and player props** via The Odds API.

**IMPORTANT:** All odds tools fetch FRESH data on every call - no caching. Previous results may be stale; always re-invoke for current lines.

## Setup

### 1. Get API Keys

1. **BALLDONTLIE** (schedules): [balldontlie.io](https://balldontlie.io) - Sign up for free
2. **The Odds API** (odds/props): [the-odds-api.com](https://the-odds-api.com) - Free tier: 500 requests/month

### 2. Install Dependencies

```bash
cd mcp
npm install
```

### 3. Configure Cursor

Edit `.cursor/mcp.json` with your API keys:

```json
{
  "mcpServers": {
    "sports-schedule": {
      "command": "node",
      "args": ["mcp/sports-schedule-server.js"],
      "env": {
        "BALLDONTLIE_API_KEY": "your-balldontlie-key",
        "ODDS_API_KEY": "your-odds-api-key"
      }
    }
  }
}
```

### 4. Restart Cursor

Cursor will auto-discover tools from the MCP server.

---

## Available Tools

### Schedule Tools (BALLDONTLIE)

| Tool | Description |
|------|-------------|
| `get_nba_schedule({ date })` | Get NBA games for a date (YYYY-MM-DD) |
| `get_ncaab_schedule({ date })` | Get NCAAB games for a date |
| `get_nba_player_stats({ game_id })` | Get player box scores for a game |
| `get_nba_team_roster({ team_id })` | Get team roster |
| `get_todays_slate()` | Get all NBA + NCAAB games today |

### Live Odds Tools (The Odds API) - Always Fresh

| Tool | Description |
|------|-------------|
| `get_live_odds({ sport, markets?, bookmakers? })` | Current spreads, totals, moneylines |
| `get_player_props({ sport, event_id, markets? })` | Player prop lines for a game |
| `compare_book_lines({ sport, market?, min_difference? })` | Cross-book line comparison |
| `get_available_sports()` | List all sports with active markets |

---

## Usage Examples

### Get Live NBA Odds

```
"Get current NBA spreads and totals from DraftKings and FanDuel"
```

Calls: `get_live_odds({ sport: "nba", markets: ["spreads", "totals"], bookmakers: ["draftkings", "fanduel"] })`

### Get Player Props

```
"Get LeBron's player props for tonight's Lakers game"
```

1. First call `get_live_odds({ sport: "nba" })` to get event_id
2. Then call `get_player_props({ sport: "nba", event_id: "abc123" })`

### Find Line Differences

```
"Show me NBA spreads where books differ by at least 1.5 points"
```

Calls: `compare_book_lines({ sport: "nba", market: "spreads", min_difference: 1.5 })`

### Combined Query

```
"Pull today's full NBA and NCAAB slate with live spreads from all books, then show any games where the spread differs by more than 1 point across books"
```

---

## Response Formats

### get_live_odds Response

```json
{
  "sport": "NBA",
  "fetched_at": "2026-01-30T12:00:00Z",
  "games": [
    {
      "id": "abc123",
      "commence_time": "2026-01-30T00:00:00Z",
      "home_team": "Los Angeles Lakers",
      "away_team": "Boston Celtics",
      "bookmakers": [
        {
          "key": "draftkings",
          "markets": [
            {
              "key": "spreads",
              "outcomes": [
                { "name": "Los Angeles Lakers", "price": -110, "point": -3.5 },
                { "name": "Boston Celtics", "price": -110, "point": 3.5 }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### get_player_props Response

```json
{
  "sport": "NBA",
  "event_id": "abc123",
  "fetched_at": "2026-01-30T12:00:00Z",
  "home_team": "Los Angeles Lakers",
  "away_team": "Boston Celtics",
  "players": [
    {
      "name": "LeBron James",
      "props": [
        { "market": "player_points", "side": "Over", "line": 25.5, "odds": -110, "bookmaker": "draftkings" },
        { "market": "player_points", "side": "Under", "line": 25.5, "odds": -110, "bookmaker": "draftkings" }
      ]
    }
  ]
}
```

### compare_book_lines Response

```json
{
  "sport": "NBA",
  "market": "spreads",
  "fetched_at": "2026-01-30T12:00:00Z",
  "comparisons": [
    {
      "game": "Boston Celtics @ Los Angeles Lakers",
      "team": "Los Angeles Lakers",
      "point_difference": 1.5,
      "best_line": { "bookmaker": "draftkings", "line": -3.0, "odds": -110 },
      "worst_line": { "bookmaker": "fanduel", "line": -4.5, "odds": -110 }
    }
  ]
}
```

---

## API Quotas

### The Odds API (Free Tier)
- 500 requests/month
- Each `get_live_odds` call = 1 request
- Each `get_player_props` call = 1 request
- Quota shown in server logs after each call

### BALLDONTLIE
- Free tier available
- Rate limits apply

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "ODDS_API_KEY not configured" | Add key to `.cursor/mcp.json` |
| "BALLDONTLIE_API_KEY not set" | Add key to `.cursor/mcp.json` |
| Tools not appearing | Restart Cursor after editing mcp.json |
| "Odds API error 401" | Invalid API key |
| "Odds API error 429" | Rate limit exceeded, wait or upgrade plan |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Cursor Agent                          │
└─────────────────────┬───────────────────────────────────┘
                      │ MCP Protocol
┌─────────────────────▼───────────────────────────────────┐
│               MCP Server (Node.js)                       │
│  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │ Schedule Tools  │  │ Live Odds Tools (no cache)  │   │
│  └────────┬────────┘  └──────────────┬──────────────┘   │
└───────────┼──────────────────────────┼──────────────────┘
            │                          │
    ┌───────▼───────┐          ┌───────▼───────┐
    │  BALLDONTLIE  │          │ The Odds API  │
    │   (schedules) │          │ (odds/props)  │
    └───────────────┘          └───────────────┘
```

Every odds tool call hits the API fresh - no caching between calls.
