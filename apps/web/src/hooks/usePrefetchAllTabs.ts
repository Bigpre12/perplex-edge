"use client";

import { useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { API } from '@/lib/api';
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
                { key: ['props', activeSport], fn: () => API.props(activeSport) },
                { key: ['brain-metrics', activeSport], fn: () => API.brainMetrics() },
                { key: ['injuries', activeSport], fn: () => API.injuries(activeSport) },
                { key: ['ev-top', activeSport], fn: () => API.evTop(activeSport, 2) },
                { key: ['sharp-moves', activeSport], fn: () => API.sharpMoves(activeSport) },
                { key: ['line-movement', activeSport], fn: () => API.lineMovement(activeSport) },
                { key: ['hit-rate-summary', activeSport], fn: () => API.hitRateSummary(activeSport) },
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
