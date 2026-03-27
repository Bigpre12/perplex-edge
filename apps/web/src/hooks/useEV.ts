import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { supabase } from '@/lib/supabase';

export interface EVRecord {
  id: string;
  player_name: string;
  market_key: string;
  ev_pct: number;
  edge_percent?: number;
  ev_score?: number;
  bookmaker: string;
  line?: number;
  recommendation: string;
  sport: string;
}

export const useEV = (sport: string = 'all') => {
  return useQuery({
    queryKey: ['ev', sport],
    queryFn: async () => {
      try {
        const url = sport === 'all' ? '/api/ev' : `/api/ev?sport=${sport}`;
        const { data } = await api.get(url);
        if (data && data.props) {
          return data.props as EVRecord[];
        }
        throw new Error('No EV signals returned from API');
      } catch (err) {
        console.warn('Backend EV fetch failed, falling back to Supabase', err);
        let query = supabase.from('ev_signals').select('*').order('edge_percent', { ascending: false }).limit(50);
        if (sport !== 'all') {
            query = query.eq('sport', sport);
        }
        const { data: supabaseData, error: supabaseError } = await query;

        if (supabaseError) throw supabaseError;
        return (supabaseData || []) as EVRecord[];
      }
    },
    refetchInterval: 30000, // 30s
  });
};
