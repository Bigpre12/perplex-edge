"use client";
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { CanonicalProp } from './usePropsBoard';

export function useScoredProps(sport = "basketball_nba") {
    const effectiveSport = (!sport || sport === 'all') ? '' : sport;
    return useQuery<CanonicalProp[], Error>({
        queryKey: ['scoredProps', effectiveSport || 'all'],
        queryFn: async () => {
            const url = effectiveSport
                ? `/api/props/scored?sport=${effectiveSport}`
                : `/api/props/scored`;
            const { data } = await api.get(url);
            
            // Standardize format - handle both { data: [...] } and direct array
            const signals = Array.isArray(data) ? data : data?.data || data?.props || [];
            return signals as CanonicalProp[];
        },
        refetchInterval: 60000, // Scored data changes less frequently
        staleTime: 30000,
    });
}
