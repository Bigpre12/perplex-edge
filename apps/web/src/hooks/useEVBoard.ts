"use client";
import { useQuery } from '@tanstack/react-query';
import API from '@/lib/api';
import { CanonicalBoardResponse } from './usePropsBoard';

export function useEVBoard(sport = "basketball_nba", minEv?: number) {
    return useQuery<CanonicalBoardResponse, Error>({
        queryKey: ['evBoard', sport, minEv],
        queryFn: async () => {
            const res = await API.evBoard(sport, minEv);
            if (res instanceof Error) throw res;
            if (res?.status === "pipeline_error" || res?.error) {
                throw new Error(res.message || res.error || "Failed to fetch EV board");
            }
            return res as CanonicalBoardResponse;
        },
        refetchInterval: 30000, // 30s auto-refresh
        staleTime: 15000,
    });
}
