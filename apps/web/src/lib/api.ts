import { API_BASE } from "./apiConfig";
import { UniversalResponse, PropLiveSchema, EvEdgeSchema, WhaleEventSchema, ClvTradeSchema } from "../types";
import { apiClient, api as client, APIError } from "./apiClient";

export { API_BASE };

export const unwrap = (d: any): any => {
    if (!d || isApiError(d)) return [];
    if (d.status && d.data !== undefined) return d.data;
    if (Array.isArray(d)) return d;
    return d.data || d.results || d.items || d.props || d.games || d.decisions || d.injuries || d.alerts || d;
};

/**
 * Legacy request wrapper for compatibility.
 * Redirects to the new robust apiClient.
 */
async function request<T = any>(
    path: string,
    options?: RequestInit,
    params?: Record<string, any>
): Promise<T | Error> {
    try {
        return await apiClient<T>(path, { ...options, params });
    } catch (e: any) {
        return e instanceof Error ? e : new Error(String(e));
    }
}

export function isApiError(val: any): val is Error | APIError {
    return val instanceof Error || (val && typeof val === 'object' && ('error' in val || 'detail' in val));
}

export const api = {
    // Generic
    get: <T = any>(path: string, params?: Record<string, any>) =>
        request<T>(path, { method: "GET" }, params),
    post: <T = any>(path: string, body?: any, params?: Record<string, any>) =>
        request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }, params),
    
    // Core
    health: () => request("/api/health"),
    metaHealth: () => request("/api/meta/health"), // Alias for backward compatibility
    meta: {
        health: () => request("/api/meta/health"),
        summary: () => request("/api/meta/summary"),
    },
    auth: {
        me: () => request("/api/auth/me"),
        login: (creds: any) => request("/api/auth/login", { method: "POST", body: JSON.stringify(creds) }),
    },

    // Models
    props: (sport = "basketball_nba", market?: string, minEv?: number, limit = 50, isHistorical = false) =>
        request(`/api/props${isHistorical ? '/history' : '/live'}`, { cache: isHistorical ? 'default' : 'no-store' }, { sport, market, min_ev: minEv, limit }),
    propsScored: (sport = "basketball_nba", limit = 50) =>
        request("/api/props/scored", { cache: 'no-store' }, { sport, limit }),
    hero: (player: string, sport = "basketball_nba") =>
        request(`/api/props/hero/${encodeURIComponent(player)}`, { cache: 'no-store' }, { sport }),
        
    // Canonical Board Endpoints (Phase 6)
    propsBoard: (sport = "basketball_nba", minEv?: number) =>
        request(`/api/props/${sport}`, { cache: 'no-store' }, minEv ? { min_ev: minEv } : undefined),
    evBoard: (sport = "basketball_nba", minEv?: number) =>
        request(`/api/ev/${sport}`, { cache: 'no-store' }, minEv ? { min_ev: minEv } : undefined),

    // Intel & Signals
    ev: {
        top: (sport = "basketball_nba", limit = 50, isHistorical = false) =>
            request(`/api/intel/ev-${isHistorical ? 'history' : 'top'}`, { cache: isHistorical ? 'default' : 'no-store' }, { sport, limit }),
        scanner: (sport = "basketball_nba") =>
            request("/api/ev/", { cache: 'no-store' }, { sport }),
    },
    clv: (sport = "basketball_nba", isHistorical = false) =>
        request(`/api/clv/${isHistorical ? 'history' : 'live'}`, { cache: isHistorical ? 'default' : 'no-store' }, { sport }),
    clvLeaderboard: () => request("/api/clv/leaderboard", { cache: 'no-store' }),
    signals: {
        sharp: (sport = "basketball_nba") =>
            request("/api/signals/sharp-moves", undefined, { sport }),
        freshness: (sport = "basketball_nba") =>
            request("/api/signals/freshness", undefined, { sport }),
    },
    
    // Features
    injuries: (sport = "basketball_nba", isHistorical = false) =>
        request(`/api/injuries${isHistorical ? '/history' : '/live'}`, { cache: isHistorical ? 'default' : 'no-store' }, { sport }),
    news: (sport = "basketball_nba") =>
        request("/api/news", { cache: 'no-store' }, { sport }),
    lineMovement: (sport = "basketball_nba") =>
        request("/api/line-movement", { cache: 'no-store' }, { sport }),
    liveGames: (sport = "basketball_nba") =>
        request("/api/live/games", undefined, { sport }),
    slate: (sport = "basketball_nba") =>
        request("/api/slate/today", undefined, { sport }),
    arbitrage: (sport = "basketball_nba") =>
        request("/api/arbitrage", undefined, { sport }),
    middleBoost: (sport = "basketball_nba") =>
        request("/api/arbitrage", undefined, { sport }),
    
    // Intelligence Tier Aliases
    recentIntel: (sport = "basketball_nba") =>
        request("/api/intel/ev-top", undefined, { sport, limit: 10 }),
    
    // Misc
    metrics: () => request("/api/metrics"),
    performance: (timeframe = "24h") => request("/api/metrics", undefined, { timeframe }),
    adminStats: () => request("/api/metrics"),
    picksStats: () => request("/api/metrics/picks-stats"),
    hitRate: (sport = "all") => request("/api/hit-rate", undefined, { sport }),
    hitRateSummary: (sport = "all") => request("/api/hit-rate/summary", undefined, { sport }),
    hitRateByPlayer: (sport = "all", slate_only = false) => request("/api/hit-rate/by-player", undefined, { sport, slate_only }),
    hitRateTrends: (sport = "all") => request("/api/hit-rate/trends", { cache: 'no-store' }, { sport }),
    hitRateOutliers: (params: { sport?: string; min_hit_rate?: number; window?: number; market?: string; limit?: number }) => 
        request("/api/hit-rate/outliers", { cache: 'no-store' }, params),
    whale: (sport = "basketball_nba", min_units = 0, isHistorical = false) => 
        request(`/api/whale/${isHistorical ? 'history' : 'live'}`, { cache: isHistorical ? 'default' : 'no-store' }, { sport, min_units }),
    whaleSignals: (sport = "basketball_nba", min_units = 0, isHistorical = false) => 
        request(`/api/whale/${isHistorical ? 'history' : 'live'}`, { cache: isHistorical ? 'default' : 'no-store' }, { sport, min_units }),
    parlay: (sport = "basketball_nba") => request("/api/parlay", { cache: 'no-store' }, { sport }),
    steam: (sport = "basketball_nba") => request("/api/steam", { cache: 'no-store' }, { sport }),
    sharpMoves: (sport = "basketball_nba") => request("/api/signals/sharp-moves", { cache: 'no-store' }, { sport }),
    search: (q: string) => request("/api/search", undefined, { q }),
    globalSearch: (q: string) => request("/api/search", undefined, { q }),
    ledgerMyBets: () => request("/api/bets"),
    bets: () => request("/api/bets"),
    settleBet: (betId: string, data: any) => request(`/api/bets/${betId}`, { method: "PATCH", body: JSON.stringify(data) }),
    ledgerStats: (sport = "all") => request("/api/bets/stats", undefined, { sport }),
    stripeCheckout: (data: any) => request("/api/stripe/create-checkout-session", { method: "POST", body: JSON.stringify(data) }),
    affiliateMyLink: () => request("/api/affiliate/link"),
    
    // Brain
    brain: {
        status: () => request("/api/brain/status"),
        brainStatus: () => request("/api/brain/status"),
        metrics: () => request("/api/brain/metrics"),
        decisions: (sport = "basketball_nba") => 
            request("/api/brain/decisions", undefined, { sport }),
        parlays: (sport = "basketball_nba") =>
            request("/api/brain/parlay-builder", undefined, { sport }),
        heatmap: (sport = "basketball_nba") =>
            request("/api/brain/heatmap", undefined, { sport }),
        reasoningFeed: (sport = "basketball_nba") =>
            request("/api/brain/insights", undefined, { sport }),
        propScore: (sport = "basketball_nba") =>
            request("/api/brain/decisions", undefined, { sport }),
        parlayBuilder: (sport = "basketball_nba") =>
            request("/api/brain/parlay-builder", undefined, { sport }),
    },

    // AI & Oracle
    oracle: (data: any) => request("/api/oracle/chat", { method: "POST", body: JSON.stringify(data) }),
    aiChat: (data: any) => request("/api/oracle/chat", { method: "POST", body: JSON.stringify(data) }),
    mlPredict: (data: any) => request("/api/brain/analyze", { method: "POST", body: JSON.stringify(data) }),

    // Settings & Config
    edgeConfig: () => request("/api/settings/edge-config"),
    saveEdgeConfig: (config: any) => request("/api/settings/edge-config", { method: "POST", body: JSON.stringify(config) }),
    updateWebhooks: (data: any) => request("/api/auth/profile/update-webhooks", { method: "POST", body: JSON.stringify(data) }),
    backtestRun: (params: any) => request("/api/backtest/run", { method: "POST", body: JSON.stringify(params) }),

    // Users / Legacy
    userProfile: () => request("/api/auth/me"),
    playerProfile: (id: string) => request(`/api/users/${id}`),
    playerTrends: (sport = "basketball_nba") => request("/api/hit-rate/players", undefined, { sport }),
    autocopy: (data: any) => request("/api/users/autocopy", { method: "POST", body: JSON.stringify(data) }),
    referrals: () => request("/api/users/referrals"),

    // Legacy Aliases
    authMe: () => request("/api/auth/me"),
    authKeys: () => request("/api/auth/keys"),
    generateKey: (label: string) => request("/api/auth/keys/generate", { method: "POST", body: JSON.stringify({ label }) }),
    evTop: (sport = "basketball_nba", limit = 50) => request("/api/ev/ev-top", undefined, { sport, limit }),
    getEV: (sport = "basketball_nba", limit = 50) => request("/api/ev/ev-top", undefined, { sport, limit }),
    getProps: (sport = "basketball_nba", limit = 25) => request("/api/props", undefined, { sport, limit }),
    brainMetrics: () => request("/api/brain/metrics"),
    getHealth: () => request("/api/health"),
    activeMoves: (sport = "basketball_nba", min_units = 0) => request("/api/whale", undefined, { sport, min_units }),
    steamAlerts: (sport = "basketball_nba") => request("/api/steam", undefined, { sport }),
    alerts: (sport = "basketball_nba") => request("/api/intel/ev-top", undefined, { sport, limit: 10 }),
    wsBaseUrl: API_BASE.replace(/^http/, 'ws'),
    wsOdds: `${API_BASE.replace(/^http/, 'ws')}/api/ws/ev`,
    wsEv: `${API_BASE.replace(/^http/, 'ws')}/api/ws/ev`, // Alias for wsOdds
    wsKalshi: `${API_BASE.replace(/^http/, 'ws')}/api/ws/kalshi`,
    pollMs: 30000,
    edges: (sport = "basketball_nba") => request("/api/ev/ev-top", undefined, { sport }),
    simulate: (legs: any[], stake = 100, simulations = 10000) => 
        request("/api/simulate", { method: "POST", body: JSON.stringify({ legs, stake, simulations }) }),

    // Extended Interface (Requested)
    fetchPropsLive: (token: string) => 
        request<UniversalResponse<PropLiveSchema[]>>("/api/props/live", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchPropsList: (token: string) => 
        request<UniversalResponse<any>>("/api/props", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchPropsScored: (token: string) => 
        request<UniversalResponse<any>>("/api/props/scored", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchEVSignals: (token: string) => 
        request<UniversalResponse<any>>("/api/ev/", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchEVTop: (token: string) => 
        request<UniversalResponse<any>>("/api/intel/ev-top", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchBrainDecisions: (token: string) => 
        request<UniversalResponse<any>>("/api/brain/decisions", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchParlayBuilder: (token: string) => 
        request<UniversalResponse<any>>("/api/brain/parlay-builder", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchSteamAlerts: (token: string) => 
        request<UniversalResponse<any>>("/api/steam", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchSmartMoney: (token: string) => 
        request<UniversalResponse<any>>("/api/smart-money", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchSteamFeed: (token: string) => 
        request<UniversalResponse<any>>("/api/steam", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchWhaleFeed: (token: string) => 
        request<UniversalResponse<any>>("/api/whale/live", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchHitRateSummary: (token: string) => 
        request<UniversalResponse<any>>("/api/hit-rate/summary", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchHitRatePlayers: (token: string) => 
        request<UniversalResponse<any>>("/api/hit-rate/by-player", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchHitRateTrends: (token: string) => 
        request<UniversalResponse<any>>("/api/hit-rate/trends", { headers: { "Authorization": `Bearer ${token}` } }),
    fetchPerformanceSummary: (token: string) => 
        request<UniversalResponse<any>>("/api/metrics", { headers: { "Authorization": `Bearer ${token}` } }),

    // Billing
    billing: {
        createCheckoutSession: (priceId: string) => 
            request("/api/billing/create-checkout-session", { method: "POST", body: JSON.stringify({ price_id: priceId }) }),
        createPortalSession: () => 
            request("/api/billing/create-portal-session", { method: "POST" }),
        status: () => request("/api/billing/status"),
    },
};

export const API = api;
export const apiFetch = request;
export default api;

/**
 * Circuit breaker reset — now a no-op as the new apiClient handles retries internally.
 */
export function resetCircuit(): void {
    // Legacy support
}
