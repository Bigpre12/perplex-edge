/**
 * Bets API types and React Query hooks for personal results tracking.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL, fetchJson, buildQueryString } from './client';

// =============================================================================
// Types
// =============================================================================

export type BetStatus = 'pending' | 'won' | 'lost' | 'push' | 'void';

export interface BetCreate {
  sport_id: number;
  game_id?: number;
  player_id?: number;
  market_type: string;
  side: string;
  line_value?: number;
  sportsbook: string;
  opening_odds: number;
  stake?: number;
  notes?: string;
  model_pick_id?: number;
  placed_at?: string;
}

export interface BetSettle {
  status: BetStatus;
  actual_value?: number;
  closing_odds?: number;
  closing_line?: number;
}

export interface BetResponse {
  id: number;
  sport_id: number;
  sport_name: string | null;
  game_id: number | null;
  player_id: number | null;
  player_name: string | null;
  market_type: string;
  side: string;
  line_value: number | null;
  sportsbook: string;
  opening_odds: number;
  stake: number;
  status: BetStatus;
  actual_value: number | null;
  closing_odds: number | null;
  closing_line: number | null;
  clv_cents: number | null;
  profit_loss: number | null;
  placed_at: string;
  settled_at: string | null;
  notes: string | null;
  model_pick_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface BetList {
  items: BetResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ROIByCategory {
  category: string;
  total_bets: number;
  won: number;
  lost: number;
  pushed: number;
  win_rate: number;
  total_stake: number;
  total_profit_loss: number;
  roi: number;
}

export interface CLVStats {
  total_bets_with_clv: number;
  avg_clv_cents: number;
  positive_clv_count: number;
  positive_clv_pct: number;
  total_clv_cents: number;
}

export interface BetStatsResponse {
  total_bets: number;
  settled_bets: number;
  pending_bets: number;
  total_stake: number;
  total_profit_loss: number;
  overall_roi: number;
  overall_win_rate: number;
  won: number;
  lost: number;
  pushed: number;
  voided: number;
  clv_stats: CLVStats;
  by_market: ROIByCategory[];
  by_sportsbook: ROIByCategory[];
  by_sport: ROIByCategory[];
  top_players: ROIByCategory[];
  worst_players: ROIByCategory[];
}

export interface CLVHistoryPoint {
  date: string;
  cumulative_clv: number;
  rolling_clv_7d: number | null;
  bet_count: number;
}

export interface CLVHistoryResponse {
  data_points: CLVHistoryPoint[];
  total_clv: number;
  avg_clv: number;
}

export interface QuickBetFromPick {
  pick_id: number;
  sportsbook: string;
  stake?: number;
  actual_odds?: number;
  notes?: string;
}

export interface BetFilters {
  sport_id?: number;
  sportsbook?: string;
  market_type?: string;
  status?: BetStatus;
  player_id?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
  [key: string]: unknown;
}

// =============================================================================
// API Functions
// =============================================================================

// List bets
export async function fetchBets(filters: BetFilters = {}): Promise<BetList> {
  const qs = buildQueryString(filters);
  return fetchJson<BetList>(`${API_BASE_URL}/api/bets${qs}`);
}

// Get single bet
export async function fetchBet(betId: number): Promise<BetResponse> {
  return fetchJson<BetResponse>(`${API_BASE_URL}/api/bets/${betId}`);
}

// Create bet
export async function createBet(bet: BetCreate): Promise<BetResponse> {
  return fetchJson<BetResponse>(`${API_BASE_URL}/api/bets`, {
    method: 'POST',
    body: JSON.stringify(bet),
  });
}

// Create bet from pick
export async function createBetFromPick(data: QuickBetFromPick): Promise<BetResponse> {
  return fetchJson<BetResponse>(`${API_BASE_URL}/api/bets/from-pick`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Settle bet
export async function settleBet(betId: number, data: BetSettle): Promise<BetResponse> {
  return fetchJson<BetResponse>(`${API_BASE_URL}/api/bets/${betId}/settle`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// Delete bet
export async function deleteBet(betId: number): Promise<void> {
  await fetchJson<{ status: string }>(`${API_BASE_URL}/api/bets/${betId}`, {
    method: 'DELETE',
  });
}

// Get stats
export async function fetchBetStats(
  sportId?: number,
  daysBack?: number,
): Promise<BetStatsResponse> {
  const params: Record<string, unknown> = {};
  if (sportId) params.sport_id = sportId;
  if (daysBack) params.days_back = daysBack;
  const qs = buildQueryString(params);
  return fetchJson<BetStatsResponse>(`${API_BASE_URL}/api/bets/stats/summary${qs}`);
}

// Get CLV history
export async function fetchCLVHistory(
  sportId?: number,
  daysBack: number = 30,
): Promise<CLVHistoryResponse> {
  const params: Record<string, unknown> = { days_back: daysBack };
  if (sportId) params.sport_id = sportId;
  const qs = buildQueryString(params);
  return fetchJson<CLVHistoryResponse>(`${API_BASE_URL}/api/bets/stats/clv-history${qs}`);
}

// Get sportsbooks
export async function fetchSportsbooks(): Promise<{ sportsbooks: string[] }> {
  return fetchJson<{ sportsbooks: string[] }>(`${API_BASE_URL}/api/bets/sportsbooks`);
}

// Get market types
export async function fetchMarketTypes(): Promise<{ market_types: string[] }> {
  return fetchJson<{ market_types: string[] }>(`${API_BASE_URL}/api/bets/market-types`);
}

// =============================================================================
// React Query Hooks
// =============================================================================

/**
 * List bets with filters.
 */
