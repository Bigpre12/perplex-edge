/**
 * Public API types and React Query hooks for the betting dashboard.
 * Matches the backend public API endpoints.
 */

import { useQuery } from '@tanstack/react-query';

// Production URL is hardcoded for reliability; localhost is only for development
const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:8000' 
  : (import.meta.env.VITE_API_BASE_URL || 'https://railway-engine-production.up.railway.app');

// Log API URL on load for debugging
console.log('[API] Configuration:', {
  DEV: import.meta.env.DEV,
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
  API_BASE_URL,
});

// =============================================================================
// Types (matching backend schemas/public.py)
// =============================================================================

export interface PublicSport {
  id: number;
  name: string;
  league_code: string;
  key: string;
}

export interface PublicSportList {
  items: PublicSport[];
  total: number;
}

export interface PublicGame {
  id: number;
  external_game_id: string;
  home_team: string;
  home_team_abbr: string | null;
  away_team: string;
  away_team_abbr: string | null;
  start_time: string;
  status: string;
}

export interface PublicGameList {
  items: PublicGame[];
  total: number;
}

export interface PublicMarket {
  id: number;
  market_type: string;
  stat_type: string | null;
  description: string | null;
}

export interface PublicMarketList {
  items: PublicMarket[];
  total: number;
}

// Per-sportsbook line data for comparison
export interface BookLine {
  sportsbook: string;
  line: number | null;
  odds: number;
  ev: number | null;
}

export interface PlayerPropPick {
  pick_id: number;
  player_name: string;
  player_id: number;
  team: string;
  team_abbr: string | null;
  opponent_team: string;
  opponent_abbr: string | null;
  stat_type: string;
  line: number;
  side: string;
  odds: number;
  sportsbook: string | null;
  model_probability: number;
  implied_probability: number;
  expected_value: number;
  hit_rate_30d: number | null;
  hit_rate_10g: number | null;
  hit_rate_5g: number | null;
  hit_rate_3g: number | null;
  confidence_score: number;
  game_id: number;
  game_start_time: string;
  // Per-book comparison
  book_lines: BookLine[] | null;
  best_book: string | null;
  line_variance: number | null;
  // Kelly sizing (bet size recommendation)
  kelly_units: number | null;  // Suggested bet size (0-5 units)
  kelly_edge_pct: number | null;  // Edge percentage
  kelly_risk_level: string | null;  // "NO_BET", "SMALL", "STANDARD", "CONFIDENT", "STRONG", "MAX"
}

export interface PlayerPropPickList {
  items: PlayerPropPick[];
  total: number;
  filters: Record<string, unknown>;
}

export interface GameLinePick {
  pick_id: number;
  game_id: number;
  home_team: string;
  home_team_abbr: string | null;
  away_team: string;
  away_team_abbr: string | null;
  game_start_time: string;
  market_type: string;
  line: number | null;
  side: string;
  odds: number;
  sportsbook: string | null;
  model_probability: number;
  implied_probability: number;
  expected_value: number;
  confidence_score: number;
}

export interface GameLinePickList {
  items: GameLinePick[];
  total: number;
  filters: Record<string, unknown>;
}

// =============================================================================
// Filter Types
// =============================================================================

export interface PlayerPropFilters {
  stat_type?: string;
  [key: string]: unknown;
  min_confidence?: number;
  min_ev?: number;
  risk_levels?: string;  // Comma-separated: "STANDARD,CONFIDENT,STRONG,MAX"
  game_id?: number;
  fresh_only?: boolean;  // Only show picks for games that haven't started
  limit?: number;
  offset?: number;
}

export interface GameLineFilters {
  market_type?: string;
  [key: string]: unknown;
  min_confidence?: number;
  min_ev?: number;
  game_id?: number;
  fresh_only?: boolean;  // Only show picks for games that haven't started
  limit?: number;
  offset?: number;
}

// =============================================================================
// API Functions
// =============================================================================

// Timeout helper - abort fetch after X ms
function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs: number = 30000): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  
  return fetch(url, {
    ...options,
    signal: controller.signal,
  }).finally(() => clearTimeout(timeoutId));
}

