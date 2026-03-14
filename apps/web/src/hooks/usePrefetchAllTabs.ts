"use client";

import { useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { api } from '@/lib/api';
import { useSport } from '@/context/SportContext';

/**
 * usePrefetchAllTabs - Warms the cache by prefetching core data for all major tabs.
 * Fired on app load and whenever the selected sport changes.
 */
export function usePrefetchAllTabs() {
    const queryClient = useQueryClient();
    const { selectedSport: activeSport } = useSport();

    useEffect(() => {
        const prefetch = async () => {
            const endpoints = [
                { key: ['props', activeSport], fn: () => api.props(activeSport) },
                { key: ['brain-metrics', activeSport], fn: () => api.brainMetrics(activeSport) },
                { key: ['injuries', activeSport], fn: () => api.injuries(activeSport) },
                { key: ['ev-top', activeSport], fn: () => api.evTop(2, activeSport) },
                { key: ['sharp-moves', activeSport], fn: () => api.sharpMoves(activeSport) },
                { key: ['line-movement', activeSport], fn: () => api.lineMovement(activeSport) },
                { key: ['hit-rate-summary', activeSport], fn: () => api.hitRateSummary(activeSport) },
            ];

            // Prefetch each query with a 1-minute stale time to ensure immediate tab availability
            await Promise.allSettled(
                endpoints.map(({ key, fn }) =>
                    queryClient.prefetchQuery({
                        queryKey: key,
                        queryFn: fn,
                        staleTime: 60000,
                    })
                )
            );
        };

        if (activeSport) {
            prefetch();
        }
    }, [activeSport, queryClient]);
}
