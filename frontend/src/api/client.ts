// =============================================================================
// Shared API Client — single source of truth for API_BASE_URL, fetchJson,
// fetchWithTimeout, buildQueryString, and auth token injection.
// =============================================================================

// Production URL is hardcoded for reliability; localhost is only for development
export const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : (import.meta.env.VITE_API_BASE_URL || 'https://railway-engine-production.up.railway.app');

// =============================================================================
// Auth Token Provider
// =============================================================================

let _authTokenProvider: (() => Promise<string | null>) | null = null;

/**
 * Register an auth token provider (e.g. Clerk's getToken).
 * Once set, fetchJson will attach Authorization headers automatically.
 */
export function setAuthTokenProvider(fn: () => Promise<string | null>) {
  _authTokenProvider = fn;
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  if (!_authTokenProvider) return {};
  try {
    const token = await _authTokenProvider();
    if (token) return { Authorization: `Bearer ${token}` };
  } catch {
    // Silently fail — unauthenticated request is fine
  }
  return {};
}

// =============================================================================
// Shared Utilities
// =============================================================================

export function buildQueryString(params: Record<string, unknown>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  const qs = searchParams.toString();
  return qs ? `?${qs}` : '';
}

export async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs: number = 30000
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  return fetch(url, { ...options, signal: controller.signal })
    .finally(() => clearTimeout(timeoutId));
}

export async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  if (import.meta.env.DEV) console.log('[API] Fetching:', url);

  const authHeaders = await getAuthHeaders();

  try {
    const response = await fetchWithTimeout(url, {
      cache: 'no-store',
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
        ...authHeaders,
        ...options?.headers,
      },
    }, 30000);

    if (!response.ok) {
      if (import.meta.env.DEV) console.error('[API] Error response:', response.status, response.statusText, url);
      const errorText = await response.text().catch(() => response.statusText);
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    if (import.meta.env.DEV) console.log('[API] Success:', url, { itemCount: data?.items?.length ?? data?.total ?? 'N/A' });
    return data;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      if (import.meta.env.DEV) console.error('[API] Request timed out after 30s:', url);
      throw new Error('Request timed out - server may be slow or unavailable');
    }
    if (import.meta.env.DEV) console.error('[API] Fetch failed:', url, error);
    throw error;
  }
}

// Legacy request() function used by the api object below
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

  return fetchJson<T>(url, {
    method,
    body: body ? JSON.stringify(body) : undefined,
  });
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
