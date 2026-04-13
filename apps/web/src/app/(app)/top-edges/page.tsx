"use client";

import { useState, useCallback } from "react";
import { Zap, Target, Gauge, TrendingUp, Info } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";


export default function TopEdgesPage() {
    const [minEV, setMinEV] = useState(2);
    const { data: edgesData, isLoading: loading, error, dataUpdatedAt, refetch: refresh } = useQuery({
        queryKey: ['top-edges', minEV],
        queryFn: () => api.get(`/api/ev/top?limit=30&min_ev=${minEV}`).then(r => r.data),
        refetchInterval: 180_000,
    });

    const isStale = dataUpdatedAt ? (Date.now() - dataUpdatedAt) > 300_000 : false;
    const lastUpdated = dataUpdatedAt ? new Date(dataUpdatedAt) : null;
    const errorMsg = error ? (error as Error).message : null;

    const props = edgesData?.props || [];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-8 pb-24 text-white">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-yellow-500/20 p-2 rounded-lg border border-yellow-500/30">
                            <Zap size={24} className="text-yellow-500 fill-yellow-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Top Model Edges</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm font-medium">Highest mathematical advantage vs bookmakers</p>
                </div>

                <div className="flex items-center gap-6">
                    <div className="flex flex-col gap-1 items-end">
                        <label className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest">Min Edge %</label>
                        <div className="flex items-center gap-3">
                            <input
                                type="range"
                                min="0"
                                max="15"
                                step="1"
                                value={minEV}
                                aria-label="Minimum edge percentage"
                                onChange={(e) => setMinEV(parseInt(e.target.value))}
                                className="w-32 accent-primary h-1.5 bg-white/5 rounded-full appearance-none cursor-pointer"
                            />
                            <span className="text-xs font-black text-primary font-mono">{minEV}%</span>
                        </div>
                    </div>
                    <LiveStatusBar
                        lastUpdated={lastUpdated}
                        isStale={isStale}
                        loading={loading}
                        error={errorMsg}
                        onRefresh={refresh}
                        refreshInterval={180}
                    />
                </div>
            </div>

            <PageStates
                loading={loading && !edgesData}
                error={errorMsg}
                empty={!loading && props.length === 0}
                emptyMessage={`No edges found above ${minEV}% threshold.`}
            >
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {props.map((prop: any, i: number) => (
                            <div key={i} className="bg-[#0D0D14] border border-white/5 rounded-2xl p-6 shadow-2xl hover:border-primary/30 transition-all group overflow-hidden relative">
                                {/* Grade Badge */}
                                <div className={`absolute -top-1 -right-1 w-12 h-12 flex items-center justify-center font-black italic text-xl transform rotate-12 ${prop.grade === 'A' ? 'bg-emerald-500 text-black' : 'bg-blue-500 text-white'
                                    }`}>
                                    {prop.grade}
                                </div>

                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <div className="text-sm font-black text-white italic tracking-tight">{prop.player_name}</div>
                                        <div className="text-[10px] font-bold text-[#6B7280] uppercase mt-0.5">{prop.team} vs {prop.opponent}</div>
                                    </div>
                                </div>

                                <div className="space-y-4 mb-6">
                                    <div className="flex justify-between items-center bg-white/[0.02] p-3 rounded-xl border border-white/5">
                                        <div className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest">Market</div>
                                        <div className="text-xs font-black text-white italic">{prop.stat_type} {prop.pick.toUpperCase()} {prop.line}</div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-3">
                                        <div className="bg-white/[0.02] p-3 rounded-xl border border-white/5">
                                            <div className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-1">Model Edge</div>
                                            <div className="text-xl font-black text-primary italic">+{prop.ev_percentage}%</div>
                                        </div>
                                        <div className="bg-white/[0.02] p-3 rounded-xl border border-white/5">
                                            <div className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-1">Kelly Crit.</div>
                                            <div className="text-xl font-black text-blue-400 italic">{prop.kelly_pct}%</div>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between pt-4 border-t border-white/5">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-0.5">Best Odds</span>
                                        <span className="text-sm font-black text-white font-mono">{prop.odds > 0 ? `+${prop.odds}` : prop.odds} ({prop.book})</span>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-0.5">Confidence</div>
                                        <div className={`text-[10px] font-black px-2 py-0.5 rounded border uppercase ${prop.confidence === 'HIGH' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' : 'bg-blue-500/10 border-blue-500/20 text-blue-400'
                                            }`}>
                                            {prop.confidence}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
            </PageStates>

            {/* Disclaimer */}
            <div className="flex items-start gap-4 p-6 bg-[#0D0D14] rounded-2xl border border-white/5 max-w-2xl mx-auto">
                <Info size={20} className="text-primary shrink-0 mt-0.5" />
                <div>
                    <h5 className="text-[10px] font-black text-white uppercase tracking-widest mb-1">Audited Model Signals</h5>
                    <p className="text-[10px] font-medium text-[#6B7280] leading-relaxed">
                        These edges are derived from our proprietary Monte Carlo simulation engine. We compare our projected probabilities against current market lines from 20+ sharp and recreational books. Always practice responsible bankroll management using the Kelly Criterion recommendation.
                    </p>
                </div>
            </div>
        </div>
    );
}
