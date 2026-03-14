// apps/web/src/hooks/useEvSignals.ts
import { useState, useEffect, useCallback } from "react";
import { API } from "@/lib/api";

export type EVSignal = {
    event_id: string;
    market: string;
    selection: string;
    book: string;
    odds: number;
    true_prob: number;
    edge: number;
    updated_at: string;
};

export function useEvSignals(sport: string, minEv = 2.0) {
    const [signals, setSignals] = useState<EVSignal[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/ev/unified/top?sport=${sport}&min_ev=${minEv}`);
            if (!res.ok) throw new Error("Failed to load EV signals");
            const data = await res.json();
            setSignals(data.signals || []);
            setError(null);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [sport, minEv]);

    useEffect(() => {
        load();
    }, [load]);

    return { signals, loading, error, refetch: load };
}
