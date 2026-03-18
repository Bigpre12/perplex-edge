import { API_BASE, API_HOST } from "./apiConfig";

const API_BASE_URL = API_BASE;

type QueryValue = string | number | boolean | undefined | null;

export const unwrap = (d: any): any => {
    if (!d || isApiError(d)) return [];
    if (Array.isArray(d)) return d;
    return d.data || d.results || d.items || d.props || d.games || d.decisions || d.injuries || d.alerts || d;
};

function buildUrl(path: string, params?: Record<string, QueryValue>) {
    const base = API_BASE;

    // In the browser we intentionally use relative `/api/*` so Next rewrites can proxy.
    if (!base) {
        if (!params) return path;
        const sp = new URLSearchParams();
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) sp.set(key, String(value));
        });
        const qs = sp.toString();
        return qs ? `${path}?${qs}` : path;
    }

    // On the server we need an absolute URL.
    const url = new URL(`${base}${path}`);
    if (params) {
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) url.searchParams.set(key, String(value));
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
    props: (sport = "basketball_nba", limit = 25) =>
        request("/api/props", undefined, { sport, limit }),
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
    signals: {
        sharp: (sport = "basketball_nba") =>
            request("/api/signals/sharp-moves", undefined, { sport }),
        scanner: (sport = "basketball_nba") =>
            request("/api/ev/ev-top", undefined, { sport }),
    },
    wsEv: API_HOST.replace(/^http/, 'ws'),

    // Features
    injuries: (sport = "basketball_nba") =>
        request("/api/injuries", undefined, { sport }),
    news: (sport = "basketball_nba") =>
        request("/api/news", undefined, { sport }),
    lineMovement: (sport = "basketball_nba") =>
        request("/api/lines", undefined, { sport }),
    liveGames: (sport = "basketball_nba") =>
        request("/api/live/games", undefined, { sport }),
    
    // Intelligence Tier Aliases (for useBrainData etc)
    recentIntel: (sport = "basketball_nba") =>
        request("/api/intel/ev-top", undefined, { sport, limit: 10 }),
    
    // Misc
    metrics: () => request("/api/metrics"),
    picksStats: () => request("/api/metrics/picks-stats"),
    hitRate: (sport = "all") => request("/api/hit-rate", undefined, { sport }),
    whale: (sport = "basketball_nba") => request("/api/whale", undefined, { sport }),
    parlay: (sport = "basketball_nba") => request("/api/parlay", undefined, { sport }),
    steam: (sport = "basketball_nba") => request("/api/steam", undefined, { sport }),
    search: (q: string) => request("/api/search", undefined, { q }),
    ledgerMyBets: () => request("/api/bets"),
    ledgerStats: (sport = "all") => request("/api/bets/stats", undefined, { sport }),
    socialShare: (data: any, token: string) => request("/api/meta/share", { method: "POST", body: JSON.stringify(data), headers: { "Authorization": `Bearer ${token}` } }),

    // Brain
    brain: {
        status: () => request("/api/brain/brain-status"),
        metrics: () => request("/api/metrics"), // Added alias for useBrainData
        decisions: (sport = "basketball_nba") => 
            request("/api/brain/decisions", undefined, { sport }),
        parlays: (sport = "basketball_nba") =>
            request("/api/brain/parlay-builder", undefined, { sport }),
    },

    // Legacy Aliases for Component Backward Compatibility
    authMe: () => request("/api/auth/me"),
    evTop: (sport = "basketball_nba", limit = 50) => request("/api/ev/ev-top", undefined, { sport, limit }),
    getEV: (sport = "basketball_nba", limit = 50) => request("/api/ev/ev-top", undefined, { sport, limit }),
    getProps: (sport = "basketball_nba", limit = 25) => request("/api/props", undefined, { sport, limit }),
    brainMetrics: () => request("/api/metrics"),
    getHealth: () => request("/api/health"),
    activeMoves: (sport = "basketball_nba") => request("/api/whale", undefined, { sport }),
    steamAlerts: (sport = "basketball_nba") => request("/api/steam", undefined, { sport }),
    alerts: (sport = "basketball_nba") => request("/api/intel/ev-top", undefined, { sport, limit: 10 }),
    wsBaseUrl: API_HOST.replace(/^http/, 'ws'),
    wsOdds: `${API_HOST.replace(/^http/, 'ws')}/api/ev/ws`,
    wsKalshi: `${API_HOST.replace(/^http/, 'ws')}/api/kalshi/ws`,
    share: () => "/api/meta/share",
    reportingExport: (format: string) => `/api/metrics/export?format=${format}`,

    // Institutional / Execution
    authKeys: () => request("/api/auth/keys"),
    generateKey: (label: string) =>
        request("/api/auth/keys", { method: "POST", body: JSON.stringify({ label }) }),
    updateWebhooks: (data: any) =>
        request("/api/settings/webhooks", { method: "POST", body: JSON.stringify(data) }),
    edgeConfig: () => request("/api/settings/edge-config"),
    saveEdgeConfig: (config: any) =>
        request("/api/settings/edge-config", { method: "POST", body: JSON.stringify(config) }),
    backtestRun: (params: any) =>
        request("/api/backtest/run", { method: "POST", body: JSON.stringify(params) }),

    // Hit Rate & Trends
    hitRateSummary: (sport = "all") =>
        request("/api/hit-rate/summary", undefined, { sport }),
    hitRateByPlayer: (sport = "all", slateOnly = false) =>
        request("/api/hit-rate/by-player", undefined, { sport, slate_only: slateOnly }),
    trendHunter: (sport = "basketball_nba", timeframe = "10g") =>
        request("/api/trends/hunter", undefined, { sport, timeframe }),
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
