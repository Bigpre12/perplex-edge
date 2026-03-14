// ============================================================
// src/lib/api.ts — LUCRIX / PERPLEX EDGE — MASTER API LAYER
// ============================================================

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─────────────────────────────────────────────────────────────
// SPORT ID MAP — string keys → numeric IDs backend expects
// ─────────────────────────────────────────────────────────────
export const SPORT_ID_MAP: Record<string, number> = {
  basketball_nba:              30,
  americanfootball_nfl:        31,
  baseball_mlb:                32,
  icehockey_nhl:               33,
  basketball_ncaab:            34,
  americanfootball_ncaaf:      35,
  tennis_atp:                  40,
  tennis_wta:                  41,
  soccer_epl:                  50,
  soccer_usa_mls:              51,
  mma_mixed_martial_arts:      60,
  boxing_boxing:               61,
  // shorthand aliases
  nba:  30, nfl: 31, mlb: 32, nhl: 33,
  nba2: 30, ncaab: 34, ncaaf: 35,
};

export function toSportId(sport: string | number): number {
  if (typeof sport === "number") return sport;
  return SPORT_ID_MAP[sport.toLowerCase()] ?? 30;
}

export function toSportKey(id: number): string {
  return Object.entries(SPORT_ID_MAP).find(([, v]) => v === id)?.[0] ?? "basketball_nba";
}

// ─────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────
export interface ApiError {
  error:      string;
  status?:    number;
  timestamp?: string;
}

export interface ApiResponse<T = any> {
  data?:      T;
  items?:     T[];
  total?:     number;
  error?:     string;
  timestamp?: string;
}

export interface PickItem {
  id:                number;
  player_name?:      string;
  player?:           { name: string; position?: string };
  market?:           { stat_type: string; description?: string };
  stat_type?:        string;
  side:              "over" | "under";
  line_value:        number;
  odds:              number;
  expected_value:    number;
  confidence_score:  number;
  edge?:             number;
  sport_id:          number;
  generated_at?:     string;
}

export interface GameItem {
  id:          number;
  home_team:   { name: string; abbreviation?: string };
  away_team:   { name: string; abbreviation?: string };
  start_time:  string;
  sport_id:    number;
  status?:     string;
}

export interface InjuryItem {
  id:           string;
  player_name:  string;
  short_name?:  string;
  position?:    string;
  team:         string;
  status:       string;
  comment?:     string;
  detail?:      string;
  date?:        string;
  headshot?:    string;
}

export interface BrainDecision {
  id:             number;
  decision:       string;
  confidence:     number;
  expected_value: number;
  sport_id:       number;
  reasoning?:     string;
  generated_at?:  string;
}

export interface UserProfile {
  email:           string;
  tier:            "free" | "pro" | "elite";
  authenticated:   boolean;
  timestamp?:      string;
}

// ─────────────────────────────────────────────────────────────
// CIRCUIT BREAKER
// ─────────────────────────────────────────────────────────────
let _circuitOpen  = false;
let _failCount    = 0;
const FAIL_THRESH = 5;

export function resetCircuit(): void {
  _circuitOpen = false;
  _failCount   = 0;
}

export function isCircuitOpen(): boolean {
  return _circuitOpen;
}

function _recordFailure(): void {
  _failCount++;
  if (_failCount >= FAIL_THRESH) _circuitOpen = true;
}

function _recordSuccess(): void {
  _failCount   = 0;
  _circuitOpen = false;
}

// ─────────────────────────────────────────────────────────────
// TYPE GUARDS
// ─────────────────────────────────────────────────────────────
export function isApiError(result: any): result is ApiError {
  return (
    result !== null &&
    typeof result === "object" &&
    (typeof result.error === "string" || (result.status && result.status >= 400))
  );
}

export function unwrap<T>(result: T | ApiError): T {
  if (isApiError(result)) throw new Error((result as ApiError).error ?? "API Error");
  return result as T;
}

