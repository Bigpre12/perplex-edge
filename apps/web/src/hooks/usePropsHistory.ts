import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface PropsHistoryRecord {
  id: string;
  player_name: string;
  market_key: string;
  line: number;
  result_value?: number;
  status: 'HIT' | 'MISS' | 'PENDING';
  sport: string;
  commence_time: string;
  actual_score?: number;
  confidence?: number;
  prediction?: 'OVER' | 'UNDER';
  book?: string;
  odds_over?: number;
  odds_under?: number;
  snapshot_at?: string;
  history_sparkline?: number[];
}

export const usePropsHistory = (sport: string = 'basketball_nba') => {
  return useQuery({
    queryKey: ['props-history', sport],
    queryFn: async () => {
      try {
        // Migrated from /api/props/graded to unified /api/history/props
        const { data } = await api.get(`/api/history/props?sport=${sport}&limit=50`);
        
        if (data.status !== 'ok') {
          console.warn('History API returned error status', data.message);
          return [];
        }

        const results = data.data || [];
        return (results as any[]).map((r, i) => ({
          ...r,
          id: r?.id ?? `ph-${i}-${r.snapshot_at}`,
          player_name: r?.player_name ?? "Unknown",
          market_key: r?.market_key ?? "—",
          // Map legacy fields if needed for UI components
          commence_time: r.snapshot_at,
          status: 'PENDING' // Props history from snapshots is inherently pending/observational
        }));
      } catch (err) {
        console.warn('History fetch failed', err);
        return [];
      }
    },
    refetchInterval: 120000, // 2 mins
  });
};
