"use client";
import { useEffect, useState, useRef } from "react";
import { useLucrixStore } from "@/store";
import { SPORTS_CONFIG, SportKey } from "@/lib/sports.config";

export default function NewsTicker() {
    const activeSport = useLucrixStore((s: any) => s.activeSport) || "basketball_nba";
    const [headlines, setHeadlines] = useState<string[]>([]);
    const tickerRef = useRef<HTMLDivElement>(null);

    const sportCfg = SPORTS_CONFIG[activeSport as SportKey] || SPORTS_CONFIG.basketball_nba;
    const sportLabel = sportCfg.label?.toUpperCase() || "NBA";

    const fallbackHeadlines = [
        `${sportLabel} Market Live - Ingesting internal prop data`,
        `Real-time liquidity scan across ${sportLabel} markets`,
        "Quantum Engine: Detecting mathematical mispricings",
        "Monitor sharp movement for late-market edges",
        `Dynamic ${sportLabel} analysis active`,
        "Odds pipeline synced with 12 sportsbooks",
        "Neural model scanning for +EV edges",
    ];

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
                const items = (data.articles ?? [])
                    .slice(0, 12)
                    .map((a: any) => a.headline)
                    .filter(Boolean);
                if (!cancelled && items.length > 0) {
                    setHeadlines(items);
                }
            } catch {
                // ESPN fetch failed - fallbacks will be used
            }
        }
        fetchHeadlines();
        const interval = setInterval(fetchHeadlines, 10 * 60_000);
        return () => { cancelled = true; clearInterval(interval); };
    }, [activeSport, sportCfg]);

    const displayItems = headlines.length > 0 ? headlines : fallbackHeadlines;

    useEffect(() => {
        if (tickerRef.current) {
            tickerRef.current.style.setProperty("--ticker-duration", `${displayItems.length * 6}s`);
        }
    }, [displayItems.length]);

    return (
        <div className="w-full bg-[#0a0a14] border-b border-[#1a1a30] overflow-hidden h-9 flex items-center relative z-30 shrink-0">
            <div className="flex items-center w-full h-full">
                <div className="flex-shrink-0 px-4 py-1.5 bg-[#22C55E] text-black text-[10px] font-black tracking-widest uppercase italic z-50 shadow-[4px_0_10px_rgba(0,0,0,0.5)] h-full flex items-center">
                    {sportLabel} LIVE
                </div>
                <div className="overflow-hidden flex-1 relative h-full flex items-center">
                    <div
                        ref={tickerRef}
                        className="flex whitespace-nowrap animate-ticker will-change-transform"
                    >
                        {[...displayItems, ...displayItems].map((item, i) => (
                            <span key={i} className="inline-flex items-center px-8 text-[11px] font-bold text-slate-300 uppercase tracking-tight">
                                {item}
                                <span className="ml-8 text-[#1E1E35] font-black opacity-50">/</span>
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
