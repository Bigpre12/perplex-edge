"use client";
import { useEffect, useState, useRef, useMemo } from "react";
import { useLucrixStore } from "@/store";
import { SPORTS_CONFIG, SportKey } from "@/lib/sports.config";

type TickerItem = { headline: string; sport: string };

function detectSport(headline: string, fallback: string): string {
    const h = headline || "";
    if (/nba|basketball|playoff/i.test(h)) return "NBA";
    if (/nfl|football|super bowl/i.test(h)) return "NFL";
    if (/mlb|baseball/i.test(h)) return "MLB";
    if (/nhl|hockey/i.test(h)) return "NHL";
    return fallback;
}

const SPORT_EMOJI: Record<string, string> = {
    NBA: "🏀",
    NFL: "🏈",
    MLB: "⚾",
    NHL: "🏒",
};

export default function NewsTicker() {
    const activeSport = useLucrixStore((s: any) => s.activeSport) || "basketball_nba";
    const [items, setItems] = useState<TickerItem[]>([]);
    const tickerRef = useRef<HTMLDivElement>(null);

    const sportCfg = SPORTS_CONFIG[activeSport as SportKey] || SPORTS_CONFIG.basketball_nba;
    const sportLabel = sportCfg.label?.toUpperCase() || "NBA";

    const fallbackItems: TickerItem[] = useMemo(
        () => [
            { headline: `${sportLabel} Market Live - Ingesting internal prop data`, sport: sportLabel },
            { headline: `Real-time liquidity scan across ${sportLabel} markets`, sport: sportLabel },
            { headline: "Quantum Engine: Detecting mathematical mispricings", sport: sportLabel },
            { headline: "Monitor sharp movement for late-market edges", sport: sportLabel },
            { headline: `Dynamic ${sportLabel} analysis active`, sport: sportLabel },
            { headline: "Odds pipeline synced with 12 sportsbooks", sport: sportLabel },
            { headline: "Neural model scanning for +EV edges", sport: sportLabel },
        ],
        [sportLabel]
    );

    useEffect(() => {
        let cancelled = false;
        async function fetchHeadlines() {
            try {
                const espnPath = (sportCfg as any).espn_path || "basketball/nba";
                const res = await fetch(
                    `https://site.api.espn.com/apis/site/v2/sports/${espnPath}/news`,
                    { signal: AbortSignal.timeout(5000) }
                );
                if (!res.ok) return;
                const data = await res.json();
                const next: TickerItem[] = (data.articles ?? [])
                    .slice(0, 12)
                    .map((a: any) => {
                        const headline = a.headline as string;
                        return {
                            headline,
                            sport: detectSport(headline, sportLabel),
                        };
                    })
                    .filter((x: TickerItem) => Boolean(x.headline));
                if (!cancelled && next.length > 0) {
                    setItems(next);
                }
            } catch {
                // ESPN fetch failed - fallbacks will be used
            }
        }
        fetchHeadlines();
        const interval = setInterval(fetchHeadlines, 10 * 60_000);
        return () => {
            cancelled = true;
            clearInterval(interval);
        };
    }, [activeSport, sportCfg, sportLabel]);

    const displayItems = items.length > 0 ? items : fallbackItems;

    const badgeLabel = useMemo(() => {
        const set = new Set(displayItems.map((d) => d.sport));
        if (set.size <= 1) return [...set][0] || sportLabel;
        return "MIXED";
    }, [displayItems, sportLabel]);

    useEffect(() => {
        if (tickerRef.current) {
            tickerRef.current.style.setProperty("--ticker-duration", `${displayItems.length * 6}s`);
        }
    }, [displayItems.length]);

    return (
        <div className="w-full bg-[#0a0a14] border-b border-[#1a1a30] overflow-hidden h-9 flex items-center relative z-30 shrink-0">
            <div className="flex items-center w-full h-full">
                <div className="flex-shrink-0 px-4 py-1.5 bg-[#22C55E] text-black text-[10px] font-black tracking-widest uppercase italic z-50 shadow-[4px_0_10px_rgba(0,0,0,0.5)] h-full flex items-center">
                    {badgeLabel} LIVE
                </div>
                <div className="overflow-hidden flex-1 relative h-full flex items-center">
                    <div
                        ref={tickerRef}
                        className="flex whitespace-nowrap animate-ticker will-change-transform"
                    >
                        {[...displayItems, ...displayItems].map((item, i) => (
                            <span
                                key={i}
                                className="inline-flex items-center px-8 text-[11px] font-bold text-slate-300 uppercase tracking-tight"
                            >
                                <span className="mr-2 shrink-0" aria-hidden>
                                    {SPORT_EMOJI[item.sport] || "⚡"}
                                </span>
                                {item.headline}
                                <span className="ml-8 text-[#1E1E35] font-black opacity-50">/</span>
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