async function fetchJson<T>(url: string): Promise<T> {
  console.log('[API] Fetching:', url);
  
  try {
    const response = await fetchWithTimeout(url, {
      // Prevent browser caching to ensure fresh data
      cache: 'no-store',
      headers: {
        'Cache-Control': 'no-cache',
      },
    }, 30000); // 30 second timeout
    
    if (!response.ok) {
      console.error('[API] Error response:', response.status, response.statusText, url);
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('[API] Success:', url, { itemCount: data?.items?.length ?? data?.total ?? 'N/A' });
    return data;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.error('[API] Request timed out after 30s:', url);
      throw new Error('Request timed out - server may be slow or unavailable');
    }
    console.error('[API] Fetch failed:', url, error);
    throw error;
  }
}

function buildQueryString(params: Record<string, unknown>): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, String(value));
    }
  });
  const qs = searchParams.toString();
  return qs ? `?${qs}` : '';
}

// Sports
export async function fetchSports(): Promise<PublicSportList> {
  return fetchJson<PublicSportList>(`${API_BASE_URL}/api/sports`);
}

// Games
export async function fetchTodaysGames(sportId: number): Promise<PublicGameList> {
  return fetchJson<PublicGameList>(`${API_BASE_URL}/api/sports/${sportId}/games/today`);
}

// Markets
export async function fetchMarkets(sportId: number, marketType?: string): Promise<PublicMarketList> {
  const qs = marketType ? `?market_type=${marketType}` : '';
  return fetchJson<PublicMarketList>(`${API_BASE_URL}/api/sports/${sportId}/markets${qs}`);
}

// Player Props
export async function fetchPlayerPropPicks(
  sportId: number,
  filters: PlayerPropFilters = {}
): Promise<PlayerPropPickList> {
  const qs = buildQueryString(filters);
  return fetchJson<PlayerPropPickList>(`${API_BASE_URL}/api/sports/${sportId}/picks/player-props${qs}`);
}

// Game Lines
export async function fetchGameLinePicks(
  sportId: number,
  filters: GameLineFilters = {}
): Promise<GameLinePickList> {
  const qs = buildQueryString(filters);
  return fetchJson<GameLinePickList>(`${API_BASE_URL}/api/sports/${sportId}/picks/game-lines${qs}`);
}

// =============================================================================
// React Query Hooks
// =============================================================================

/**
 * Fetch all available sports.
 */
export function useSports() {
  return useQuery({
    queryKey: ['sports'],
    queryFn: fetchSports,
    staleTime: 5 * 60 * 1000, // 5 minutes - sports don't change often
  });
}

/**
 * Fetch today's games for a sport.
 */
export function useTodaysGames(sportId: number | null) {
  return useQuery({
    queryKey: ['games-today', sportId],
    queryFn: () => fetchTodaysGames(sportId!),
    enabled: sportId !== null,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  });
}

/**
 * Fetch markets for a sport.
 */
