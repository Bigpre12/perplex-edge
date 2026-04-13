import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { supabase } from '@/lib/supabase';

export interface PropRecord {
  id: string;
  player_name: string;
  market_key: string;
  line: number;
  odds_over: number;
  odds_under: number;
  confidence: number;
  grade: string;
  sport: string;
  book: string;
  commence_time: string;
}

export const useProps = (sport: string = 'basketball_nba') => {
  return useQuery({
    queryKey: ['props', sport],
    queryFn: async () => {
      try {
        const { data } = await api.get(`/api/props/scored?sport=${sport}`);
        const props = Array.isArray(data) ? data : (data.props || data.data || []);
        return props as PropRecord[];
      } catch (err) {
        console.warn('Backend props fetch failed, falling back to Supabase', err);
        const { data: supabaseData, error: supabaseError } = await supabase
          .from('props_live')
          .select('*')
          .eq('sport', sport)
          .order('last_updated_at', { ascending: false })
          .limit(50);

        if (supabaseError) throw supabaseError;
        return (supabaseData || []) as PropRecord[];
      }
    },
    refetchInterval: 60000, // 60s
  });
};
