"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { SlidersHorizontal } from "lucide-react";

export function SportFilterBar() {
    const pathname = usePathname();
    const router = useRouter();
    const searchParams = useSearchParams();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Filter Logic based on Active Tab
    const isPropsTab = pathname.startsWith("/props");
    const isEVTab = pathname.startsWith("/ev");
    const isSharpTab = pathname.startsWith("/sharp");
    const isLiveTab = pathname.startsWith("/live");

    const activeMarket = searchParams.get("market") || "points";
    const minEdge = searchParams.get("minEdge") || "0";
    const signalType = searchParams.get("signal") || "all";
    const gameStatus = searchParams.get("status") || "all";

    const updateFilter = (key: string, value: string) => {
        const params = new URLSearchParams(searchParams.toString());
        if (value === "all" || value === "0") {
            params.delete(key);
        } else {
            params.set(key, value);
        }
        router.push(`?${params.toString()}`, { scroll: false });
    };

    if (!mounted) return <div className="h-11 bg-lucrix-surface border-b border-lucrix-border hidden md:flex" />;

    // If we're on Home or Settings, we might not need the filter bar, but we can show it globally empty or hide it
    if (pathname === "/" || pathname === "/settings" || pathname === "/kalshi") {
        return null; // Hide on tabs that don't use it to save space, or show empty
    }

    return (
        <div className="sticky top-14 z-40 h-11 bg-lucrix-surface/90 backdrop-blur-md border-b border-lucrix-border flex items-center px-4 sm:px-6 w-full shadow-sm">
            <div className="flex items-center gap-4 text-xs font-medium overflow-x-auto scrollbar-none w-full">
                <div className="flex items-center gap-2 text-textMuted uppercase font-bold tracking-widest px-2 pr-4 border-r border-lucrix-border shrink-0">
                    <SlidersHorizontal size={14} />
                    <span>Filters</span>
                </div>

                {isPropsTab && (
                    <div className="flex items-center gap-1 shrink-0">
                        {['points', 'rebounds', 'assists', 'pra', '3pm', 'strikeouts', 'hits'].map(m => (
                            <button
                                key={m}
                                onClick={() => updateFilter('market', m)}
                                className={`px-3 py-1 rounded-full capitalize transition-colors ${activeMarket === m ? 'bg-lucrix-elevated text-white border border-lucrix-borderBright' : 'text-textSecondary hover:text-white border border-transparent hover:bg-lucrix-dark'}`}
                            >
                                {m}
                            </button>
                        ))}
                    </div>
                )}

                {isEVTab && (
                    <div className="flex items-center gap-4 shrink-0 px-2">
                        <span className="text-textSecondary flex items-center gap-2">
                            Min Edge %
                            <input 
                                type="range" 
                                min="0" max="10" step="0.5" 
                                value={minEdge}
                                aria-label="Minimum Edge Percentage"
                                onChange={(e) => updateFilter('minEdge', e.target.value)}
                                className="w-24 accent-brand-success"
                            />
                            <span className="text-white font-mono w-8">{minEdge}%</span>
                        </span>
                        
                        <select 
                            className="bg-lucrix-dark border border-lucrix-border rounded px-2 py-1 text-textSecondary outline-none min-w-[120px]"
                            aria-label="Select Bookmaker"
                            onChange={(e) => updateFilter('bookmaker', e.target.value)}
                        >
                            <option value="all">All Books</option>
                            <option value="draftkings">DraftKings</option>
                            <option value="fanduel">FanDuel</option>
                            <option value="betmgm">BetMGM</option>
                        </select>
                    </div>
                )}

                {isSharpTab && (
                    <div className="flex items-center gap-1 shrink-0">
                        {['all', 'steam', 'reverse', 'sharp_action'].map(s => (
                            <button
                                key={s}
                                onClick={() => updateFilter('signal', s)}
                                className={`px-3 py-1 rounded-full capitalize transition-colors ${signalType === s ? 'bg-lucrix-elevated text-white border border-lucrix-borderBright' : 'text-textSecondary hover:text-white border border-transparent hover:bg-lucrix-dark'}`}
                            >
                                {s.replace('_', ' ')}
                            </button>
                        ))}
                    </div>
                )}
                
                {isLiveTab && (
                    <div className="flex items-center gap-1 shrink-0">
                        {['all', 'pregame', 'live', 'final'].map(s => (
                            <button
                                key={s}
                                onClick={() => updateFilter('status', s)}
                                className={`px-3 py-1 rounded-full capitalize transition-colors ${gameStatus === s ? 'bg-lucrix-elevated text-white border border-lucrix-borderBright' : 'text-textSecondary hover:text-white border border-transparent hover:bg-lucrix-dark'}`}
                            >
                                {s}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
