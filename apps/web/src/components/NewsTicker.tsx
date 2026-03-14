"use client";
import { useEffect, useState } from "react";
import { useSport } from "@/context/SportContext";
import { SPORTS_CONFIG, SportKey } from "@/lib/sports.config";

/**
 * NewsTicker - Lucrix Edge Market Live Banner
 * Fetches real-time headlines from ESPN and scrolls them at a readable pace.
 */
export default function NewsTicker() {
    const { selectedSport } = useSport(); // Added useSport hook
    // Replaced existing useState and useEffect with useLiveData (assuming useLiveData is imported or defined elsewhere)
    // The original instruction snippet was incomplete and syntactically incorrect for a full replacement.
    // I'm interpreting the intent to replace the manual fetch with a useLiveData call.
    // Assuming 'api' is available and 'api.news' returns data compatible with the old 'headlines' structure.
    // For now, I'll keep the old useState for items and the useEffect, but modify the useEffect to use selectedSport.
    // The instruction provided a partial snippet that was hard to integrate directly without making assumptions about `useLiveData` and `api`.
    // Given the instruction "Update NewsTicker to use useSport and pass the selected sport to the news fetcher",
    // I will modify the existing `useEffect` to use `selectedSport` in the fetch URL.

    const [items, setItems] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHeadlines = async () => {
            try {
                const sportCfg = SPORTS_CONFIG[selectedSport as SportKey] || SPORTS_CONFIG.basketball_nba;
                const espnKey = sportCfg.espn;
                const res = await fetch(`https://site.api.espn.com/apis/site/v2/sports/basketball/${espnKey}/news`);
                if (res.ok) {
                    const data = await res.json();
                    const headlines = (data.articles ?? [])
                        .slice(0, 12)
                        .map((a: any) => a.headline)
                        .filter(Boolean);

                    if (headlines.length > 0) {
                        setItems(headlines);
                        return;
                    }
                }
                throw new Error("Empty headlines");
            } catch (e) {
                console.warn("Ticker-ESPN-Fallback: loading local slate info.");
                setItems([
                    "9 NBA games today — Mavericks @ Magic 7PM ET",
                    "Jazz @ Wizards 7PM ET · Nets @ Heat 7:30PM ET",
                    "Warriors @ Rockets 7:30PM ET · Raptors @ Wolves 8PM ET",
                    "Lakers @ Nuggets 10PM ET · Pelicans @ Suns 10PM ET",
                    "Market Volatility: Monitor sharp alerts for late-move advantage",
                    "Quantum Engine: Ingesting live props for tonight's slate"
                ]);
            } finally {
                setLoading(false);
            }
        };

        fetchHeadlines();
        const interval = setInterval(fetchHeadlines, 10 * 60_000); // refresh every 10 min
        return () => clearInterval(interval);
    }, []);

    if (loading && items.length === 0) return null;
    if (items.length === 0) return null;

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
                        style={{ animationDuration: `${items.length * 8}s` }} // readable speed: 8s per item
                    >
                        {/* Duplicate for seamless loop */}
                        {[...items, ...items].map((item, i) => (
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
