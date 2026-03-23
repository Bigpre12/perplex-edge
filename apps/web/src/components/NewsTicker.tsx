"use client";
import { useEffect, useState } from "react";
import { useSport } from "@/context/SportContext";
import { useLiveData } from "@/hooks/useLiveData";
import { SPORTS_CONFIG, SportKey } from "@/lib/sports.config";

/**
 * NewsTicker - Lucrix Edge Market Live Banner
 * Fetches real-time headlines from ESPN and scrolls them at a readable pace.
 */
export default function NewsTicker() {
    const { selectedSport } = useSport(); // Added useSport hook
    const { data: items, loading } = useLiveData<string[]>(
        async () => {
            const sportCfg = SPORTS_CONFIG[selectedSport as SportKey] || SPORTS_CONFIG.basketball_nba;
            const espnPath = (sportCfg as any).espn_path || "basketball/nba";
            const res = await fetch(`https://site.api.espn.com/apis/site/v2/sports/${espnPath}/news`);
            if (res.ok) {
                const data = await res.json();
                const headlines = (data.articles ?? [])
                    .slice(0, 12)
                    .map((a: any) => a.headline)
                    .filter(Boolean);

                if (headlines.length > 0) return headlines;
            }
            throw new Error("Empty headlines");
        },
        ["news_ticker", selectedSport],
        {
            refreshInterval: 10 * 60_000
        }
    );

    const displayItems = (items as string[]) || [
        "9 NBA games today — Mavericks @ Magic 7PM ET",
        "Jazz @ Wizards 7PM ET · Nets @ Heat 7:30PM ET",
        "Warriors @ Rockets 7:30PM ET · Raptors @ Wolves 8PM ET",
        "Lakers @ Nuggets 10PM ET · Pelicans @ Suns 10PM ET",
        "Market Volatility: Monitor sharp alerts for late-move advantage",
        "Quantum Engine: Ingesting live props for tonight's slate"
    ];

    if (loading && displayItems.length === 0) return null;
    if (displayItems.length === 0) return null;

    return (
        <div className="w-full bg-[#080810] border-b border-[#1E1E35] overflow-hidden h-8 flex items-center relative z-40">
            <div className="flex items-center w-full">
                {/* Static label - High Visibility */}
                <div className="flex-shrink-0 px-4 py-1.5 bg-[#22C55E] text-black text-[10px] font-black tracking-widest uppercase italic z-50 shadow-[4px_0_10px_rgba(0,0,0,0.5)]">
                    MARKET LIVE
                </div>

                {/* Scrolling ticker content */}
                <div className="overflow-hidden flex-1 relative h-full flex items-center">
                    <div
                        className="flex whitespace-nowrap animate-ticker will-change-transform"
                        style={{ "--ticker-duration": `${displayItems.length * 8}s` } as React.CSSProperties}
                    >
                        {/* Duplicate for seamless loop */}
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
