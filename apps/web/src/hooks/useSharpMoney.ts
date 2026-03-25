import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { supabase } from '@/lib/supabase';

export interface SharpAlert {
  id: string;
  player_name: string;
  market_key: string;
  sharp_side: string;
  line_movement: number;
  is_steam: boolean;
  is_whale: boolean;
  created_at: string;
}

export const useSharpMoney = () => {
  return useQuery({
    queryKey: ['sharp-money'],
    queryFn: async () => {
      try {
        const { data } = await api.get('/api/smart-money');
        if (data && data.alerts) {
          return data.alerts as SharpAlert[];
        }
        throw new Error('No sharp alerts returned from API');
      } catch (err) {
        console.warn('Backend sharp-money fetch failed, falling back to Supabase', err);
        const { data: supabaseData, error: supabaseError } = await supabase
          .from('sharp_alerts')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(30);

        if (supabaseError) throw supabaseError;
        return (supabaseData || []) as SharpAlert[];
      }
    },
    refetchInterval: 30000, // 30s
  });
};
