const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

async function request<T = any>(
    path: string,
    options?: RequestInit,
    params?: Record<string, QueryValue>
): Promise<T | Error> {
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

        return await res.json();
    } catch (e: any) {
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
        freshness: (sport = "basketball_nba") =>
            request("/api/signals/freshness", undefined, { sport }),
    },
    wsEv: `${API_BASE.replace('http', 'ws')}/api/ev/ws`,

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
    hitRate: (sport = "all") => request("/api/hit-rate", undefined, { sport }),
    whale: (sport = "basketball_nba") => request("/api/whale", undefined, { sport }),
    parlay: (sport = "basketball_nba") => request("/api/parlay", undefined, { sport }),
    steam: (sport = "basketball_nba") => request("/api/steam", undefined, { sport }),
    search: (q: string) => request("/api/search", undefined, { q }),

    // Brain
    brain: {
        status: () => request("/api/brain/brain-status"),
        metrics: () => request("/api/metrics"), // Added alias for useBrainData
        decisions: (sport = "basketball_nba") => 
            request("/api/brain/decisions", undefined, { sport }),
        parlays: (sport = "basketball_nba") =>
            request("/api/brain/parlay-builder", undefined, { sport }),
    }
};

// Aliases for backward compatibility
(api as any).authMe = api.auth.me;
(api as any).evTop = api.ev.top;
(api as any).getEV = api.ev.top;
(api as any).propsScored = api.propsScored;
(api as any).injuries = api.injuries;
(api as any).news = api.news;
(api as any).lineMovement = api.lineMovement;
(api as any).freshness = api.signals.freshness;

export const API = api;
export const apiFetch = request;
export default api;
