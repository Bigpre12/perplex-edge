import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { getAuthenticatedClient } from '@/lib/supabaseAuth';

export interface HitRateStats {
  overall_hit_rate: number;
  roi: number;
  graded_picks: number;
  streak?: number;
}

export const useHitRate = () => {
  return useQuery({
    queryKey: ['hit-rate'],
    queryFn: async () => {
      try {
        const { data } = await api.get('/api/hit-rate');
        return data as HitRateStats;
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
        return (data || []) as any[];
      } catch (err) {
        console.warn('Backend hit-rate players fetch failed', err);
        const supabaseAuth = getAuthenticatedClient();
        const { data: supabaseData, error: supabaseError } = await supabaseAuth
          .from('player_hit_rates')
          .select('*')
          .order('hit_rate', { ascending: false });

        if (supabaseError) throw supabaseError;
        return (supabaseData || []) as any[];
      }
    },
    refetchInterval: 120000,
  });
};
