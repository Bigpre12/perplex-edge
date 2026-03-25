import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://perplex-edge-backend-production.up.railway.app';

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
                const { data } = await api.get('/api/brain');
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        },
        decisions: async (sport?: string) => {
            try {
                const { data } = await api.get(sport ? `/api/brain/decisions?sport=${sport}` : '/api/brain/decisions');
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        },
        metrics: async () => {
            try {
                const { data } = await api.get('/api/brain/metrics');
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        }
    },
    ev: {
        top: async (sport?: string, limit = 10) => {
            try {
                const { data } = await api.get(`/api/ev/top?sport=${sport || ''}&limit=${limit}`);
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        }
    },
    signals: {
        freshness: async (sport?: string) => {
            try {
                const { data } = await api.get(`/api/signals/freshness?sport=${sport || ''}`);
                return data;
            } catch (err) {
                return handleApiError(err);
            }
        }
    },
    props: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/api/props/graded?sport=${sport}` : '/api/props/graded');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    propsScored: async (sport?: string, limit = 50) => {
        try {
            const { data } = await api.get(`/api/props/scored?sport=${sport || ''}&limit=${limit}`);
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    injuries: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/api/injuries?sport=${sport}` : '/api/injuries');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    news: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/api/news?sport=${sport}` : '/api/news');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    lineMovement: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/api/line-movement?sport=${sport}` : '/api/line-movement');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    health: async () => {
        try {
            const { data } = await api.get('/api/health');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    metrics: async () => {
        try {
            const { data } = await api.get('/api/brain/metrics');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    brainMetrics: async () => {
        try {
            const { data } = await api.get('/api/brain/metrics');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    recentIntel: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/api/intel?sport=${sport}` : '/api/intel');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    alerts: async (sport?: string) => {
        try {
            const { data } = await api.get(sport ? `/api/alerts?sport=${sport}` : '/api/alerts');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    authMe: async () => {
        try {
            const { data } = await api.get('/api/auth/me');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    },
    referrals: async () => {
        try {
            const { data } = await api.get('/api/referrals');
            return data;
        } catch (err) {
            return handleApiError(err);
        }
    }
};

export default API;
