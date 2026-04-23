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
  history_sparkline?: number[];
}

export const usePropsHistory = (sport: string = 'basketball_nba') => {
  return useQuery({
    queryKey: ['props-history', sport],
    queryFn: async () => {
      try {
        // Fallback to /api/props/graded as suggested if /api/history is specialized
        const { data } = await api.get(`/api/props/graded?sport=${sport}&status=settled`);
        const results = Array.isArray(data) ? data : (data.props || data.data || []);
        return (results as PropsHistoryRecord[]).map((r, i) => ({
          ...r,
          id: r?.id ?? `ph-${i}`,
          player_name: r?.player_name ?? "Unknown",
          market_key: r?.market_key ?? "—",
        }));
      } catch (err) {
        console.warn('History fetch failed', err);
        return [];
      }
    },
    refetchInterval: 120000, // 2 mins
  });
};
