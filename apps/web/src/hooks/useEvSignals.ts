"use client";
import { useState, useEffect, useCallback } from "react";
import { useReconnectingWs } from "./useReconnectingWs";
import api, { isApiError } from "@/lib/api";

export type EVSignal = {
    event_id: string;
    sport_key: string;
    player_name: string;
    market_key: string;
    line: number;
    bookmaker: string;
    current_price: number;
    true_prob: number;
    implied_prob: number;
    edge_percent: number;
    confidence_score: number;
    updated_at: string;
};

export function useEvSignals(sport: string, minEv = 2.0) {
    const [signals, setSignals] = useState<EVSignal[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            const res = await api.ev.scanner(sport);
            if (isApiError(res)) throw res;
            
            const raw = res.data || [];
            const mapped = raw.map((s: any) => ({
                event_id: s.id || s.event_id,
                sport_key: s.sport,
                player_name: s.player_name,
                market_key: s.stat_type,
                line: s.line,
                bookmaker: s.book,
                current_price: s.odds,
                true_prob: s.true_prob,
                implied_prob: 1 / s.odds,
                edge_percent: s.ev_percentage,
                confidence_score: s.ev_percentage,
                updated_at: s.updated_at
            }));
            const filtered = mapped.filter((s: any) => s.edge_percent >= minEv);
            setSignals(filtered);
            setError(null);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [sport, minEv]);

    // WebSocket for live updates
    useReconnectingWs(api.wsEv, (message: any) => {
        if (message.type === "ev_signal") {
            const s = message.data;
            const newSignal: EVSignal = {
                event_id: s.id || s.event_id,
                sport_key: s.sport,
                player_name: s.player_name,
                market_key: s.stat_type,
                line: s.line,
                bookmaker: s.book,
                current_price: s.odds,
                true_prob: s.true_prob,
                implied_prob: 1 / s.odds,
                edge_percent: s.ev_percentage,
                confidence_score: s.ev_percentage,
                updated_at: s.updated_at
            };
            
            if (newSignal.sport_key === sport && newSignal.edge_percent >= minEv) {
                setSignals(prev => {
                    const exists = prev.findIndex(p => 
                        p.event_id === newSignal.event_id && 
                        p.market_key === newSignal.market_key && 
                        p.player_name === newSignal.player_name &&
                        p.bookmaker === newSignal.bookmaker
                    );
                    
                    if (exists > -1) {
                        const next = [...prev];
                        next[exists] = newSignal;
                        return next.sort((a, b) => b.edge_percent - a.edge_percent);
                    }
                    
                    return [newSignal, ...prev].sort((a, b) => b.edge_percent - a.edge_percent).slice(0, 50);
                });
            }
        } else if (message.type === "ev_refresh_request") {
            if (message.sport === sport) load();
        }
    });

    useEffect(() => {
        load();
    }, [load]);

    return { signals, loading, error, refetch: load };
}
