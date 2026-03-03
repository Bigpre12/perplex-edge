"use client";

import { useQuery } from "@tanstack/react-query";
import { Zap, ExternalLink, Info } from "lucide-react";

interface Props {
    playerName: string;
    propType: string;
    pick: "over" | "under";
}

export function BestBookBadge({ playerName, propType, pick }: Props) {
    const { data, isLoading } = useQuery({
        queryKey: ["best-book", playerName, propType, pick],
        queryFn: () =>
            fetch(`/api/best-book/${encodeURIComponent(playerName)}/${propType}/${pick}`)
                .then(r => r.json()),
    });

    if (isLoading) return <div className="h-8 w-24 bg-gray-900 animate-pulse rounded-full" />;
    if (!data?.best_book) return null;

    return (
        <div className="group relative flex items-center gap-2 bg-gradient-to-r from-blue-600/20 to-indigo-600/10 border border-blue-500/30 rounded-full px-3 py-1.5 shadow-lg shadow-blue-500/5 transition-all hover:border-blue-500/60 cursor-help">
            <Zap size={12} className="text-blue-400 fill-blue-400 animate-pulse" />
            <div className="flex items-center gap-1.5 ">
                <span className="text-[10px] text-blue-300 font-black uppercase tracking-widest">Best Price</span>
                <div className="h-3 w-px bg-blue-500/30" />
                <span className="text-white text-[11px] font-black">{data.best_book}</span>
                <span className="text-emerald-400 text-[11px] font-black">
                    {data.best_price > 0 ? "+" : ""}{data.best_price}
                </span>
            </div>

            {/* Tooltip on hover */}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-48 bg-gray-900 border border-gray-800 rounded-xl p-3 opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none shadow-2xl z-50">
                <p className="text-[10px] text-gray-400 font-bold uppercase mb-2 border-b border-gray-800 pb-1 flex items-center gap-1">
                    <Info size={10} /> Market Comparison
                </p>
                <div className="space-y-1.5">
                    {data.all_books?.map((b: any, i: number) => (
                        <div key={i} className="flex justify-between items-center text-[10px]">
                            <span className="text-gray-300 font-medium">{b.book}</span>
                            <span className={i === 0 ? "text-emerald-400 font-black" : "text-gray-500"}>
                                {b.price > 0 ? "+" : ""}{b.price}
                            </span>
                        </div>
                    ))}
                </div>
                <div className="absolute top-full left-1/2 -translate-x-1/2 w-2 h-2 bg-gray-900 border-r border-b border-gray-800 rotate-45 -mt-1" />
            </div>

            <button className="ml-1 text-blue-500/50 hover:text-blue-400 transition-colors">
                <ExternalLink size={10} />
            </button>
        </div>
    );
}
