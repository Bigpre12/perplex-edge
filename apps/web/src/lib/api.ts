import axios from 'axios';
const isServer = typeof window === 'undefined';
export const API_BASE = isServer 
  ? (process.env.NEXT_PUBLIC_API_URL || 'https://perplex-edge-backend-production.up.railway.app')
  : '/backend';

const API_URL = isServer 
  ? (process.env.NEXT_PUBLIC_API_URL || 'https://perplex-edge-backend-production.up.railway.app')
  : '/backend';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper for error handling
export const handleApiError = (error: any) => {
  console.error('API Error:', error.response?.data || error.message);
  return error.response?.data || { detail: 'An unexpected error occurred' };
};

export const isApiError = (data: any) => {
  return !data || data.detail || data.error || data.message === 'error';
};

export const unwrap = (d: any): any[] => {
    if (!d) return [];
    if (Array.isArray(d)) return d;
    // Handle nested structures commonly returned by the backend
    const nested = d.data || d.results || d.items || d.props || d.games || d.edges || d.alerts || d.injuries || d.decisions || d.news || d.moves || [];
    return Array.isArray(nested) ? nested : [];
};

// Legacy API methods needed by dashboard and hooks
export const API = {
    brain: {
        status: async () => {
            try {
                const { data } = await api.get('/brain');
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        },
        decisions: async (sport?: string) => {
            try {
                const { data } = await api.get(sport ? `/brain/decisions?sport=${sport}` : '/brain/decisions');
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        },
        metrics: async () => {
            try {
                const { data } = await api.get('/brain/metrics');
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        }
    },
    ev: {
        top: async (sport?: string, limit = 10) => {
            try {
                const { data } = await api.get(`/ev/top?sport=${sport || ''}&limit=${limit}`);
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        }
    },
    signals: {
        freshness: async (sport?: string) => {
            try {
                const { data } = await api.get(`/signals/freshness?sport=${sport || ''}`);
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        }
    },
    props: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/props/graded?sport=${sport}` : '/props/graded');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    propsScored: async (sport?: string, limit = 50) => {
        try {
            const { data } = await api.get(`/props/scored?sport=${sport || ''}&limit=${limit}`);
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    injuries: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/injuries?sport=${sport}` : '/injuries');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    news: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/news?sport=${sport}` : '/news');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    lineMovement: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/line-movement?sport=${sport}` : '/line-movement');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    health: async () => {
        try {
            const { data } = await api.get('/health');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    metrics: async () => {
        try {
            const { data } = await api.get('/brain/metrics');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    brainMetrics: async () => {
        try {
            const { data } = await api.get('/brain/metrics');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    recentIntel: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/intel?sport=${sport}` : '/intel');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    alerts: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/alerts?sport=${sport}` : '/alerts');
            return data;
        } catch (err) {
            return { alerts: [], total: 0, status: 'unavailable', sport: sport || 'all' };
        }
    },
    authMe: async () => {
        try {
            const { data } = await api.get('/auth/me');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    referrals: async () => {
        try {
            const { data } = await api.get('/referrals');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    hero: async (playerName: string, sport: string) => {
        try {
            const { data } = await api.get('/hero', { params: { name: playerName, sport } });
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    activeMoves: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/alerts?sport=${sport}` : '/alerts');
            return data?.alerts || data || [];
        } catch (err) {
            return [];
        }
    },
    evTop: async (sport?: string, limit = 10) => {
        try {
            const { data } = await api.get(`/ev?sport=${sport || ''}&limit=${limit}`);
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    sharpMoves: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/alerts?sport=${sport}` : '/alerts');
            return data;
        } catch (err) {
            return { alerts: [], total: 0, status: 'unavailable' };
        }
    },
    hitRateSummary: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/hit-rate?sport=${sport}` : '/hit-rate');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    playerTrends: async (playerName: string, statType: string) => {
        try {
            const { data } = await api.get(`/props/history`, {
                params: { player_name: playerName, market_key: statType, sport: 'basketball_nba', book: 'draftkings' }
            });
            return { history: data };
        } catch (err) {
            return { history: [] };
        }
    },
    mlPredict: async (payload: any) => {
        try {
            const { data } = await api.post(`/oracle/analyze-prop`, payload);
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    ledgerStats: async () => {
        try {
            const { data } = await api.get('/bets/stats');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    backtestRun: async (payload: any) => {
        try {
            const { data } = await api.post('/backtest', payload);
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    reportingExport: (format: string) => {
        return `${API_BASE}/reporting/export?format=${format}`;
    },
    playerProfile: async (playerName: string) => {
        try {
            const { data } = await api.get('/hero', { params: { name: playerName, sport: 'basketball_nba' } });
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    }
};

export default API;
