import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { supabase } from '@/lib/supabase';

export const useAudit = (page: number = 0, limit: number = 50) => {
  return useQuery({
    queryKey: ['audit', page, limit],
    queryFn: async () => {
      try {
        const { data } = await api.get(`/api/audit?page=${page}&limit=${limit}`);
        if (data && data.rows) {
          return data;
        }
        throw new Error('No audit data from API');
      } catch (err) {
        console.warn('Backend audit fetch failed, falling back to Supabase', err);
        const { data: supabaseData, error: supabaseError, count } = await supabase
          .from('props_live')
          .select('*', { count: 'exact' })
          .eq('graded', true)
          .order('graded_at', { ascending: false })
          .range(page * limit, (page + 1) * limit - 1);

        if (supabaseError) throw supabaseError;
        return {
          rows: supabaseData || [],
          total: count || 0
        };
      }
    },
    refetchInterval: 120000, // 2min
  });
};
