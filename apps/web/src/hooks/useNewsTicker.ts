"use client";
import { useState, useEffect, useRef } from "react";
import { API, apiFetch, isApiError } from "@/lib/api";
import { useBackendStatus } from "./useBackendStatus";
import { SportKey } from "@/lib/sports.config";

export interface TickerItem {
    id: string;
    sport: string;
    tag: string;
    icon: string;
    headline: string;
    description: string;
    published: string;
    link: string;
    is_injury: boolean;
    is_lineup: boolean;
}

export function useNewsTicker(sports: string = "NBA,NFL,MLB", refreshMs: number = 60000) {
    const [items, setItems] = useState<TickerItem[]>([]);
    const [loading, setLoading] = useState(true);
    const intervalRef = useRef<NodeJS.Timeout | null>(null);
    const { isDown } = useBackendStatus();

    const fetchTicker = async () => {
        if (isDown) return;
        const result = await apiFetch<any>(API.news((sports.split(',')[0].toLowerCase() === 'nba' ? 'basketball_nba' : 'basketball_nba') as SportKey));

        if (!isApiError(result)) {
            setItems(result.items || result.data || []);
        } else {
            console.warn("[Ticker] fetch failed:", result.message);
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchTicker();
        // Auto-refresh the ticker items
        intervalRef.current = setInterval(() => {
            if (!isDown) fetchTicker();
        }, refreshMs);

        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, [sports, refreshMs, isDown]);

    return { items, loading };
}