export function useBets(filters: BetFilters = {}) {
  return useQuery({
    queryKey: ['bets', filters],
    queryFn: () => fetchBets(filters),
    staleTime: 30 * 1000,
  });
}

/**
 * Get single bet.
 */
export function useBet(betId: number | null) {
  return useQuery({
    queryKey: ['bet', betId],
    queryFn: () => fetchBet(betId!),
    enabled: betId !== null,
  });
}

/**
 * Get betting stats.
 */
export function useBetStats(sportId?: number, daysBack?: number) {
  return useQuery({
    queryKey: ['bet-stats', sportId, daysBack],
    queryFn: () => fetchBetStats(sportId, daysBack),
    staleTime: 60 * 1000,
  });
}

/**
 * Get CLV history for charts.
 */
export function useCLVHistory(sportId?: number, daysBack: number = 30) {
  return useQuery({
    queryKey: ['clv-history', sportId, daysBack],
    queryFn: () => fetchCLVHistory(sportId, daysBack),
    staleTime: 60 * 1000,
  });
}

/**
 * Get available sportsbooks.
 */
export function useSportsbooks() {
  return useQuery({
    queryKey: ['sportsbooks'],
    queryFn: fetchSportsbooks,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Get available market types.
 */
export function useMarketTypes() {
  return useQuery({
    queryKey: ['market-types'],
    queryFn: fetchMarketTypes,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Create bet mutation.
 */
export function useCreateBet() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createBet,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bets'] });
      queryClient.invalidateQueries({ queryKey: ['bet-stats'] });
    },
  });
}

/**
 * Create bet from pick mutation.
 */
export function useCreateBetFromPick() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createBetFromPick,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bets'] });
      queryClient.invalidateQueries({ queryKey: ['bet-stats'] });
    },
  });
}

/**
 * Settle bet mutation.
 */
export function useSettleBet() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ betId, data }: { betId: number; data: BetSettle }) => 
      settleBet(betId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bets'] });
      queryClient.invalidateQueries({ queryKey: ['bet-stats'] });
      queryClient.invalidateQueries({ queryKey: ['clv-history'] });
    },
  });
}

/**
 * Delete bet mutation.
 */
export function useDeleteBet() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deleteBet,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bets'] });
      queryClient.invalidateQueries({ queryKey: ['bet-stats'] });
    },
  });
}

// =============================================================================
// Constants
// =============================================================================

export const DEFAULT_SPORTSBOOKS = [
  'FanDuel',
  'DraftKings',
  'PrizePicks',
  'Fliff',
  'BetMGM',
  'Caesars',
  'PointsBet',
  'BetRivers',
];

export const DEFAULT_MARKET_TYPES = [
  { value: 'spread', label: 'Spread' },
  { value: 'total', label: 'Total' },
  { value: 'moneyline', label: 'Moneyline' },
  { value: 'player_points', label: 'Points' },
  { value: 'player_rebounds', label: 'Rebounds' },
  { value: 'player_assists', label: 'Assists' },
  { value: 'player_threes', label: '3-Pointers' },
  { value: 'player_pra', label: 'Pts+Reb+Ast' },
];
