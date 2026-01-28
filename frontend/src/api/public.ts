/**
 * Public API types and React Query hooks for the betting dashboard.
 * Matches the backend public API endpoints.
 */

import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// =============================================================================
// Types (matching backend schemas/public.py)
// =============================================================================

export interface PublicSport {
  id: number;
  name: string;
  league_code: string;
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
  game_id?: number;
  limit?: number;
  offset?: number;
}

export interface GameLineFilters {
  market_type?: string;
    [key: string]: unknown;
  min_confidence?: number;
  min_ev?: number;
  game_id?: number;
  limit?: number;
  offset?: number;
}

// =============================================================================
// API Functions
// =============================================================================

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
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
    staleTime: 60 * 1000, // 1 minute
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
