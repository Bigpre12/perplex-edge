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
        const url = sport === 'all' 
          ? '/api/ev/top?limit=25' 
          : `/api/ev/top?sport=${sport}&limit=25`;
        const { data } = await api.get(url);
        
        let signals = Array.isArray(data) ? data : (data.props || data.data || []);
        
        if (signals.length === 0) {
            console.log('[CLIENT-SIDE EV CALC TRIGGERED]');
            // Fallback: Fetch all props and calculate EV manually
            const { data: rawProps } = await api.get(`/api/props/${sport === 'all' ? 'basketball_nba' : sport}`);
            const props = rawProps?.props || [];
            signals = props.map((p: any) => ({
                id: p.id,
                player_name: p.player_name || p.team,
                market_key: p.stat_type,
                ev_pct: p.ev_percentage || ((p.model_probability / (1 / (p.over_odds > 0 ? (p.over_odds/100 + 1) : (100/Math.abs(p.over_odds) + 1)))) - 1) * 100,
                bookmaker: p.best_book || 'DraftKings',
                sport: p.sport || sport,
                line: p.line,
                recommendation: p.recommendation?.side || 'over'
            })).filter((s: any) => s.ev_pct > 2); // Only show 2%+ EV in the signal feed
        }

        return signals as EVRecord[];
      } catch (err) {
        console.warn('Backend EV fetch failed, falling back to Supabase', err);
        console.log('[CLIENT-SIDE EV CALC TRIGGERED]');
        
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
