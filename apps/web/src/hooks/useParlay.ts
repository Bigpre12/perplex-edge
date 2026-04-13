import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { supabase } from '@/lib/supabase';

export const useParlay = () => {
  return useQuery({
    queryKey: ['parlay-decisions'],
    queryFn: async () => {
      try {
        // Reuse graded props if possible, but the prompt says GET /api/props/graded (reuse props data)
        const { data } = await api.get('/api/props/graded');
        return data.props as any[];
      } catch (err) {
        console.warn('Backend parlay fetch failed, falling back to Supabase', err);
        const { data: supabaseData, error: supabaseError } = await supabase
          .from('parlay_decisions')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(10);

        if (supabaseError) throw supabaseError;
        return (supabaseData || []) as any[];
      }
    },
    refetchInterval: 60000, // 60s
  });
};
