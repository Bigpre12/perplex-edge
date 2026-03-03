"use client";

import { useQuery } from "@tanstack/react-query";
import { Layers, TrendingUp, AlertCircle, ExternalLink } from "lucide-react";

interface Props {
    playerName: string;
    propType: string;
    standardLine: number;
}

export function AltLinesLadder({ playerName, propType, standardLine }: Props) {
    const { data: result, isLoading } = useQuery({
        queryKey: ["alt-lines", playerName, propType, standardLine],
        queryFn: () =>
            fetch(`/api/alt-lines/ladder/${encodeURIComponent(playerName)}/${propType}?standard_line=${standardLine}`)
                .then(r => r.json()),
    });

    const ladder = result?.ladder || [];

    if (isLoading) return <div className="space-y-2 animate-pulse">
        {[1, 2, 3].map(i => <div key={i} className="h-10 bg-gray-900 border border-gray-800 rounded-lg" />)}
    </div>;

    return (
        <div className="bg-gray-950 border border-gray-800 rounded-2xl p-5 space-y-4 shadow-2xl relative overflow-hidden group">
            <div className="absolute -top-12 -right-12 w-32 h-32 bg-indigo-500/5 rounded-full blur-3xl group-hover:bg-indigo-500/10 transition-all duration-700" />

            <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-2">
                    <Layers size={14} className="text-indigo-400" />
                    <h4 className="text-[10px] text-gray-400 uppercase font-black tracking-[0.2em] mb-0">Alt Lines Ladder</h4>
                </div>
                <span className="text-[9px] text-gray-600 font-bold uppercase tracking-widest flex items-center gap-1">
                    <AlertCircle size={10} /> Market Depth
                </span>
            </div>

            <div className="space-y-1.5 relative z-10">
                {ladder.length === 0 && (
                    <p className="text-gray-600 text-[10px] text-center py-4 font-bold uppercase italic">No alternative lines found for this market.</p>
                )}

                {ladder.map((row: any) => (
                    <div
                        key={`${row.line}-${row.bookmaker}`}
                        className={`group/row flex justify-between items-center text-xs px-4 py-2.5 rounded-xl transition-all duration-300 border ${row.is_base
                                ? "bg-indigo-500/10 border-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.1)]"
                                : "bg-gray-900 border-gray-800 hover:border-gray-700"
                            }`}
                    >
                        <div className="flex items-center gap-3">
                            <span className={`font-black text-sm ${row.is_base ? "text-indigo-400" : "text-gray-200"}`}>
                                {row.line}
                            </span>
                            <div className="flex flex-col">
                                <span className="text-[10px] text-gray-400 font-bold group-hover/row:text-gray-200 transition-colors">{row.bookmaker}</span>
                            </div>
                        </div>

                        <div className="flex items-center gap-4">
                            <div className="flex flex-col items-end">
                                <span className={`font-black tracking-tighter ${row.price > 0 ? "text-emerald-400" : "text-gray-400"}`}>
                                    {row.price > 0 ? "+" : ""}{row.price}
                                </span>
                                {row.is_positive_ev && (
                                    <div className="flex items-center gap-1">
                                        <TrendingUp size={10} className="text-emerald-500" />
                                        <span className="text-[9px] font-black text-emerald-500/80">+{(row.ev * 100).toFixed(1)}% EV</span>
                                    </div>
                                )}
                            </div>
                            <button className="opacity-0 group-hover/row:opacity-100 p-1.5 bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-all">
                                <ExternalLink size={12} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="pt-2">
                <p className="text-[9px] text-gray-600 font-medium leading-tight italic">
                    * EV calculation based on player's historical L10 hit rates against the offered line.
                </p>
            </div>
        </div>
    );
}
