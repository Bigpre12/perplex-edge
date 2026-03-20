import { API_BASE } from "./apiConfig";

const API_BASE_URL = API_BASE;

type QueryValue = string | number | boolean | undefined | null;

export const unwrap = (d: any): any => {
    if (!d || isApiError(d)) return [];
    if (Array.isArray(d)) return d;
    return d.data || d.results || d.items || d.props || d.games || d.decisions || d.injuries || d.alerts || d;
};

function buildUrl(path: string, params?: Record<string, QueryValue>) {
    const url = new URL(`${API_BASE}${path}`);
    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                url.searchParams.set(key, String(value));
            }
        });
    }
    return url.toString();
}

let failureCount = 0;
let lastFailureTime = 0;
const BREAKER_THRESHOLD = 5;
const BREAKER_COOLDOWN = 30000; // 30s

async function request<T = any>(
    path: string,
    options?: RequestInit,
    params?: Record<string, QueryValue>
): Promise<T | Error> {
    // Circuit Breaker Logic
    if (failureCount >= BREAKER_THRESHOLD) {
        const now = Date.now();
        if (now - lastFailureTime < BREAKER_COOLDOWN) {
            return new Error("Circuit breaker is open. Request blocked.");
        } else {
            // Half-open: allow one request to test the waters
            failureCount = BREAKER_THRESHOLD - 1;
        }
    }

    try {
        const token = typeof window !== 'undefined' ? localStorage.getItem("accessToken") : null;
        
        const res = await fetch(buildUrl(path, params), {
            headers: {
                "Content-Type": "application/json",
                ...(token ? { "Authorization": `Bearer ${token}` } : {}),
                ...(options?.headers || {}),
            },
            ...options,
        });

        if (!res.ok) {
            failureCount++;
            lastFailureTime = Date.now();
            const text = await res.text();
            let errorMessage = `${res.status} ${res.statusText}`;
            try {
                const json = JSON.parse(text);
                errorMessage = json.detail || json.message || errorMessage;
            } catch {
                if (text && text.length < 100) errorMessage = text;
            }
            return new Error(errorMessage);
        }

        failureCount = 0; // Success! Reset breaker
        return await res.json();
    } catch (e: any) {
        failureCount++;
        lastFailureTime = Date.now();
        return e instanceof Error ? e : new Error(String(e));
    }
}

export function isApiError(val: any): val is Error {
    return val instanceof Error || (val && typeof val === 'object' && ('error' in val || 'detail' in val));
}

export const api = {
    // Generic
    get: <T = any>(path: string, params?: Record<string, QueryValue>) =>
        request<T>(path, { method: "GET" }, params),
    post: <T = any>(path: string, body?: any, params?: Record<string, QueryValue>) =>
        request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }, params),
    
    // Core
    health: () => request("/api/health"),
    meta: {
        health: () => request("/api/meta/health"),
        summary: () => request("/api/meta/summary"),
    },
    auth: {
        me: () => request("/api/auth/me"),
        login: (creds: any) => request("/api/auth/login", { method: "POST", body: JSON.stringify(creds) }),
    },

    // Models
    props: (sport = "basketball_nba", market?: string, minEv?: number, limit = 50) =>
        request("/api/props", undefined, { sport, market, min_ev: minEv, limit }),
    propsScored: (sport = "basketball_nba", limit = 50) =>
        request("/api/props/scored", undefined, { sport, limit }),

    // Intel & Signals
    ev: {
        top: (sport = "basketball_nba", limit = 50) =>
            request("/api/ev/ev-top", undefined, { sport, limit }),
        scanner: (sport = "basketball_nba") =>
            request("/api/ev/", undefined, { sport }),
    },
    clv: (sport = "basketball_nba") =>
        request("/api/clv/", undefined, { sport }),
    clvLeaderboard: () => request("/api/clv/leaderboard"),
    signals: {
        sharp: (sport = "basketball_nba") =>
            request("/api/signals/sharp-moves", undefined, { sport }),
        freshness: (sport = "basketball_nba") =>
            request("/api/signals/freshness", undefined, { sport }),
    },
    
    // Features
    injuries: (sport = "basketball_nba") =>
        request("/api/injuries", undefined, { sport }),
    news: (sport = "basketball_nba") =>
        request("/api/news", undefined, { sport }),
    lineMovement: (sport = "basketball_nba") =>
        request("/api/line-movement", undefined, { sport }),
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
    hitRateTrends: (sport = "all") => request("/api/hit-rate/trends", undefined, { sport }),
    hitRateOutliers: (params: { sport?: string; min_hit_rate?: number; window?: number; market?: string; limit?: number }) => 
        request("/api/hit-rate/outliers", undefined, params),
    whale: (sport = "basketball_nba") => request("/api/whale", undefined, { sport }),
    whaleSignals: (sport = "basketball_nba") => request("/api/whale", undefined, { sport }),
    parlay: (sport = "basketball_nba") => request("/api/parlay", undefined, { sport }),
    steam: (sport = "basketball_nba") => request("/api/steam", undefined, { sport }),
    sharpMoves: (sport = "basketball_nba") => request("/api/signals/sharp-moves", undefined, { sport }),
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
    activeMoves: (sport = "basketball_nba") => request("/api/whale", undefined, { sport }),
    steamAlerts: (sport = "basketball_nba") => request("/api/steam", undefined, { sport }),
    alerts: (sport = "basketball_nba") => request("/api/intel/ev-top", undefined, { sport, limit: 10 }),
    wsBaseUrl: API_BASE.replace(/^http/, 'ws'),
    wsOdds: `${API_BASE.replace(/^http/, 'ws')}/api/ws/ev`,
    wsKalshi: `${API_BASE.replace(/^http/, 'ws')}/api/ws/kalshi`,
    edges: (sport = "basketball_nba") => request("/api/ev/ev-top", undefined, { sport }),
    simulate: (legs: any[], stake = 100, simulations = 10000) => 
        request("/api/simulate", { method: "POST", body: JSON.stringify({ legs, stake, simulations }) }),
};

export const API = api;
export const apiFetch = request;
export default api;

/**
 * Circuit breaker reset — called by useHealthMonitor when the API comes back
 * online. Currently a no-op; extend if a real breaker is added in future.
 */
export function resetCircuit(): void {
    failureCount = 0;
    lastFailureTime = 0;
}