// ─────────────────────────────────────────────────────────────
// CORE FETCH WRAPPER
// ─────────────────────────────────────────────────────────────
export async function apiFetch<T = any>(
  urlOrPath: string,
  options?: RequestInit
): Promise<T | ApiError> {
  try {
    const url = urlOrPath.startsWith("http")
      ? urlOrPath
      : `${BASE_URL}${urlOrPath}`;

    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("accessToken")
        : null;

    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options?.headers,
      },
    });

    // Try to parse JSON — some endpoints return empty bodies
    let data: any = {};
    try { data = await res.json(); } catch { data = {}; }

    if (!res.ok) {
      if (res.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem("accessToken");
      }
      _recordFailure();
      return {
        error:     data?.detail ?? data?.error ?? `HTTP ${res.status}`,
        status:    res.status,
        timestamp: new Date().toISOString(),
      } as ApiError;
    }

    _recordSuccess();
    return data as T;
  } catch (err: any) {
    _recordFailure();
    return {
      error:     err?.message ?? "Network error",
      status:    0,
      timestamp: new Date().toISOString(),
    } as ApiError;
  }
}

// ─────────────────────────────────────────────────────────────
// QUERY STRING BUILDER
// ─────────────────────────────────────────────────────────────
function qs(params?: Record<string, any>): string {
  if (!params) return "";
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null && v !== ""
  );
  if (!entries.length) return "";
  return "?" + new URLSearchParams(entries.map(([k, v]) => [k, String(v)])).toString();
}

