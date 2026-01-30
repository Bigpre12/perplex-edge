// Production URL is hardcoded for reliability; localhost is only for development
const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : (import.meta.env.VITE_API_BASE_URL || 'https://railway-engine-production.up.railway.app');

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined>;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, params } = options;

  let url = `${API_BASE_URL}${endpoint}`;
  
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const response = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// Types
export interface Game {
  id: number;
  sport_id: number;
  external_game_id: string;
  home_team_id: number;
  away_team_id: number;
  start_time: string;
  status: string;
  home_team: { id: number; name: string; abbreviation?: string };
  away_team: { id: number; name: string; abbreviation?: string };
}

export interface GameList {
  items: Game[];
  total: number;
}

export interface LineComparison {
  game_id: number;
  market_type: string;
  side: string;
  stat_type?: string;
  player_name?: string;
  lines: { sportsbook: string; odds: number; line_value?: number }[];
  best_odds: number;
  best_sportsbook: string;
  consensus_line?: number;
}

export interface Injury {
  id: number;
  player_name: string;
  team_name?: string;
  position?: string;
  status: string;
  status_detail?: string;
  probability?: number;
  updated_at: string;
}

export interface InjuryList {
  items: Injury[];
  total: number;
}

export interface ModelPick {
  id: number;
  sport_name: string;
  market_type: string;
  stat_type?: string;
  player_name?: string;
  home_team: string;
  away_team: string;
  game_time: string;
  side: string;
  line_value?: number;
  odds: number;
  model_probability: number;
  implied_probability: number;
  expected_value: number;
  confidence_score: number;
  hit_rate_30d?: number;
  hit_rate_10g?: number;
}

export interface PickList {
  items: ModelPick[];
  total: number;
}

export interface PickSummary {
  total_picks: number;
  active_picks: number;
  avg_ev: number;
  avg_confidence: number;
  high_confidence_picks: number;
}

export interface SyncStatus {
  status: string;
  counts: {
    sports: number;
    games: number;
    lines: { total: number; current: number };
    injuries: number;
    picks: { total: number; active: number };
  };
}

// API functions
export const api = {
  // Health
  health: () => request<{ status: string; environment: string; version: string }>('/health'),

  // Games
  getGames: (params?: { sport?: string; status?: string; limit?: number }) =>
    request<GameList>('/api/games', { params }),
  
  getTodaysGames: (sport?: string) =>
    request<GameList>('/api/games/today', { params: { sport } }),
  
  getGame: (id: number) =>
    request<Game>('/api/games/' + id),

  // Odds
  compareLines: (gameId: number, marketType?: string) =>
    request<LineComparison[]>(`/api/odds/compare/${gameId}`, { params: { market_type: marketType } }),
  
  getBestLines: (sport?: string, marketType?: string) =>
    request<LineComparison[]>('/api/odds/best', { params: { sport, market_type: marketType } }),

  // Props
  getProps: (params?: { game_id?: number; player_id?: number; stat_type?: string }) =>
    request<{ items: unknown[]; total: number }>('/api/props', { params }),
  
  comparePlayerProps: (gameId: number, playerId: number) =>
    request<LineComparison[]>(`/api/props/compare/${gameId}/${playerId}`),
  
  getPlayersWithProps: (gameId: number) =>
    request<{ id: number; name: string; position?: string }[]>(`/api/props/players/${gameId}`),

  // Injuries
  getInjuries: (params?: { sport?: string; status?: string; limit?: number }) =>
    request<InjuryList>('/api/injuries', { params }),
  
  getInjuriesByGame: (gameId: number) =>
    request<InjuryList>(`/api/injuries/by-game/${gameId}`),

  // Picks
  getPicks: (params?: { sport?: string; min_confidence?: number; min_ev?: number; limit?: number }) =>
    request<PickList>('/api/picks', { params }),
  
  getTopPicks: (sport?: string, limit?: number) =>
    request<PickList>('/api/picks/top', { params: { sport, limit } }),
  
  getPicksSummary: (sport?: string) =>
    request<PickSummary>('/api/picks/summary', { params: { sport } }),

  // Sync
  getSyncStatus: () =>
    request<SyncStatus>('/api/sync/status'),
  
  syncOdds: (sport: string) =>
    request<{ status: string; sport: string; stats: unknown }>(`/api/sync/odds/${sport}`, { method: 'POST' }),
  
  syncAllOdds: () =>
    request<{ status: string; results: unknown }>('/api/sync/odds', { method: 'POST' }),
};
