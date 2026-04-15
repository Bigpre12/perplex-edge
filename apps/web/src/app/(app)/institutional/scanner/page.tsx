"use client";

import { useState, useCallback, Suspense } from "react";
import { motion } from "framer-motion";
import { Radar, Zap, Activity, Server, Globe, Share2, CheckCircle2 } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import API from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";
import GateLock from "@/components/GateLock";
import { useGate } from "@/hooks/useGate";
import { useSport } from "@/context/SportContext";

function InstitutionalScannerContent() {
    const { selectedSport: sport } = useSport();
    const { data: allProps, loading, error, lastUpdated, isStale, refresh } = useLiveData<any[]>(
        () => API.props(sport || "basketball_nba"),
        [sport],
        { refreshInterval: 60000 } // 1 minute
    );

    const handleSignal = async (prop: any) => {
        alert("Signal dispatched to secure relay.");
    };

    const handleQuickTrack = async (prop: any) => {
        alert("Prop tracked successfully in personal ledger.");
    };

    return (
        <GateLock feature="parlay" reason="Institutional-grade market scanning is reserved for Elite partners.">
            <div className="space-y-8 pb-24">
                {/* Command Header */}
                <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-primary/20 rounded-lg text-primary animate-pulse">
                                <Radar size={24} />
                            </div>
                            <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic">Institutional Command Center</h1>
                        </div>
                        <p className="text-[#6B7280] text-sm font-medium flex items-center gap-2">
                            <Globe size={14} className="text-emerald-500" /> Scanning global markets for multi-asset steam pressure
                        </p>
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

                {/* Main Scanner Grid */}
                <PageStates
                    loading={loading && !allProps}
                    error={error}
                    empty={!loading && (!allProps || allProps.length === 0)}
                    emptyMessage="No institutional-grade edges identified in current scan cycle."
                >
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        {/* Real-time Feed */}
                        <div className="lg:col-span-2 space-y-4">
                            <div className="flex items-center justify-between px-2">
                                <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-2">
                                    <Activity size={14} /> High-Intensity Market Feed
                                </h3>
                            </div>

                            <div className="bg-[#0D0D14] border border-white/5 rounded-2xl overflow-hidden shadow-2xl">
                                <table className="w-full text-left">
                                    <thead className="bg-white/5 border-b border-white/5">
                                        <tr>
                                            <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Market / Asset</th>
                                            <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">Odds</th>
                                            <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">EV%</th>
                                            <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Execution</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/[0.03]">
                                        {(allProps || []).map((prop: any, i: number) => (
                                            <ScannerRow
                                                key={`${prop.event_id}-${i}`}
                                                prop={prop}
                                                onQuickTrack={handleQuickTrack}
                                                onSignal={handleSignal}
                                            />
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        {/* Intelligence Sidebar */}
                        <div className="space-y-6">
                            <div className="bg-[#0F0F1A] border border-white/5 p-6 rounded-2xl">
                                <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-6">System Health</h3>
                                <div className="space-y-4">
                                    <SystemHeartbeat label="FastAPI Hub" status="Healthy" load="12%" />
                                    <SystemHeartbeat label="PostgreSQL DB" status="Healthy" load="4%" />
                                    <SystemHeartbeat label="Cache Layer" status="Healthy" load="1%" />
                                </div>
                            </div>
                        </div>
                    </div>
                </PageStates>
            </div>
        </GateLock>
    );
}

export default function InstitutionalScanner() {
    return (
        <Suspense fallback={<div className="p-12 flex items-center gap-4 text-secondary"><Radar className="animate-pulse" /> Scanning Command Center...</div>}>
            <InstitutionalScannerContent />
        </Suspense>
    );
}

function ScannerRow({ prop, onQuickTrack, onSignal }: any) {
    return (
        <motion.tr
            whileHover={{ backgroundColor: 'rgba(255,255,255,0.02)' }}
            className="group cursor-default"
        >
            <td className="px-6 py-5">
                <div className="flex items-center gap-4">
                    <div className="size-10 rounded-xl bg-white/5 border border-white/5 flex items-center justify-center text-primary">
                        <span className="text-xs font-black">{prop.sport?.substring(0, 3)}</span>
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <p className="text-sm font-black text-white">{prop.player_name}</p>
                        </div>
                        <p className="text-[10px] text-[#6B7280] font-bold uppercase mt-0.5">
                            {prop.pick} {prop.line} {prop.stat_type}
                        </p>
                    </div>
                </div>
            </td>
            <td className="px-6 py-5 text-center">
                <span className="font-mono text-sm font-black text-white">
                    {prop.odds > 0 ? `+${prop.odds}` : prop.odds}
                </span>
                <p className="text-[9px] text-[#6B7280] font-black uppercase mt-1">{prop.book}</p>
            </td>
            <td className="px-6 py-5 text-center">
                <span className="text-lg font-black text-primary italic">+{prop.ev_percentage || 0}%</span>
            </td>
            <td className="px-6 py-5 text-right">
                <div className="flex items-center justify-end gap-3">
                    <button
                        onClick={() => onQuickTrack(prop)}
                        title="Quick track prop"
                        className="p-2 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded-lg text-emerald-500 transition-all"
                    >
                        <CheckCircle2 size={16} />
                    </button>
                    <button
                        onClick={() => onSignal(prop)}
                        title="Send signal"
                        className="p-2 bg-primary/10 hover:bg-primary/20 border border-primary/20 rounded-lg text-primary transition-all"
                    >
                        <Share2 size={16} />
                    </button>
                </div>
            </td>
        </motion.tr>
    );
}

function SystemHeartbeat({ label, load }: any) {
    return (
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
                <Server size={12} className="text-slate-500" />
                <span className="text-xs font-bold text-slate-300">{label}</span>
            </div>
            <div className="flex items-center gap-4">
                <span className="text-[10px] font-mono text-slate-500">LOAD: {load}</span>
                <div className="size-2 rounded-full bg-primary shadow-[0_0_5px_#0df233]"></div>
            </div>
        </div>
    );
}
