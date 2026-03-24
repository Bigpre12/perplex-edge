"use client";
import { useEffect, useRef, useState } from "react";
import { api, API, isApiError } from "@/lib/api";

export interface SteamAlert {
    id?: string;
    player: string;
    stat: string;
    line: number;
    pick: string;
    timestamp: string;
    alert_time?: string;
    movement: string;
    type: "STEAM" | "REVERSE";
    severity: number;
    game: string;
    books_moved: string[];
}

export function useSteamAlerts(sport = "basketball_nba") {
    const [alerts, setAlerts] = useState<SteamAlert[]>([]);
    const seenIds = useRef<Set<string>>(new Set());

    useEffect(() => {
        const poll = async () => {
            try {
                const data = await api.get<any>(API.steamAlerts(sport));
                if (isApiError(data)) return;

                const incoming: SteamAlert[] = Array.isArray(data?.alerts) ? data.alerts : (Array.isArray(data) ? data : []);

                const fresh = incoming.filter(alert => {
                    // Fingerprint = player + stat + line + side + minute bucket
                    // Use alert_time or current time for bucket if timestamp missing
                    const timeToUse = alert.alert_time || alert.timestamp || new Date().toISOString();
                    const minute = timeToUse.slice(0, 16); // "2026-03-06T02:21"
                    const fingerprint = `${alert.player}-${alert.stat}-${alert.line}-${alert.pick}-${minute}`;

                    if (seenIds.current.has(fingerprint)) return false;
                    seenIds.current.add(fingerprint);
                    return true;
                });

                if (fresh.length > 0) {
                    setAlerts(prev => [...fresh, ...prev].slice(0, 20)); // keep last 20
                }
            } catch (e) {
                console.warn("Steam alerts error:", e);
            }
        };

        poll(); // immediate
        const timer = setInterval(poll, 120_000); // 2 minutes recommended
        return () => clearInterval(timer);
    }, [sport]);

    return { alerts, loading: alerts.length === 0 };
}
