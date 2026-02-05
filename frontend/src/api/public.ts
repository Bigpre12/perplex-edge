/**
 * Public API types and React Query hooks for the betting dashboard.
 * Matches the backend public API endpoints.
 */

import { useQuery } from '@tanstack/react-query';
import { API_BASE_URL, fetchJson, buildQueryString } from './client';

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
  sport_id: number;  // Actual sport_id from the database
  sport_key: string;  // Sport key (e.g., "americanfootball_nfl") for reliable label mapping
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
  // Line movement tracking
  opening_line: number | null;  // Original line when first posted
  opening_odds: number | null;  // Original odds
  line_movement: number | null;  // current_line - opening_line (positive = moved up)
  odds_movement: number | null;  // current_odds - opening_odds (negative = sharpened)
  movement_direction: 'sharp_up' | 'sharp_down' | 'steam' | 'reverse' | 'stable' | null;
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
  player_id?: number;    // Filter to specific player (for deep linking from Stats)
  side?: string;         // Filter by side: "over" or "under"
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
// API Functions (using shared client utilities)
// =============================================================================

// Sports
export async function fetchSports(): Promise<PublicSportList> {
  return fetchJson<PublicSportList>(`${API_BASE_URL}/api/sports`);
}

// Sport Availability
export interface SportStatus {
  is_active: boolean;
  status: string;
  message: string;
  next_action: string | null;
}

export interface SportAvailability {
  sport_id: number;
  sport_key: string;
  status: SportStatus;
  data_counts: {
    games_today: number;
    total_picks: number;
  };
  data_reason: string | null;
  tennis_note: string | null;
}

export interface AllSportsAvailability {
  checked_at: string;
  sports: Record<string, SportStatus>;
  tennis_tournaments: Record<string, string[]>;
  notes: Record<string, string>;
}

export async function fetchSportAvailability(sportId: number): Promise<SportAvailability> {
  return fetchJson<SportAvailability>(`${API_BASE_URL}/api/sports/${sportId}/availability`);
}

