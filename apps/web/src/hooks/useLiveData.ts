import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { isApiError, unwrap } from "@/lib/api";

interface UseLiveDataOptions {
    refreshInterval?: number; // ms, default 120000
    enabled?: boolean;
}

interface UseLiveDataResult<T> {
    data: T | any[] | null;
    loading: boolean;
    error: string | null;
    lastUpdated: Date | null;
    isStale: boolean;
    refresh: () => void;
}

export const REFRESH_INTERVALS = {
    INJURIES: 300000,      // 5m
    PROPS: 600000,         // 10m
    STATS: 1800000,        // 30m
    HEALTH: 30000,         // 30s
    ACTIVE_MOVES: 120000,  // 2m
    DEFAULT: 120000        // 2m
};

/**
 * useLiveData refactored to use React Query for centralized caching and deduplication.
 * Maintains the same interface for zero-friction project-wide migration.
 */
export function useLiveData<T = any>(
    fetcher: () => Promise<T | any>,
    deps: any[] = [],
    options: UseLiveDataOptions = {}
): UseLiveDataResult<any> {
    const { refreshInterval = REFRESH_INTERVALS.DEFAULT, enabled = true } = options;
    const [mounted, setMounted] = useState(false);
    useEffect(() => { setMounted(true); }, []);

    const {
        data: queryData,
        isLoading,
        error: queryError,
        refetch,
        dataUpdatedAt,
        isStale
    } = useQuery({
        queryKey: deps, // Unique key based on deps
        queryFn: async () => {
            const result = await fetcher();
            if (isApiError(result)) {
                throw new Error((result as any).error);
            }
            return unwrap(result);
        },
        refetchInterval: refreshInterval,
        staleTime: refreshInterval, // 1 minute stale time for smoother tab switching
        enabled: enabled,
    });

    // Hydration guard: Force loading state on first client render to match server
    if (!mounted) {
        return {
            data: null,
            loading: true,
            error: null,
            lastUpdated: null,
            isStale: false,
            refresh: () => { }
        };
    }

    return {
        data: queryData ?? null,
        loading: isLoading,
        error: queryError ? (queryError as Error).message : null,
        lastUpdated: dataUpdatedAt ? new Date(dataUpdatedAt) : null,
        isStale,
        refresh: () => refetch()
    };
}
