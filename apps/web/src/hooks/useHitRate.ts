import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { getAuthenticatedClient } from '@/lib/supabaseAuth';

export interface HitRateStats {
  overall_hit_rate: number;
  roi: number;
  graded_picks: number;
  streak?: number;
}

function sanitize(raw: any): HitRateStats {
  const safe = (v: any) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : 0;
  };
  return {
    overall_hit_rate: safe(raw?.overall_hit_rate),
    roi: safe(raw?.roi),
    graded_picks: safe(raw?.graded_picks),
    streak: safe(raw?.streak),
  };
}

export const useHitRate = () => {
  return useQuery({
    queryKey: ['hit-rate'],
    queryFn: async () => {
      try {
        const { data } = await api.get('/api/hit-rate');
        return sanitize(data);
      } catch (err) {
        console.warn('Backend hit-rate fetch failed, falling back to Supabase', err);
        const supabaseAuth = getAuthenticatedClient();
        const { data: supabaseData, error: supabaseError } = await supabaseAuth
          .from('player_hit_rates')
          .select('*')
          .order('hit_rate', { ascending: false });

        if (supabaseError) throw supabaseError;
        // Map top results if needed or return list
        return (supabaseData || []) as any;
      }
    },
    refetchInterval: 120000, // 2min
  });
};

export const useHitRatePlayers = (sport = 'all') => {
  return useQuery({
    queryKey: ['hit-rate-players', sport],
    queryFn: async () => {
      try {
        const { data } = await api.get(`/api/hit-rate/players?sport=${sport}`);
        const rows = (data || []) as any[];
        return rows.map((r, i) => ({
          ...r,
          id: r?.id ?? r?.player_id ?? `hrp-${i}`,
        }));
      } catch (err) {
        console.warn('Backend hit-rate players fetch failed', err);
        const supabaseAuth = getAuthenticatedClient();
        const { data: supabaseData, error: supabaseError } = await supabaseAuth
          .from('player_hit_rates')
          .select('*')
          .order('hit_rate', { ascending: false });

        if (supabaseError) throw supabaseError;
        const rows = (supabaseData || []) as any[];
        return rows.map((r, i) => ({
          ...r,
          id: r?.id ?? r?.player_id ?? `hrp-${i}`,
        }));
      }
    },
    refetchInterval: 120000,
  });
};