export function useMarkets(sportId: number | null, marketType?: string) {
  return useQuery({
    queryKey: ['markets', sportId, marketType],
    queryFn: () => fetchMarkets(sportId!, marketType),
    enabled: sportId !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch player prop picks with filters.
 * Query key includes all filters to ensure fresh fetch on any filter change.
 */
export function usePlayerPropPicks(sportId: number | null, filters: PlayerPropFilters = {}) {
  return useQuery({
    queryKey: ['player-props', sportId, filters],
    queryFn: () => fetchPlayerPropPicks(sportId!, filters),
    enabled: sportId !== null,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  });
}

/**
 * Fetch game line picks with filters.
 * Query key includes all filters to ensure fresh fetch on any filter change.
 */
export function useGameLinePicks(sportId: number | null, filters: GameLineFilters = {}) {
  return useQuery({
    queryKey: ['game-lines', sportId, filters],
    queryFn: () => fetchGameLinePicks(sportId!, filters),
    enabled: sportId !== null,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  });
}

// =============================================================================
// Stat Type Options (common player prop stat types)
// =============================================================================

export const STAT_TYPE_OPTIONS = [
  { value: '', label: 'All Stats' },
  { value: 'PTS', label: 'Points' },
  { value: 'REB', label: 'Rebounds' },
  { value: 'AST', label: 'Assists' },
  { value: '3PM', label: '3-Pointers Made' },
  { value: 'PRA', label: 'Pts + Reb + Ast' },
  { value: 'PR', label: 'Pts + Reb' },
  { value: 'PA', label: 'Pts + Ast' },
  { value: 'RA', label: 'Reb + Ast' },
  { value: 'STL', label: 'Steals' },
  { value: 'BLK', label: 'Blocks' },
  { value: 'TO', label: 'Turnovers' },
];

export const MARKET_TYPE_OPTIONS = [
  { value: '', label: 'All Markets' },
  { value: 'spread', label: 'Spread' },
  { value: 'total', label: 'Total (O/U)' },
  { value: 'moneyline', label: 'Moneyline' },
];

// =============================================================================
// Stats Types
// =============================================================================

export interface StatsResponse {
  total_picks: number;
  hit_rate: number;
  avg_ev: number;
  players_tracked: number;
  error?: string;
}

export interface HitRateRecord {
  id: number;
  player_name: string;
  stat_type: string;
  total_picks: number;
  hits: number;
  misses: number;
  hit_rate_percentage: number;
  avg_ev: number;
}

export interface HitRateList {
  items: HitRateRecord[];
  total: number;
  error?: string;
}

export interface PlayerStatsResponse {
  player_name: string;
  overall_stats: {
    total_picks: number;
    total_hits: number;
    overall_hit_rate: number;
    avg_ev: number;
  };
  by_stat_type: Array<{
    stat_type: string;
    total_picks: number;
    hits: number;
    hit_rate: number;
    avg_ev: number;
  }>;
  recent_performance: Array<{
    id: number;
    player_name: string;
    team: string;
    opponent: string;
    date: string;
    stat_type: string;
    actual_value: number;
    line: number;
    result: string;
  }>;
  recent_picks: Array<{
    id: number;
    pick_type: string;
    stat_type: string;
    line: number;
    odds: number;
    ev_percentage: number;
    confidence: number;
  }>;
}

export interface RefreshResponse {
  status: string;
  sport: string;
  result: Record<string, unknown>;
}

export interface SchedulerStatus {
  enabled: boolean;
  tasks_running: number;
  tasks: Array<{
    name: string;
    done: boolean;
    cancelled: boolean;
  }>;
}

// =============================================================================
// Hit Rate Tracking Types
// =============================================================================

export interface HotPlayer {
  player_id: number;
  player_name: string;
  hit_rate_7d: number;
  total_7d: number;
  hits_7d: number;
  current_streak: number;
  last_5: string | null;
}

export interface HotPlayerList {
  items: HotPlayer[];
  total: number;
}

export interface StreakPlayer {
  player_id: number;
  player_name: string;
  streak: number;
  hit_rate_7d: number | null;
  last_5: string | null;
}

export interface StreaksList {
  hot: StreakPlayer[];
  cold: StreakPlayer[];
}

export interface RecentResult {
  result_id: number;
  player_id: number;
  player_name: string;
  stat_type: string | null;
  line: number;
  side: string;
  actual_value: number;
  hit: boolean;
  settled_at: string;
  game_id: number;
}

export interface RecentResultList {
  items: RecentResult[];
  total: number;
}

export interface PlayerHistory {
  player_id: number;
  player_name: string;
  stats: {
    hit_rate_7d: number | null;
    total_7d: number;
    hit_rate_all: number | null;
    total_all: number;
    current_streak: number;
    best_streak: number;
    worst_streak: number;
    last_5: string | null;
  };
  results: Array<{
    stat_type: string | null;
    line: number;
    side: string;
    actual_value: number;
    hit: boolean;
    settled_at: string;
  }>;
}

// =============================================================================
// Stats API Functions
// =============================================================================

export async function fetchStats(): Promise<StatsResponse> {
  return fetchJson<StatsResponse>(`${API_BASE_URL}/api/stats`);
}

export async function fetchHitRates(): Promise<HitRateList> {
  return fetchJson<HitRateList>(`${API_BASE_URL}/api/stats/hit-rates`);
}

export async function fetchPlayerStats(playerName: string): Promise<PlayerStatsResponse> {
  return fetchJson<PlayerStatsResponse>(`${API_BASE_URL}/api/stats/player/${encodeURIComponent(playerName)}`);
}

export async function refreshPicks(sport: string = 'nba'): Promise<RefreshResponse> {
  const response = await fetch(`${API_BASE_URL}/api/picks/refresh?sport=${sport}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchSchedulerStatus(): Promise<SchedulerStatus> {
  return fetchJson<SchedulerStatus>(`${API_BASE_URL}/api/scheduler/status`);
}

// Hit Rate Tracking API Functions
export async function fetchHotPlayers(sportId: number, minPicks: number = 5, limit: number = 10): Promise<HotPlayerList> {
  return fetchJson<HotPlayerList>(`${API_BASE_URL}/api/stats/sports/${sportId}/hot-players?min_picks=${minPicks}&limit=${limit}`);
}

export async function fetchColdPlayers(sportId: number, minPicks: number = 5, limit: number = 10): Promise<HotPlayerList> {
  return fetchJson<HotPlayerList>(`${API_BASE_URL}/api/stats/sports/${sportId}/cold-players?min_picks=${minPicks}&limit=${limit}`);
}

export async function fetchStreaks(sportId: number, minStreak: number = 3, limit: number = 20): Promise<StreaksList> {
  return fetchJson<StreaksList>(`${API_BASE_URL}/api/stats/sports/${sportId}/streaks?min_streak=${minStreak}&limit=${limit}`);
}

export async function fetchRecentResults(sportId: number, limit: number = 20): Promise<RecentResultList> {
  return fetchJson<RecentResultList>(`${API_BASE_URL}/api/stats/sports/${sportId}/recent-results?limit=${limit}`);
}

export async function fetchPlayerHistory(playerId: number, limit: number = 50): Promise<PlayerHistory> {
  return fetchJson<PlayerHistory>(`${API_BASE_URL}/api/stats/players/${playerId}/history?limit=${limit}`);
}

export async function settleGame(gameId: number, simulate: boolean = false): Promise<{ game_id: number; settled: number; hits: number; misses: number; hit_rate: number }> {
  const response = await fetch(`${API_BASE_URL}/api/stats/games/${gameId}/settle?simulate=${simulate}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

// =============================================================================
// Stats React Query Hooks
// =============================================================================

/**
 * Fetch overall stats summary.
 */
export function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  });
}

/**
 * Fetch hit rates for all tracked players.
 */
export function useHitRates() {
  return useQuery({
    queryKey: ['hit-rates'],
    queryFn: fetchHitRates,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
  });
}

/**
 * Fetch detailed stats for a specific player.
 */
export function usePlayerStats(playerName: string | null) {
  return useQuery({
    queryKey: ['player-stats', playerName],
    queryFn: () => fetchPlayerStats(playerName!),
    enabled: playerName !== null && playerName !== '',
    staleTime: 60 * 1000, // 1 minute
  });
}

/**
 * Fetch scheduler status.
 */
export function useSchedulerStatus() {
  return useQuery({
    queryKey: ['scheduler-status'],
    queryFn: fetchSchedulerStatus,
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
  });
}

/**
 * Fetch hot players by 7-day hit rate.
 */
export function useHotPlayers(sportId: number | null, minPicks: number = 5, limit: number = 10) {
  return useQuery({
    queryKey: ['hot-players', sportId, minPicks, limit],
    queryFn: () => fetchHotPlayers(sportId!, minPicks, limit),
    enabled: sportId !== null,
    staleTime: 60 * 1000,
    refetchInterval: 2 * 60 * 1000,
  });
}

/**
 * Fetch cold players by 7-day hit rate.
 */
export function useColdPlayers(sportId: number | null, minPicks: number = 5, limit: number = 10) {
  return useQuery({
    queryKey: ['cold-players', sportId, minPicks, limit],
    queryFn: () => fetchColdPlayers(sportId!, minPicks, limit),
    enabled: sportId !== null,
    staleTime: 60 * 1000,
    refetchInterval: 2 * 60 * 1000,
  });
}

/**
 * Fetch players on streaks.
 */
export function useStreaks(sportId: number | null, minStreak: number = 3) {
  return useQuery({
    queryKey: ['streaks', sportId, minStreak],
    queryFn: () => fetchStreaks(sportId!, minStreak),
    enabled: sportId !== null,
    staleTime: 60 * 1000,
    refetchInterval: 2 * 60 * 1000,
  });
}

/**
 * Fetch recent pick results.
 */
export function useRecentResults(sportId: number | null, limit: number = 20) {
  return useQuery({
    queryKey: ['recent-results', sportId, limit],
    queryFn: () => fetchRecentResults(sportId!, limit),
    enabled: sportId !== null,
    staleTime: 30 * 1000,
    refetchInterval: 60 * 1000,
  });
}

/**
 * Fetch detailed history for a player.
 */
export function usePlayerHistory(playerId: number | null) {
  return useQuery({
    queryKey: ['player-history', playerId],
    queryFn: () => fetchPlayerHistory(playerId!),
    enabled: playerId !== null,
    staleTime: 60 * 1000,
  });
}

// =============================================================================
// 100% Hit Rate Props Types
// =============================================================================

export interface HundredPercentProp {
  pick_id: number;
  player_name: string;
  player_id: number;
  team: string;
  team_abbr: string | null;
  opponent_team: string;
  opponent_abbr: string | null;
  stat_type: string;
  line: number;
  side: string;
  odds: number;
  sportsbook: string | null;
  hit_rate_season: number | null;
  games_season: number;
  hit_rate_last_10: number | null;
  games_last_10: number;
  hit_rate_last_5: number | null;
  games_last_5: number;
  is_100_season: boolean;
  is_100_last_10: boolean;
  is_100_last_5: boolean;
  model_probability: number;
  expected_value: number;
  confidence_score: number;
  game_id: number;
  game_start_time: string | null;  // Nullable if not available
}

export interface HundredPercentPropList {
  items: HundredPercentProp[];
  total: number;
  window: string;
}

// =============================================================================
// Parlay Builder Types
// =============================================================================

export interface ParlayLeg {
  pick_id: number;
  player_name: string;
  player_id: number | null;  // For correlation detection
  team_abbr: string | null;
  game_id: number | null;  // For correlation detection
  stat_type: string;
  line: number;
  side: string;
  odds: number;
  grade: string;  // "A", "B", "C", "D", "F"
  win_prob: number;
  edge: number;
  hit_rate_5g: number | null;
  is_100_last_5: boolean;
}

export interface CorrelationWarning {
  type: string;  // "same_game", "same_player", "stat_ladder", "opposing_sides"
  severity: string;  // "high", "medium", "low"
  legs: number[];  // Indices of correlated legs (1-indexed)
  message: string;
}

export interface KellySizing {
  full_kelly_pct: number;
  kelly_fraction: number;
  suggested_units: number;
  edge_pct: number;
  risk_level: string;  // "NO_BET", "SMALL", "STANDARD", "CONFIDENT", "STRONG", "MAX"
}

export interface ParlayRecommendation {
  legs: ParlayLeg[];
  leg_count: number;
  total_odds: number;  // American odds
  decimal_odds: number;
  parlay_probability: number;
  parlay_ev: number;
  overall_grade: string;
  label: string;  // "LOCK", "PLAY", "SKIP"
  min_leg_prob: number;
  avg_edge: number;
  // Correlation warnings
  correlations: CorrelationWarning[];
  correlation_risk: number;  // 0-1 risk score
  correlation_risk_label: string;  // "LOW", "MEDIUM", "HIGH", "CRITICAL"
  // Kelly sizing
  kelly: KellySizing | null;
}

export interface ParlayBuilderResponse {
  parlays: ParlayRecommendation[];
  total_candidates: number;
  leg_count: number;
  filters_applied: Record<string, unknown>;
}

export interface ParlayBuilderFilters {
  leg_count?: number;
  include_100_pct?: boolean;
  min_leg_grade?: string;
  max_results?: number;
  block_correlated?: boolean;  // Block high-correlation parlays
  max_correlation_risk?: string;  // "LOW", "MEDIUM", "HIGH", "CRITICAL"
  [key: string]: unknown;  // Index signature for buildQueryString compatibility
}

// =============================================================================
// Alt-Line Explorer Types
// =============================================================================

export interface AltLine {
  line: number;
  over_odds: number | null;
  under_odds: number | null;
  over_prob: number | null;
  under_prob: number | null;
  over_ev: number | null;
  under_ev: number | null;
  over_fair_odds: number | null;
  under_fair_odds: number | null;
  is_main_line: boolean;
}

export interface AltLineExplorerResponse {
  player_name: string;
  player_id: number;
  team_abbr: string | null;
  stat_type: string;
  game_id: number;
  opponent_abbr: string | null;
  game_start_time: string;
  model_projection: number;
  projection_std: number | null;
  alt_lines: AltLine[];
  best_over_line: AltLine | null;
  best_under_line: AltLine | null;
  hit_rate_5g: number | null;
  season_avg: number | null;
}

// =============================================================================
// Alt-Line Explorer API Functions
// =============================================================================

export async function fetchAltLines(pickId: number): Promise<AltLineExplorerResponse> {
  return fetchJson<AltLineExplorerResponse>(`${API_BASE_URL}/api/picks/${pickId}/alt-lines`);
}

export function useAltLines(pickId: number | null) {
  return useQuery({
    queryKey: ['alt-lines', pickId],
    queryFn: () => fetchAltLines(pickId!),
    enabled: pickId !== null,
    staleTime: 60 * 1000, // 1 minute
  });
}

// =============================================================================
// 100% Hit Rate API Functions
// =============================================================================

export async function fetch100PercentProps(
  sportId: number,
  window: string = 'last_5',
  limit: number = 50
): Promise<HundredPercentPropList> {
  return fetchJson<HundredPercentPropList>(
    `${API_BASE_URL}/api/sports/${sportId}/picks/100pct-hits?window=${window}&limit=${limit}`
  );
}

export function use100PercentProps(
  sportId: number | null,
  window: string = 'last_5',
  limit: number = 50
) {
  return useQuery({
    queryKey: ['100pct-props', sportId, window, limit],
    queryFn: async () => {
      const result = await fetch100PercentProps(sportId!, window, limit);
      // Ensure we always return a valid structure
      return {
        items: result?.items ?? [],
        total: result?.total ?? 0,
        window: result?.window ?? window,
      };
    },
    enabled: sportId !== null,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 2 * 60 * 1000, // Auto-refresh every 2 minutes
    retry: 2, // Retry twice on failure
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000), // Exponential backoff
  });
}

// =============================================================================
// Parlay Builder API Functions
// =============================================================================

export async function fetchParlayBuilder(
  sportId: number,
  filters: ParlayBuilderFilters = {}
): Promise<ParlayBuilderResponse> {
  const qs = buildQueryString(filters);
  return fetchJson<ParlayBuilderResponse>(
    `${API_BASE_URL}/api/sports/${sportId}/parlays/builder${qs}`
  );
}

export function useParlayBuilder(
  sportId: number | null,
  filters: ParlayBuilderFilters = {}
) {
  return useQuery({
    queryKey: ['parlay-builder', sportId, filters],
    queryFn: async () => {
      const result = await fetchParlayBuilder(sportId!, filters);
      // Ensure we always return a valid structure
      return {
        parlays: result?.parlays ?? [],
        total_candidates: result?.total_candidates ?? 0,
        leg_count: result?.leg_count ?? filters.leg_count ?? 3,
        filters_applied: result?.filters_applied ?? {},
      };
    },
    enabled: sportId !== null,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 2 * 60 * 1000, // Auto-refresh every 2 minutes
    retry: 2, // Retry twice on failure
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 10000), // Exponential backoff
  });
}

// =============================================================================
// Data Freshness / Metadata Types and Hooks
// =============================================================================

export interface SportMetadata {
  name: string;
  last_updated: string | null;
  relative: string;
  games_count?: number;
  lines_count?: number;
  props_count?: number;
  source?: string;
  is_healthy: boolean;
}

export interface DataFreshnessResponse {
  updated_at: string;
  sports: Record<string, SportMetadata>;
}

/**
 * Fetch data freshness metadata for all sports.
 * Shows "Last updated: X" for each sport.
 */
export async function fetchDataFreshness(): Promise<DataFreshnessResponse> {
  return fetchJson<DataFreshnessResponse>(`${API_BASE_URL}/api/meta`);
}

/**
 * Hook to fetch data freshness with auto-refresh.
 * Updates every 30 seconds to show accurate "X minutes ago" text.
 */
export function useDataFreshness() {
  return useQuery({
    queryKey: ['data-freshness'],
    queryFn: fetchDataFreshness,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
  });
}
