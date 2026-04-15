"use client";

import { useQuery } from "@tanstack/react-query";
import { Trophy, TrendingUp, Info } from "lucide-react";
import API, { isApiError } from "@/lib/api";

export function CLVLeaderboard() {
    const { data, isLoading } = useQuery({
        queryKey: ["clv-leaderboard"],
        queryFn: async () => {
            const res = await API.clvLeaderboard();
            if (isApiError(res)) throw new Error(res.message);
            return res;
        },
    });

    if (isLoading) return (
        <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 h-64 animate-pulse flex items-center justify-center">
            <span className="text-gray-600 text-xs font-bold uppercase tracking-widest">Loading Analytics...</span>
        </div>
    );

    if (!data) return null;

    return (
        <div className="bg-gradient-to-br from-gray-900 via-gray-900 to-indigo-950/20 border border-indigo-500/20 rounded-2xl p-6 space-y-5 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-5">
                <Trophy size={80} />
            </div>

            <div className="text-center relative z-10">
                <div className="flex items-center justify-center gap-2 mb-1">
                    <Trophy size={14} className="text-amber-400" />
                    <p className="text-gray-400 text-[10px] font-black uppercase tracking-[0.2em]">Platform Edge Proof</p>
                </div>
                <p className="text-6xl font-black text-white mt-2 leading-none">
                    {data.beat_closing_line_pct}<span className="text-indigo-500 text-4xl">%</span>
                </p>
                <p className="text-indigo-300/80 text-xs font-semibold mt-2">Beat Closing Line</p>
                <div className="flex items-center justify-center gap-1.5 mt-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    <p className="text-gray-500 text-[10px] font-bold uppercase">{data.total_tracked?.toLocaleString()} Picks Verified</p>
                </div>
            </div>

            <div className="space-y-3 relative z-10">
                <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest flex items-center gap-1.5">
                    <TrendingUp size={12} /> Beat-Closing Rate by League
                </p>
                {data.by_sport?.map((s: any) => (
                    <div key={s.sport} className="group cursor-default">
                        <div className="flex justify-between items-center text-xs mb-1.5">
                            <span className="text-gray-400 font-black group-hover:text-white transition-colors uppercase tracking-wider">{s.sport}</span>
                            <span className="text-emerald-400 font-black text-sm">{s.beat_clv_pct}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden border border-gray-700/50">
                            <div
                                className="h-full bg-gradient-to-r from-indigo-600 to-emerald-500 rounded-full transition-all duration-1000 shadow-[0_0_8px_rgba(79,70,229,0.5)]"
                                style={{ width: `${s.beat_clv_pct}%` }}
                            />
                        </div>
                    </div>
                ))}
            </div>

            <div className="pt-2 flex items-center gap-2 border-t border-gray-800/50">
                <Info size={12} className="text-gray-600" />
                <p className="text-[9px] text-gray-600 font-medium leading-tight">
                    CLV tracking measures the difference between our entry line and the final closing market line. Continuous edge is proof of long-term profitability.
                </p>
            </div>
        </div>
    );
}
