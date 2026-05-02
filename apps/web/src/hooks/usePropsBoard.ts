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
    market_key: string;
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
    recommendation?: {
        side: string;
        tier: string;
        ev: number;
        reason: string;
    };
}

export interface CanonicalBoardResponse {
    props: CanonicalProp[];
    count: number;
    updated: string;
    fallback?: string;  // "team_markets" when no player props exist
}

export function usePropsBoard(sport = "basketball_nba", minEv?: number) {
    const effectiveSport = (!sport || sport === 'all') ? '' : sport;
    return useQuery<CanonicalBoardResponse, Error>({
        queryKey: ['propsBoard', effectiveSport || 'all', minEv],
        queryFn: async () => {
            const url = effectiveSport
                ? `/api/props/live?sport=${effectiveSport}`
                : `/api/props/live`;
            const { data } = await api.get(url);
            
            const raw = Array.isArray(data) ? data : (data?.data || data?.props || []);
            
            // Adapter: Map PropLiveSchema to CanonicalProp
            const props: CanonicalProp[] = raw.map((p: any) => ({
                id: p.id?.toString() || `${p.player_name}_${p.market_key}`,
                game_id: p.game_id,
                sport: p.sport,
                league: p.league || '',
                player_name: p.player_name || 'Matchup',
                team: p.team || p.home_team || 'UNK',
                opponent: p.away_team || 'UNK',
                start_time: p.game_start_time,
                stat_type: p.market_key.replace('_', ' ').replace('player ', '').toUpperCase(),
                market_key: p.market_key,
                line: Number(p.line) || 0,
                over_odds: Number(p.odds_over) || -110,
                under_odds: Number(p.odds_under) || -110,
                best_book: p.book || 'Average',
                books: [{ book: p.book, side: 'over', odds: p.odds_over }, { book: p.book, side: 'under', odds: p.odds_under }],
                implied_probability: p.implied_over || 0,
                model_probability: p.true_prob || p.model_probability || 0,
                ev_percentage: p.ev_percentage || p.edge_percent || 0,
                confidence: p.confidence || 0,
                steam_signal: !!p.steam_signal,
                whale_signal: !!p.whale_signal,
                sharp_conflict: !!p.sharp_conflict,
                last_updated: p.last_updated_at || new Date().toISOString()
            }));

            return {
                props,
                count: props.length,
                updated: new Date().toISOString()
            } as CanonicalBoardResponse;
        },
        refetchInterval: 30000,
        staleTime: 15000,
    });
}
