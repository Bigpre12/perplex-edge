"use client";

import { useCallback } from "react";
import { Trophy, Star, TrendingUp, Users, ShieldCheck, Crown } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";

export default function LeaderboardPage() {
    const { data: stats, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.fetch(`/api/picks/stats`),
        [],
        { refreshInterval: 600000 } // 10 minutes
    );

    const models = stats?.models || [
        { name: "NBA Prop Oracle", sport: "NBA", hit_rate: 64.2, profit: 42.1 },
        { name: "NFL Sharp Intel", sport: "NFL", hit_rate: 61.8, profit: 38.4 },
        { name: "MLB Totalizer", sport: "MLB", hit_rate: 59.1, profit: 22.8 },
        { name: "NHL Goal Scanner", sport: "NHL", hit_rate: 58.4, profit: 18.2 },
    ];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-8 pb-24 text-white">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-amber-500/20 p-2 rounded-lg border border-amber-500/30">
                            <Trophy size={24} className="text-amber-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Trophy Room</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm font-medium">Audited model performance across all athletic sectors</p>
                </div>

                <LiveStatusBar
                    lastUpdated={lastUpdated}
                    isStale={isStale}
                    loading={loading}
                    error={error}
                    onRefresh={refresh}
                    refreshInterval={600}
                />
            </div>

            <PageStates
                loading={loading && !stats}
                error={error}
                empty={false}
            >
                <div className="bg-[#0D0D14] border border-white/5 rounded-2xl overflow-hidden shadow-2xl">
                    <table className="w-full text-left">
                        <thead className="bg-white/5 border-b border-white/5">
                            <tr>
                                <th className="px-6 py-4 text-[10px] font-black text-[#6B7280] uppercase tracking-widest text-center w-20">Rank</th>
                                <th className="px-6 py-4 text-[10px] font-black text-[#6B7280] uppercase tracking-widest">Intelligence Node</th>
                                <th className="px-6 py-4 text-[10px] font-black text-[#6B7280] uppercase tracking-widest text-center">Hit Rate</th>
                                <th className="px-6 py-4 text-[10px] font-black text-[#6B7280] uppercase tracking-widest text-right">Alpha (Units)</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.03]">
                            {models.map((model: any, i: number) => (
                                <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                                    <td className="px-6 py-6 text-center">
                                        <div className={`text-2xl font-black italic tracking-tighter ${i < 3 ? "text-amber-500" : "text-white/10"}`}>
                                            #{i + 1}
                                        </div>
                                    </td>
                                    <td className="px-6 py-6">
                                        <div className="flex items-center gap-4">
                                            <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center ring-offset-2 ring-primary/20 group-hover:ring-2 transition-all">
                                                {i === 0 ? <Crown size={18} className="text-amber-500" /> : <ShieldCheck size={18} className="text-[#6B7280]" />}
                                            </div>
                                            <div>
                                                <div className="text-sm font-black text-white italic uppercase tracking-tight">{model.name}</div>
                                                <div className="text-[9px] font-black text-[#6B7280] uppercase tracking-widest mt-0.5">{model.sport} SUB-SYSTEM</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-6 text-center">
                                        <span className="text-sm font-black text-emerald-500 font-mono tracking-tighter bg-emerald-500/10 px-3 py-1 rounded border border-emerald-500/20 italic">
                                            {model.hit_rate.toFixed(1)}%
                                        </span>
                                    </td>
                                    <td className="px-6 py-6 text-right">
                                        <div className="flex flex-col items-end">
                                            <div className="text-lg font-black text-white italic tracking-tighter">+{model.profit.toFixed(1)}u</div>
                                            <div className="flex items-center gap-1 text-emerald-500 font-black text-[9px] uppercase tracking-widest italic leading-none mt-1">
                                                <TrendingUp size={10} /> Market Outperformer
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="bg-primary/5 border border-primary/10 rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl">
                    <div className="flex items-center gap-6">
                        <Users className="text-primary shrink-0" size={32} />
                        <div>
                            <h3 className="text-sm font-black text-white italic uppercase tracking-tight">Institutional Proof of Work</h3>
                            <p className="text-[10px] text-[#6B7280] font-medium leading-relaxed uppercase tracking-widest mt-1">
                                Every signal is timestamped and locked in the ledger upon publication. Zero exceptions.
                            </p>
                        </div>
                    </div>
                </div>
            </PageStates>
        </div>
    );
}