// ─────────────────────────────────────────────────────────────
// API — full endpoint map
// ─────────────────────────────────────────────────────────────
export const API = {

  // ── System ──────────────────────────────────────────────────
  health: () =>
    apiFetch("/api/health"),

  alerts: (sport: string = "basketball_nba") =>
    apiFetch(`/api/signals/alerts${qs({ sport })}`),

  // ── Auth ────────────────────────────────────────────────────
  authMe: () =>
    apiFetch<UserProfile>("/api/auth/me"),

  authLogin: (email: string, password: string) =>
    apiFetch("/api/auth/login", {
      method: "POST",
      body:   JSON.stringify({ email, password }),
    }),

  authLogout: () =>
    apiFetch("/api/auth/logout", { method: "POST" }),

  authRegister: (email: string, password: string) =>
    apiFetch("/api/auth/register", {
      method: "POST",
      body:   JSON.stringify({ email, password }),
    }),

  authTier: () =>
    apiFetch<UserProfile>("/api/auth/tier"),

  // ── Picks ────────────────────────────────────────────────────
  picks: (params?: {
    sport_id?: number | string;
    limit?:    number;
    offset?:   number;
    side?:     string;
  }) =>
    apiFetch(`/api/immediate/picks${qs({
      ...params,
      sport_id: params?.sport_id ? toSportId(params.sport_id) : undefined,
    })}`),

  picksHighEV: (min_ev = 5.0, limit = 20, sport?: number | string) =>
    apiFetch(`/api/immediate/picks/high-ev${qs({
      min_ev,
      limit,
      sport_id: sport ? toSportId(sport) : undefined,
    })}`),

  picksHighConf: (min_confidence = 80.0, limit = 20, sport?: number | string) =>
    apiFetch(`/api/immediate/picks/high-confidence${qs({
      min_confidence,
      limit,
      sport_id: sport ? toSportId(sport) : undefined,
    })}`),

  picksStats: () =>
    apiFetch("/api/immediate/picks/statistics"),

  picksSearch: (query: string, limit = 20) =>
    apiFetch(`/api/immediate/picks/search${qs({ query, limit })}`),

  picksByPlayer: (playerName: string) =>
    apiFetch(`/api/immediate/picks/player/${encodeURIComponent(playerName)}`),

  picksByGame: (gameId: number) =>
    apiFetch(`/api/immediate/picks/game/${gameId}`),

  evTop: (min_ev = 2.0, sport?: number | string) =>
    apiFetch(`/api/immediate/picks/high-ev${qs({
      min_ev,
      sport_id: sport ? toSportId(sport) : undefined,
    })}`),

  // ── Live ─────────────────────────────────────────────────────
  liveGames: (sport: string = "basketball_nba") =>
    apiFetch(`/api/live/games${qs({ sport })}`),

  liveScores: (sport: string = "basketball_nba") =>
    apiFetch(`/api/live/scores${qs({ sport })}`),

  // ── Player Props ─────────────────────────────────────────────
  playerProps: (sport: number | string = 30, limit = 20) =>
    apiFetch(`/api/immediate/working-player-props${qs({
      sport_id: toSportId(sport),
      limit,
    })}`),

  // ── Games ────────────────────────────────────────────────────
  games: (sport: number | string = 30, date?: string) =>
    apiFetch(`/api/immediate/games${qs({
      sport_id: toSportId(sport),
      ...(date ? { date } : {}),
    })}`),

  // ── Parlays ──────────────────────────────────────────────────
  parlays: (sport: number | string = 30, limit = 5) =>
    apiFetch(`/api/immediate/working-parlays${qs({
      sport_id: toSportId(sport),
      limit,
    })}`),

  // ── Monte Carlo ──────────────────────────────────────────────
  monteCarlo: () =>
    apiFetch("/api/immediate/monte-carlo"),

  monteCarloSim: (body: Record<string, any>) =>
    apiFetch("/api/analysis/monte-carlo/prop", {
      method: "POST",
      body:   JSON.stringify(body),
    }),

  // ── Injuries ─────────────────────────────────────────────────
  injuries: (sport: number | string = 30) =>
    apiFetch<{ items: InjuryItem[]; total: number }>(
      `/api/immediate/injuries${qs({ sport_id: toSportId(sport) })}`
    ),

  // ── Brain ─────────────────────────────────────────────────────
  brainDecisions: (limit = 10) =>
    apiFetch<{ items: BrainDecision[]; decisions: BrainDecision[] }>(
      `/api/immediate/brain-decisions${qs({ limit })}`
    ),

  brainHealth: () =>
    apiFetch("/api/immediate/brain-health-status"),

  brainHealthChecks: (limit = 20) =>
    apiFetch(`/api/immediate/brain-health-checks${qs({ limit })}`),

  brainMetrics: (sport?: number | string) =>
    apiFetch(`/api/brain/brain-metrics${qs({ sport_id: sport ? toSportId(sport) : undefined })}`),

  brainHeal: () =>
    apiFetch("/api/immediate/brain-healing/run-cycle", { method: "POST" }),

  // ── Hit Rate ──────────────────────────────────────────────────
  hitRateSummary: (sport: string = "basketball_nba") =>
    apiFetch(`/api/immediate/hit-rate/summary${qs({ sport })}`),

  hitRateByPlayer: (sport: string = "basketball_nba", slateOnly: boolean = false) =>
    apiFetch(`/api/immediate/hit-rate/by-player${qs({ sport, slate_only: slateOnly })}`),

  // ── Line Movement ─────────────────────────────────────────────
  lineMovement: (sport: number | string = 30) =>
    apiFetch(`/api/line-movement/line-movement${qs({ sport: toSportKey(toSportId(sport)) })}`),

  // ── Sharp / Whale ─────────────────────────────────────────────
  activeMoves: (sport?: number | string) =>
    apiFetch(`/api/immediate/picks/high-ev${qs({
      min_ev:   2.0, // Lower threshold for "moves"
      limit:    15,
      sport_id: sport ? toSportId(sport) : undefined,
    })}`),

  sharpMoves: (sport?: number | string) =>
    apiFetch(`/api/immediate/picks/high-ev${qs({
      min_ev:   3.0,
      limit:    15,
      sport_id: sport ? toSportId(sport) : undefined,
    })}`),

  whaleMoves: (sport?: number | string) =>
    apiFetch(`/api/immediate/picks/high-confidence${qs({
      min_confidence: 85,
      sport_id:       sport ? toSportId(sport) : undefined,
    })}`),

  // ── Dedicated Whale Router ────────────────────────────────────
  whaleSignals: (sport: string = "basketball_nba") =>
    apiFetch(`/api/whale${qs({ sport })}`),

  whaleActiveMoves: (sport: string = "basketball_nba") =>
    apiFetch(`/api/whale/active-moves${qs({ sport })}`),

  // ── Player Stats ──────────────────────────────────────────────
  playerStats: (params?: Record<string, any>) =>
    apiFetch(`/api/immediate/player-stats${qs(params)}`),

  // ── Analysis ─────────────────────────────────────────────────
  clvSummary: (sport: number | string = 30) =>
    apiFetch(`/api/analysis/clv-summary${qs({ sport_id: toSportId(sport) })}`),

  // ── Track Record ─────────────────────────────────────────────
  trackRecord: () =>
    apiFetch("/api/track-record/summary"),

  // ── Model Status ─────────────────────────────────────────────
  modelStatus: () =>
    apiFetch("/api/status/model-status"),

  // ── Validation ───────────────────────────────────────────────
  validationPicks: () =>
    apiFetch("/api/validation/picks"),

  validationPerf: () =>
    apiFetch("/api/validation/performance"),

  // ── Notifications ─────────────────────────────────────────────
  notifications: () =>
    apiFetch("/api/notifications"),

  notificationsRead: (id: string) =>
    apiFetch(`/api/notifications/${id}/read`, { method: "POST" }),

  notificationsReadAll: () =>
    apiFetch("/api/notifications/mark-all-read", { method: "POST" }),

  // ── Search ────────────────────────────────────────────────────
  search: (query: string, limit = 10) =>
    apiFetch(`/api/immediate/picks/search${qs({ query, limit })}`),

  // ── Arbitrage ──────────────────────────────────────────────────
  arbitrage: (sport?: string) =>
    apiFetch(`/api/arbitrage${qs({ sport })}`),

  // ── Slate ──────────────────────────────────────────────────────
  slate: (sport?: string) =>
    apiFetch(`/api/props/slate/today${qs({ sport })}`),

  // ── Subscription ──────────────────────────────────────────────
  subscription: () =>
    apiFetch("/api/subscription"),

  upgradeTier: (tier: string) =>
    apiFetch("/api/subscription/upgrade", {
      method: "POST",
      body:   JSON.stringify({ tier }),
    }),
  // Generic Methods
  get:    <T = any>(url: string, opts?: RequestInit) => apiFetch<T>(url, { ...opts, method: "GET" }),
  post:   <T = any>(url: string, body?: any, opts?: RequestInit) => apiFetch<T>(url, { ...opts, method: "POST", body: body ? JSON.stringify(body) : undefined }),
  put:    <T = any>(url: string, body?: any, opts?: RequestInit) => apiFetch<T>(url, { ...opts, method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  delete: <T = any>(url: string, opts?: RequestInit) => apiFetch<T>(url, { ...opts, method: "DELETE" }),
};

// ─────────────────────────────────────────────────────────────
// api — flat alias object (backward compat for older components)
// ─────────────────────────────────────────────────────────────
export const api = {
  health:          API.health,
  authMe:          API.authMe,
  getProps:        API.playerProps,
  props:           API.playerProps,
  getGames:        API.games,
  getParlays:      API.parlays,
  getPickStats:    API.picksStats,
  getHighEV:       API.picksHighEV,
  getHighConf:     API.picksHighConf,
  searchPicks:     API.picksSearch,
  getAnalysis:     API.clvSummary,
  trackRecord:     API.trackRecord,
  getModelStatus:  API.modelStatus,
  activeMoves:     API.activeMoves,
  sharpMoves:      API.sharpMoves,
  whaleMoves:      API.whaleMoves,
  evTop:           API.evTop,
  injuries:        API.injuries,
  brainDecisions:  API.brainDecisions,
  brainMetrics:    API.brainMetrics,
  hitRateSummary:  API.hitRateSummary,
  hitRateByPlayer: API.hitRateByPlayer,
  lineMovement:    API.lineMovement,
  liveGames:       API.liveGames,
  liveScores:      API.liveScores,
  whaleSignals:    API.whaleSignals,
  whaleActiveMoves: API.whaleActiveMoves,
  notifications:   API.notifications,
  notificationsAll: API.notificationsReadAll,  // backward compat alias
  slate:           API.slate,
  edges:           API.picksHighEV,
  arbitrage:       API.arbitrage,
  // Generic Methods
  get:    <T = any>(url: string, opts?: RequestInit) => apiFetch<T>(url, { ...opts, method: "GET" }),
  post:   <T = any>(url: string, body?: any, opts?: RequestInit) => apiFetch<T>(url, { ...opts, method: "POST", body: body ? JSON.stringify(body) : undefined }),
  put:    <T = any>(url: string, body?: any, opts?: RequestInit) => apiFetch<T>(url, { ...opts, method: "PUT", body: body ? JSON.stringify(body) : undefined }),
  delete: <T = any>(url: string, opts?: RequestInit) => apiFetch<T>(url, { ...opts, method: "DELETE" }),
};

export default API;
