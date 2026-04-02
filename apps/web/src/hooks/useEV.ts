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
          ? '/api/ev?limit=50' 
          : `/api/ev?sport=${sport}&limit=50`;
        const { data } = await api.get(url);
        
        let signals = Array.isArray(data) ? data : (data.props || data.results || data.edges || data.data || []);
        
        if (signals.length === 0) {
            console.warn(`[EV PIPELINE] Backend returned 0 edges for ${sport}. Triggering client-side scoring...`);
            
            // Fallback: Fetch scored props which contains the model probability and best odds
            const scoredUrl = sport === 'all' ? '/api/props/scored?limit=100' : `/api/props/scored?sport=${sport}&limit=100`;
            const { data: scoredData } = await api.get(scoredUrl);
            const props = Array.isArray(scoredData) ? scoredData : (scoredData.props || scoredData.data || []);
            
            if (props.length === 0) {
               console.error(`[EV PIPELINE] Critical: No scored props found for fallback on ${sport}.`);
               return [];
            }

            signals = props.map((p: any) => {
                // Calculation: (Model Prob / Implied Prob) - 1
                const modelProb = p.model_probability || p.confidence_score || 0;
                const bestOdds = p.best_odds || p.over_odds || 100;
                const impliedProb = bestOdds > 0 ? (100 / (bestOdds + 100)) : (Math.abs(bestOdds) / (Math.abs(bestOdds) + 100));
                
                const evPct = impliedProb > 0 ? ((modelProb / impliedProb) - 1) * 100 : 0;
                
                return {
                    id: p.id || Math.random().toString(),
                    player_name: p.player_name || p.player?.name || 'Matchup',
                    market_key: p.stat_type || p.market_key || 'STAT',
                    ev_pct: evPct,
                    edge_percent: evPct / 100,
                    bookmaker: p.best_book || p.sportsbook || 'Consensus',
                    line: p.line || p.line_value,
                    recommendation: p.recommendation?.side || p.side || 'over',
                    sport: p.sport || sport,
                    reasoning: p.analysis || p.insight || `High-conviction ${p.side || 'over'} signal based on ${((modelProb)*100).toFixed(1)}% model probability.`
                };
            })
            .filter((s: any) => s.ev_pct > 0.5) // Lower threshold for fallback to ensure we show SOMETHING if data is sparse
            .sort((a: any, b: any) => b.ev_pct - a.ev_pct);
        }

        return signals as EVRecord[];
      } catch (err) {
        console.error('[EV PIPELINE] Primary fetch failed:', err);
        
        try {
            console.log('[EV PIPELINE] Attempting Supabase fallback...');
            let query = supabase.from('ev_signals').select('*').order('ev_pct', { ascending: false }).limit(50);
            if (sport !== 'all') {
                query = query.eq('sport', sport);
            }
            const { data: supabaseData, error: supabaseError } = await query;
            if (supabaseError) throw supabaseError;
            return (supabaseData || []) as EVRecord[];
        } catch (sErr) {
            console.error('[EV PIPELINE] Supabase fallback failed:', sErr);
            return [];
        }
      }
    },
    refetchInterval: 30000, // 30s
  });
};
