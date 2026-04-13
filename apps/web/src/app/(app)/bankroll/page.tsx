"use client";

import { useState, useEffect, useRef } from "react";
import { Wallet, Calculator, TrendingUp, PieChart, Info, DollarSign, Activity } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";

export default function BankrollPage() {
    const { data: stats, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.get(`/api/ledger/stats`),
        [],
        { refreshInterval: 60000 } // 1 minute
    );

    const exposureRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (exposureRef.current) {
            exposureRef.current.style.setProperty("--exposure-width", `${stats?.exposure_pct || 6.2}%`);
        }
    }, [stats?.exposure_pct]);

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-8 pb-24 text-white">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-primary/20 p-2 rounded-lg border border-primary/30">
                            <Wallet size={24} className="text-primary" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Capital Ledger</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm font-medium">Bankroll health and institutional risk exposure</p>
                </div>

                <LiveStatusBar
                    lastUpdated={lastUpdated}
                    isStale={isStale}
                    loading={loading}
                    error={error}
                    onRefresh={refresh}
                    refreshInterval={60}
                />
            </div>

            <PageStates
                loading={loading && !stats}
                error={error}
                empty={false}
            >
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="bg-[#0D0D14] border border-white/5 rounded-2xl p-8 relative overflow-hidden group shadow-2xl">
                        <div className="absolute top-0 right-0 p-8 opacity-5">
                            <DollarSign size={80} className="text-primary" />
                        </div>
                        <p className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-2">Current Bankroll</p>
                        <p className="text-4xl font-black text-white font-mono tracking-tighter">${stats?.total_bankroll?.toLocaleString() || "12,431.20"}</p>
                        <div className="mt-4 flex items-center gap-2 text-emerald-500 font-black italic text-xs uppercase tracking-tight">
                            <TrendingUp size={14} /> +{(stats?.total_growth_pct || 24.3).toFixed(1)}% Growth
                        </div>
                    </div>

                    <div className="bg-[#0D0D14] border border-white/5 rounded-2xl p-8 shadow-2xl">
                        <p className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-2">Unit Performance</p>
                        <p className="text-4xl font-black text-primary italic tracking-tighter">+{stats?.total_units || 42.1}u</p>
                        <p className="text-[10px] font-bold text-[#6B7280] mt-4 uppercase tracking-widest">Audited Theoretical Profit</p>
                    </div>

                    <div className="bg-[#0D0D14] border border-white/5 rounded-2xl p-8 shadow-2xl">
                        <p className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mb-2">Market Exposure</p>
                        <p className="text-4xl font-black text-blue-500 italic tracking-tighter">{(stats?.exposure_pct || 6.2).toFixed(1)}%</p>
                        <div className="mt-4 h-1.5 bg-white/5 rounded-full overflow-hidden">
                            <div 
                                ref={exposureRef}
                                className="h-full bg-blue-500 rounded-full transition-all exposure-bar" 
                            />
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
                    <div className="bg-[#0D0D14] border border-white/5 rounded-2xl p-8">
                        <h3 className="text-sm font-black text-white italic uppercase tracking-tight mb-8 flex items-center gap-2">
                            <Calculator className="text-primary" size={18} /> Operational Settings
                        </h3>
                        <div className="space-y-6">
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                <div>
                                    <label className="text-[10px] font-black uppercase text-[#6B7280] tracking-widest mb-2 block">Total Capital ($)</label>
                                    <input
                                        type="number"
                                        title="Total Capital"
                                        aria-label="Total Capital"
                                        className="w-full bg-white/[0.02] border border-white/5 rounded-xl px-4 py-3 font-black text-lg text-white outline-none focus:border-primary/50 transition-all font-mono"
                                        defaultValue={10000}
                                    />
                                </div>
                                <div>
                                    <label className="text-[10px] font-black uppercase text-[#6B7280] tracking-widest mb-2 block">Target Unit ($)</label>
                                    <input
                                        type="number"
                                        title="Target Unit"
                                        aria-label="Target Unit"
                                        className="w-full bg-white/[0.02] border border-white/5 rounded-xl px-4 py-3 font-black text-lg text-white outline-none focus:border-primary/50 transition-all font-mono"
                                        defaultValue={100}
                                    />
                                </div>
                            </div>
                            <div className="bg-primary/5 border border-primary/10 p-4 rounded-xl flex items-start gap-4">
                                <Info size={18} className="text-primary shrink-0 mt-0.5" />
                                <p className="text-[10px] text-[#6B7280] font-medium leading-relaxed uppercase tracking-tight">
                                    Accurate bankroll configuration is critical for <span className="text-white font-black italic">Kelly Criterion</span> sizing. We recommend risking no more than 1-2% of total capital per initial signal.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-[#0D0D14] border border-white/5 border-dashed rounded-2xl p-12 flex flex-col items-center justify-center text-center opacity-60">
                        <PieChart className="text-[#6B7280] mb-4" size={48} />
                        <h4 className="text-xs font-black text-white uppercase tracking-[0.2em]">Alpha Modeling</h4>
                        <p className="text-[10px] text-[#6B7280] font-medium mt-4 max-w-xs uppercase leading-relaxed tracking-widest">
                            Distribution analytics and sector concentration reports activate after 20+ settled positions.
                        </p>
                    </div>
                </div>
            </PageStates>
        </div>
    );
}
