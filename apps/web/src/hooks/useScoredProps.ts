"use client";
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { CanonicalProp } from './usePropsBoard';

export function useScoredProps(sport = "basketball_nba") {
    return useQuery<CanonicalProp[], Error>({
        queryKey: ['scoredProps', sport],
        queryFn: async () => {
            const { data } = await api.get(`/api/props/scored?sport=${sport}`);
            
            // Standardize format - handle both { data: [...] } and direct array
            const signals = Array.isArray(data) ? data : data?.data || data?.props || [];
            return signals as CanonicalProp[];
        },
        refetchInterval: 60000, // Scored data changes less frequently
        staleTime: 30000,
    });
}
