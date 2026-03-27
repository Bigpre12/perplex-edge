"use client";
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface CanonicalProp {
    id: string;
    game_id: string;
    sport: string;
    league: string;
    player_name: string;
    team: string;
    opponent: string;
    start_time: string | null;
    stat_type: string;
    line: number;
    over_odds: number;
    under_odds: number;
    best_book: string;
    books: Array<{ book: string; side: string; odds: number }>;
    implied_probability: number;
    model_probability: number;
    ev_percentage: number;
    confidence: number;
    steam_signal: boolean;
    whale_signal: boolean;
    sharp_conflict: boolean;
    last_updated: string;
}

export interface CanonicalBoardResponse {
    props: CanonicalProp[];
    count: number;
    updated: string;
    fallback?: string;  // "team_markets" when no player props exist
}

export function usePropsBoard(sport = "basketball_nba", minEv?: number) {
    return useQuery<CanonicalBoardResponse, Error>({
        queryKey: ['propsBoard', sport, minEv],
        queryFn: async () => {
            const { data } = await api.get(`/api/props/${sport}`, {
                params: { min_ev: minEv }
            });
            if (data?.status === "pipeline_error" || data?.error) {
                throw new Error(data.message || data.error || "Failed to fetch props board");
            }
            return data as CanonicalBoardResponse;
        },
        refetchInterval: 30000, // 30s auto-refresh
        staleTime: 15000,
    });
}