export async function fetchAllSportsAvailability(): Promise<AllSportsAvailability> {
  return fetchJson<AllSportsAvailability>(`${API_BASE_URL}/api/sports/availability`);
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
 * Fetch availability status for a specific sport.
 * Shows whether sport is in-season, off-season, etc.
 */
export function useSportAvailability(sportId: number | null) {
  return useQuery({
    queryKey: ['sport-availability', sportId],
    queryFn: () => fetchSportAvailability(sportId!),
    enabled: sportId !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch availability status for all sports.
 */
export function useAllSportsAvailability() {
  return useQuery({
    queryKey: ['sports-availability'],
    queryFn: fetchAllSportsAvailability,
    staleTime: 5 * 60 * 1000, // 5 minutes
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
// Stat Type Options - Sport-Specific
// =============================================================================

// Import from shared config (keep in sync with backend/app/config/sports.py)
import { getStatTypeOptionsForSport, type StatType } from '../config/sports';

/**
 * Get stat type options for a specific sport.
 * Returns sport-specific stat types as { value, label } objects for dropdowns.
 * Defaults to NBA stats if sport not found.
 */
export function getStatTypesForSport(sportId: number): { value: string; label: string }[] {
  const options = getStatTypeOptionsForSport(sportId);
  if (options.length === 0) {
    // Default to NBA
    return getStatTypeOptionsForSport(30);
  }
  return options;
}

// Legacy export: STAT_TYPES_BY_SPORT as Record<number, { value: string; label: string }[]>
// Built dynamically from the config for backward compatibility
export const STAT_TYPES_BY_SPORT: Record<number, { value: string; label: string }[]> = {
  30: getStatTypeOptionsForSport(30),
  31: getStatTypeOptionsForSport(31),
  32: getStatTypeOptionsForSport(32),
  34: getStatTypeOptionsForSport(34),
  40: getStatTypeOptionsForSport(40),
  41: getStatTypeOptionsForSport(41),
  42: getStatTypeOptionsForSport(42),
  43: getStatTypeOptionsForSport(43),
  44: getStatTypeOptionsForSport(53), // Legacy NHL ID
  53: getStatTypeOptionsForSport(53),
  60: getStatTypeOptionsForSport(60),
  70: getStatTypeOptionsForSport(70),
  71: getStatTypeOptionsForSport(71),
  72: getStatTypeOptionsForSport(72),
  80: getStatTypeOptionsForSport(80),
};

// Legacy export for backward compatibility (defaults to NBA)
export const STAT_TYPE_OPTIONS = [
  { value: '', label: 'All Stats' },
  ...getStatTypeOptionsForSport(30),
];

// Re-export types for convenience
export type { StatType };

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
  // Market-specific fields (populated when include_market=true)
  stat_type?: string;  // e.g., "PTS", "REB", "3PM"
  side?: string;       // "over" or "under"
  // Trust tag for quality assessment
  trust_tag?: string;  // "strong", "ok", "thin", "weak"
}

export interface HotPlayerList {
  items: HotPlayer[];
  total: number;
}

export interface StreakPlayer {
  player_id: number;
  player_name: string;
  streak: number;
  stat_type: string | null;
  direction: string | null;
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
export async function fetchHotPlayers(
  sportId: number,
  minPicks: number = 5,
  limit: number = 10,
  includeMarket: boolean = true,
  market?: string,
  side?: string
): Promise<HotPlayerList> {
  const params = new URLSearchParams({
    min_picks: minPicks.toString(),
    limit: limit.toString(),
    include_market: includeMarket.toString(),
  });
  if (market) params.set('market', market);
  if (side) params.set('side', side);
  return fetchJson<HotPlayerList>(`${API_BASE_URL}/api/stats/sports/${sportId}/hot-players?${params}`);
}

export async function fetchColdPlayers(
  sportId: number,
  minPicks: number = 5,
  limit: number = 10,
  market?: string,
  side?: string
): Promise<HotPlayerList> {
  const params = new URLSearchParams({
    min_picks: minPicks.toString(),
    limit: limit.toString(),
  });
  if (market) params.set('market', market);
  if (side) params.set('side', side);
  return fetchJson<HotPlayerList>(`${API_BASE_URL}/api/stats/sports/${sportId}/cold-players?${params}`);
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
 * When includeMarket=true (default), includes stat_type and side for each player's best market.
 */
export function useHotPlayers(
  sportId: number | null,
  minPicks: number = 5,
  limit: number = 10,
  includeMarket: boolean = true,
  market?: string,
  side?: string
) {
  return useQuery({
    queryKey: ['hot-players', sportId, minPicks, limit, includeMarket, market, side],
    queryFn: () => fetchHotPlayers(sportId!, minPicks, limit, includeMarket, market, side),
    enabled: sportId !== null,
    staleTime: 60 * 1000,
    refetchInterval: 2 * 60 * 1000,
  });
}

/**
 * Fetch cold players by 7-day hit rate.
 */
export function useColdPlayers(
  sportId: number | null,
  minPicks: number = 5,
  limit: number = 10,
  market?: string,
  side?: string
) {
  return useQuery({
    queryKey: ['cold-players', sportId, minPicks, limit, market, side],
    queryFn: () => fetchColdPlayers(sportId!, minPicks, limit, market, side),
    enabled: sportId !== null,
    staleTime: 60 * 1000,
    refetchInterval: 2 * 60 * 1000,
  });
}

/**
 * Fetch players on streaks.
 */
export function useStreaks(sportId: number | null, minStreak: number = 3, limit: number = 20) {
  return useQuery({
    queryKey: ['streaks', sportId, minStreak, limit],
    queryFn: () => fetchStreaks(sportId!, minStreak, limit),
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

export interface PlatformViolation {
  type: string;  // "player_limit_exceeded" or "game_limit_exceeded"
  severity: string;  // "HIGH" or "CRITICAL"
  message: string;
  player_id?: number | null;
  game_id?: number | null;
  count: number;
  max_allowed: number;
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
  // Platform validation
  valid_platforms?: string[];  // Platforms where this parlay is valid
  platform_violations?: PlatformViolation[];  // Rule violations
  is_universally_valid?: boolean;  // True if valid on all platforms
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
// Auto-Generate Slips Types
// =============================================================================

export interface AutoGenerateSlipsResponse {
  slips: ParlayRecommendation[];
  slip_count: number;
  leg_count: number;
  platform: string;
  total_candidates: number;
  filters: Record<string, unknown>;
  avg_slip_ev: number;
  avg_slip_probability: number;
  total_suggested_units: number;
  slate_quality: string;  // "STRONG", "GOOD", "THIN", "PASS"
}

export interface AutoGenerateFilters {
  platform?: string;
  leg_count?: number;
  slip_count?: number;
  min_leg_ev?: number;
  min_confidence?: number;
  allow_correlation?: boolean;
}

// =============================================================================
// Auto-Generate Slips API Functions
// =============================================================================

export async function fetchAutoGenerateSlips(
  sportId: number,
  filters: AutoGenerateFilters = {}
): Promise<AutoGenerateSlipsResponse> {
  const params = new URLSearchParams();
  if (filters.platform) params.set('platform', filters.platform);
  if (filters.leg_count) params.set('leg_count', filters.leg_count.toString());
  if (filters.slip_count) params.set('slip_count', filters.slip_count.toString());
  if (filters.min_leg_ev !== undefined) params.set('min_leg_ev', filters.min_leg_ev.toString());
  if (filters.min_confidence !== undefined) params.set('min_confidence', filters.min_confidence.toString());
  if (filters.allow_correlation !== undefined) params.set('allow_correlation', filters.allow_correlation.toString());
  
  const queryString = params.toString();
  const url = `${API_BASE_URL}/api/sports/${sportId}/parlays/auto-generate${queryString ? `?${queryString}` : ''}`;
  return fetchJson<AutoGenerateSlipsResponse>(url);
}

export function useAutoGenerateSlips(
  sportId: number | null,
  filters: AutoGenerateFilters = {},
  enabled: boolean = false  // Only fetch when user clicks the button
) {
  return useQuery({
    queryKey: ['auto-generate-slips', sportId, filters],
    queryFn: () => fetchAutoGenerateSlips(sportId!, filters),
    enabled: enabled && sportId !== null,
    staleTime: 30 * 1000, // 30 seconds
  });
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

// =============================================================================
// Analytics Dashboard Types
// =============================================================================

export interface MarketPerformance {
  market_type: string;
  total_bets: number;
  won: number;
  lost: number;
  win_rate: number;
  total_stake: number;
  total_profit_loss: number;
  roi: number;
  avg_clv_cents: number;
  beat_close_pct: number;
  sample_quality: 'high' | 'medium' | 'low';
}

export interface MarketPerformanceResponse {
  markets: MarketPerformance[];
  summary: {
    total_bets: number;
    total_profit_loss: number;
    overall_roi: number;
    best_market: string | null;
    worst_market: string | null;
  };
  filters: {
    days: number;
    sport_id: number | null;
  };
}

export interface BetStatsResponse {
  total_bets: number;
  pending_bets: number;
  total_stake: number;
  total_profit_loss: number;
  overall_roi: number;
  overall_win_rate: number;
  won: number;
  lost: number;
  pushed: number;
  voided: number;
  clv_stats: {
    total_bets_with_clv: number;
    avg_clv_cents: number;
    positive_clv_count: number;
    positive_clv_pct: number;
    total_clv_cents: number;
  };
  by_market: Array<{
    category: string;
    total_bets: number;
    won: number;
    lost: number;
    pushed: number;
    win_rate: number;
    total_stake: number;
    total_profit_loss: number;
    roi: number;
  }>;
  by_sportsbook: Array<{
    category: string;
    total_bets: number;
    won: number;
    lost: number;
    pushed: number;
    win_rate: number;
    total_stake: number;
    total_profit_loss: number;
    roi: number;
  }>;
  by_sport: Array<{
    category: string;
    total_bets: number;
    won: number;
    lost: number;
    pushed: number;
    win_rate: number;
    total_stake: number;
    total_profit_loss: number;
    roi: number;
  }>;
  top_players: Array<{
    player_id: number;
    player_name: string;
    total_bets: number;
    won: number;
    lost: number;
    win_rate: number;
    total_stake: number;
    total_profit_loss: number;
    roi: number;
  }>;
  worst_players: Array<{
    player_id: number;
    player_name: string;
    total_bets: number;
    won: number;
    lost: number;
    win_rate: number;
    total_stake: number;
    total_profit_loss: number;
    roi: number;
  }>;
}

export interface CLVHistoryPoint {
  date: string;
  cumulative_clv: number;
  daily_clv: number;
  bet_count: number;
}

export interface CLVHistoryResponse {
  data_points: CLVHistoryPoint[];
  total_clv: number;
  avg_daily_clv: number;
}

// =============================================================================
// Analytics Dashboard API Functions
// =============================================================================

export async function fetchMarketPerformance(
  days: number = 30,
  sportId?: number
): Promise<MarketPerformanceResponse> {
  const params = new URLSearchParams({ days: days.toString() });
  if (sportId) params.set('sport_id', sportId.toString());
  return fetchJson<MarketPerformanceResponse>(
    `${API_BASE_URL}/api/analytics/market-performance?${params}`
  );
}

export async function fetchBetStats(
  sportId?: number,
  daysBack?: number
): Promise<BetStatsResponse> {
  const params = new URLSearchParams();
  if (sportId) params.set('sport_id', sportId.toString());
  if (daysBack) params.set('days_back', daysBack.toString());
  const queryString = params.toString();
  return fetchJson<BetStatsResponse>(
    `${API_BASE_URL}/api/bets/stats/summary${queryString ? `?${queryString}` : ''}`
  );
}

export async function fetchCLVHistory(
  sportId?: number,
  daysBack: number = 30
): Promise<CLVHistoryResponse> {
  const params = new URLSearchParams({ days_back: daysBack.toString() });
  if (sportId) params.set('sport_id', sportId.toString());
  return fetchJson<CLVHistoryResponse>(
    `${API_BASE_URL}/api/bets/stats/clv-history?${params}`
  );
}

export function useMarketPerformance(days: number = 30, sportId?: number) {
  return useQuery({
    queryKey: ['market-performance', days, sportId],
    queryFn: () => fetchMarketPerformance(days, sportId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useBetStats(sportId?: number, daysBack?: number) {
  return useQuery({
    queryKey: ['bet-stats', sportId, daysBack],
    queryFn: () => fetchBetStats(sportId, daysBack),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useCLVHistory(sportId?: number, daysBack: number = 30) {
  return useQuery({
    queryKey: ['clv-history', sportId, daysBack],
    queryFn: () => fetchCLVHistory(sportId, daysBack),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// =============================================================================
// Watchlist Types
// =============================================================================

export interface WatchlistFilters {
  sport_id?: number;
  stat_type?: string;
  side?: string;
  min_ev?: number;
  min_confidence?: number;
  risk_levels?: string;
}

export interface Watchlist {
  id: number;
  name: string;
  filters: WatchlistFilters;
  alert_enabled: boolean;
  alert_discord_webhook: string | null;
  alert_email: string | null;
  sport_id: number | null;
  last_check_at: string | null;
  last_match_count: number;
  created_at: string;
  current_match_count: number;
  new_matches_since_last_check: number;
}

export interface WatchlistListResponse {
  items: Watchlist[];
  total: number;
}

export interface WatchlistCreateRequest {
  name: string;
  filters: WatchlistFilters;
  alert_enabled?: boolean;
  alert_discord_webhook?: string;
  alert_email?: string;
}

// =============================================================================
// Watchlist API Functions
// =============================================================================

export async function fetchWatchlists(sportId?: number): Promise<WatchlistListResponse> {
  const params = new URLSearchParams();
  if (sportId) params.set('sport_id', sportId.toString());
  const queryString = params.toString();
  return fetchJson<WatchlistListResponse>(
    `${API_BASE_URL}/api/watchlists${queryString ? `?${queryString}` : ''}`
  );
}

export async function createWatchlist(data: WatchlistCreateRequest): Promise<Watchlist> {
  const response = await fetch(`${API_BASE_URL}/api/watchlists`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to create watchlist: ${response.status}`);
  }
  return response.json();
}

export async function deleteWatchlist(watchlistId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/watchlists/${watchlistId}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete watchlist: ${response.status}`);
  }
}

export async function markWatchlistChecked(watchlistId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/watchlists/${watchlistId}/mark-checked`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to mark watchlist checked: ${response.status}`);
  }
}

export function useWatchlists(sportId?: number) {
  return useQuery({
    queryKey: ['watchlists', sportId],
    queryFn: () => fetchWatchlists(sportId),
    staleTime: 30 * 1000, // 30 seconds
  });
}

// =============================================================================
// Backtest Types
// =============================================================================

export interface ConfidenceBucket {
  label: string;
  count: number;
  wins: number;
  losses: number;
  hit_rate: number;
}

export interface BacktestResult {
  qualifying_bets: number;
  wins: number;
  losses: number;
  hit_rate: number;
  flat_stake_units: number;
  flat_stake_profit: number;
  flat_stake_roi: number;
  kelly_stake_units: number;
  kelly_stake_profit: number;
  kelly_stake_roi: number;
  avg_ev: number;
  avg_clv_cents: number;
  date_range: {
    start: string;
    end: string;
  };
  filters: {
    sport_id: number | null;
    stat_type: string | null;
    side: string | null;
    min_ev: number;
    min_confidence: number;
  };
  confidence_buckets: ConfidenceBucket[];
  sample_quality: 'high' | 'medium' | 'low' | 'insufficient';
  error?: string;
}

export interface BacktestFilters {
  sport_id?: number;
  stat_type?: string;
  side?: string;
  min_ev?: number;
  min_confidence?: number;
  days_back?: number;
}

// =============================================================================
// Backtest API Functions
// =============================================================================

export async function fetchBacktest(filters: BacktestFilters = {}): Promise<BacktestResult> {
  const params = new URLSearchParams();
  if (filters.sport_id) params.set('sport_id', filters.sport_id.toString());
  if (filters.stat_type) params.set('stat_type', filters.stat_type);
  if (filters.side) params.set('side', filters.side);
  if (filters.min_ev !== undefined) params.set('min_ev', filters.min_ev.toString());
  if (filters.min_confidence !== undefined) params.set('min_confidence', filters.min_confidence.toString());
  if (filters.days_back) params.set('days_back', filters.days_back.toString());
  
  const queryString = params.toString();
  return fetchJson<BacktestResult>(
    `${API_BASE_URL}/api/analytics/backtest${queryString ? `?${queryString}` : ''}`
  );
}

export function useBacktest(filters: BacktestFilters, enabled: boolean = false) {
  return useQuery({
    queryKey: ['backtest', filters],
    queryFn: () => fetchBacktest(filters),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// =============================================================================
// Shared Cards Types
// =============================================================================

export interface CardLeg {
  player_name: string;
  team_abbr: string | null;
  stat_type: string;
  line: number;
  side: string;
  odds: number;
  grade: string;
  win_prob: number;
  edge: number;
}

export interface SharedCard {
  id: string;
  url: string;
  platform: string;
  sport_id: number | null;
  legs: CardLeg[];
  leg_count: number;
  total_odds: number;
  decimal_odds: number;
  parlay_probability: number;
  parlay_ev: number;
  overall_grade: string;
  label: string;
  kelly_suggested_units: number | null;
  kelly_risk_level: string | null;
  view_count: number;
  created_at: string;
  settled: boolean;
  won: boolean | null;
}

export interface CreateCardRequest {
  platform: string;
  sport_id?: number;
  legs: CardLeg[];
  total_odds: number;
  decimal_odds: number;
  parlay_probability: number;
  parlay_ev: number;
  overall_grade: string;
  label: string;
  kelly_suggested_units?: number;
  kelly_risk_level?: string;
}

// =============================================================================
// Shared Cards API Functions
// =============================================================================

export async function createSharedCard(data: CreateCardRequest): Promise<SharedCard> {
  const response = await fetch(`${API_BASE_URL}/api/cards`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to create card: ${response.status}`);
  }
  return response.json();
}

export async function fetchSharedCard(cardId: string): Promise<SharedCard> {
  return fetchJson<SharedCard>(`${API_BASE_URL}/api/cards/${cardId}`);
}

export function useSharedCard(cardId: string | null) {
  return useQuery({
    queryKey: ['shared-card', cardId],
    queryFn: () => fetchSharedCard(cardId!),
    enabled: cardId !== null,
    staleTime: 60 * 1000, // 1 minute
  });
}

// =============================================================================
// Tonight Summary Types (What's On Tonight Dashboard)
// =============================================================================

export interface SportTonightSummary {
  sport_id: number;
  sport_name: string;
  sport_key: string;
  games_count: number;
  props_count: number;
  best_ev: number | null;
  avg_ev: number | null;
  slate_quality: 'loaded' | 'normal' | 'thin' | 'empty';
}

export interface TonightSummaryResponse {
  date: string;
  timezone: string;
  sports: SportTonightSummary[];
  total_games: number;
  total_props: number;
  overall_best_ev: number | null;
  slate_quality: 'loaded' | 'normal' | 'thin' | 'empty';
}

// =============================================================================
// Tonight Summary API Functions
// =============================================================================

export async function fetchTonightSummary(): Promise<TonightSummaryResponse> {
  return fetchJson<TonightSummaryResponse>(`${API_BASE_URL}/api/tonight/summary`);
}

export function useTonightSummary() {
  return useQuery({
    queryKey: ['tonight-summary'],
    queryFn: fetchTonightSummary,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Auto-refresh every 5 minutes
  });
}

// =============================================================================
// Model Performance Types
// =============================================================================

export interface CalibrationBucket {
  bucket_name: string;
  predicted_low: number;
  predicted_high: number;
  predicted_mid: number;
  actual_hit_rate: number;
  sample_size: number;
  calibration_error: number;
}

export interface CalibrationReport {
  sport: string;
  days: number;
  total_picks: number;
  overall_hit_rate: number;
  overall_roi: number;
  brier_score: number;
  expected_calibration_error: number;
  buckets: CalibrationBucket[];
}

export interface ModelPerformanceSummary {
  sport: string;
  days: number;
  total_picks: number;
  hit_rate: number;
  roi_percent: number;
  avg_ev: number;
  avg_clv: number;
  win_count: number;
  loss_count: number;
  pending_count: number;
}

// =============================================================================
// Model Performance API Functions
// =============================================================================

export async function fetchCalibrationReport(sport: string, days: number = 30): Promise<CalibrationReport> {
  return fetchJson<CalibrationReport>(`${API_BASE_URL}/admin/calibration/${sport}?days=${days}`);
}

export function useCalibrationReport(sport: string | null, days: number = 30) {
  return useQuery({
    queryKey: ['calibration', sport, days],
    queryFn: () => fetchCalibrationReport(sport!, days),
    enabled: sport !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export async function fetchAnalyticsDashboard(sport: string, days: number = 30): Promise<ModelPerformanceSummary> {
  return fetchJson<ModelPerformanceSummary>(`${API_BASE_URL}/api/analytics/dashboard?sport=${sport}&days=${days}`);
}

export function useAnalyticsDashboard(sport: string | null, days: number = 30) {
  return useQuery({
    queryKey: ['analytics-dashboard', sport, days],
    queryFn: () => fetchAnalyticsDashboard(sport!, days),
    enabled: sport !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// =============================================================================
// Real-Time Parlay Quote Types
// =============================================================================

export interface QuoteLegRequest {
  game_id: number;
  player_id?: number | null;
  stat_type?: string | null;
  line_value?: number | null;
  side: string;
  model_odds?: number | null;
  model_prob?: number | null;
}

export interface QuoteRequest {
  legs: QuoteLegRequest[];
  use_cache?: boolean;
}

export interface OddsMovement {
  direction: 'up' | 'down' | 'stable';
  magnitude: number;
  old_odds: number;
  new_odds: number;
  display: string | null;
  favorable: boolean;
}

export interface QuotedLeg {
  index: number;
  game_id: number;
  player_id: number | null;
  player_name: string | null;
  stat_type: string | null;
  line_value: number | null;
  side: string;
  sportsbook: string;
  current_odds: number;
  decimal_odds: number;
  implied_prob: number;
  model_odds: number | null;
  model_prob: number;
  edge: number;
  movement: OddsMovement | null;
  is_stale: boolean;
  last_update: string | null;
  found: boolean;
}

export interface QuoteResponse {
  legs: QuotedLeg[];
  leg_count: number;
  parlay_odds: number;
  parlay_decimal: number;
  parlay_probability: number;
  implied_probability: number;
  parlay_ev: number;
  has_movement: boolean;
  stale_legs: number;
  all_fresh: boolean;
  quoted_at: string;
}

export interface OddsFreshnessResponse {
  status: 'healthy' | 'degraded' | 'stale' | 'no_data' | 'unknown';
  total_lines: number;
  fresh_lines: number;
  stale_lines: number;
  freshness_pct: number;
  oldest_update: string | null;
  newest_update: string | null;
  stale_threshold_minutes: number;
  checked_at: string;
}

// =============================================================================
// Real-Time Parlay Quote API Functions
// =============================================================================

export async function quoteParlayLegs(request: QuoteRequest): Promise<QuoteResponse> {
  const response = await fetch(`${API_BASE_URL}/api/parlays/quote`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`Failed to quote parlay: ${response.status}`);
  }
  return response.json();
}

export async function fetchOddsHealth(sportId?: number): Promise<OddsFreshnessResponse> {
  const url = sportId 
    ? `${API_BASE_URL}/api/parlays/odds-health?sport_id=${sportId}`
    : `${API_BASE_URL}/api/parlays/odds-health`;
  return fetchJson<OddsFreshnessResponse>(url);
}

export function useOddsHealth(sportId?: number) {
  return useQuery({
    queryKey: ['odds-health', sportId],
    queryFn: () => fetchOddsHealth(sportId),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Refetch every minute
  });
}

// =============================================================================
// Admin Dashboard API
// =============================================================================

export type SportHealthStatus = 'ok' | 'warn' | 'error';

export interface SportHealth {
  sport_id: number;
  sport_key: string;
  game_count: number;
  prop_count: number;
  book_count: number;
  last_update: string | null;
  status: SportHealthStatus;
  issues: string[];
}

export interface AdminDashboardResponse {
  now: string;
  sports: SportHealth[];
}

export async function fetchAdminDashboard(): Promise<AdminDashboardResponse> {
  return fetchJson<AdminDashboardResponse>(`${API_BASE_URL}/admin/dashboard/summary`);
}

export function useAdminDashboard() {
  return useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: fetchAdminDashboard,
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 60 * 1000, // Auto-refresh every minute
  });
}

// =============================================================================
// Full Slate Types (Multi-Sport Prop Review)
// =============================================================================

export interface SportSlate {
  sport_id: number;
  sport_key: string;
  sport_name: string;
  date: string;
  count: number;
  props: PlayerPropPick[];
}

export interface FullSlateResponse {
  date: string;
  total_props: number;
  sports: SportSlate[];
}

// =============================================================================
// Full Slate API Functions
// =============================================================================

export async function fetchFullSlate(
  date: string,
  minEv: number = 0,
  minConfidence: number = 0,
  limitPerSport: number = 50
): Promise<FullSlateResponse> {
  const params = new URLSearchParams({
    date,
    min_ev: minEv.toString(),
    min_confidence: minConfidence.toString(),
    limit_per_sport: limitPerSport.toString(),
  });
  return fetchJson<FullSlateResponse>(`${API_BASE_URL}/api/slate/full?${params}`);
}

/**
 * Hook to fetch full slate of player props across all sports for a specific date.
 * Useful for reviewing tomorrow's entire slate.
 */
export function useFullSlate(
  date: string,
  minEv: number = 0,
  minConfidence: number = 0,
  limitPerSport: number = 50
) {
  return useQuery({
    queryKey: ['full-slate', date, minEv, minConfidence, limitPerSport],
    queryFn: () => fetchFullSlate(date, minEv, minConfidence, limitPerSport),
    enabled: !!date,
    staleTime: 60 * 1000, // 1 minute
    refetchInterval: 2 * 60 * 1000, // Auto-refresh every 2 minutes
  });
}
