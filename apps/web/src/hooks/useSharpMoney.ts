import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { supabase } from '@/lib/supabase';

export interface SharpAlert {
  id: string;
  type: 'sharp' | 'whale';
  selection: string;
  player_name?: string; // For legacy compatibility
  market_key?: string;
  market?: string;
  sharp_side?: string;
  side?: string;
  line_movement?: number;
  severity?: number;
  rating?: number;
  move_size?: string;
  signal_type?: string;
  is_steam?: boolean;
  is_whale?: boolean;
  created_at: string;
}

export const useSharpMoney = (sport = 'basketball_nba', since = '24h') => {
  return useQuery({
    queryKey: ['sharp-money', sport, since],
    queryFn: async () => {
      try {
        const { data } = await api.get(`/api/sharp/alerts?sport=${sport}&since=${since}`);
        const signals = Array.isArray(data) ? data : (data.data || data.alerts || []);
        
        return signals as SharpAlert[];
      } catch (err) {
        console.warn('Backend /api/sharp/alerts fetch failed, falling back to Supabase', err);
        const { data: supabaseData, error: supabaseError } = await supabase
          .from('sharp_alerts')
          .select('*')
          .eq('sport', sport)
          .order('created_at', { ascending: false })
          .limit(30);

        if (supabaseError) throw supabaseError;
        return (supabaseData || []) as SharpAlert[];
      }
    },
    refetchInterval: 30000, // 30s
  });
};
