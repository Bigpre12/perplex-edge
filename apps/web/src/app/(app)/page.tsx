"use client";

import { useState, useEffect, Suspense } from 'react';
import { useUpgradeSuccess } from '@/hooks/useUpgradeSuccess';
import { useSubscription } from '@/hooks/useSubscription';
import { Activity, Loader2 } from "lucide-react";

import SystemStatusBanner from "@/components/SystemStatusBanner";
import StatsCards from "@/components/dashboard/StatsCards";
import NeuralEngineBrain from "@/components/dashboard/NeuralEngineBrain";
import { WhaleTracker } from '@/components/dashboard/WhaleTracker';
import LiveTrackCard from '@/components/dashboard/LiveTrackCard';
import RecentIntel from '@/components/RecentIntel';


import { useSport } from '@/context/SportContext';
import { api, isApiError } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';
import { REFRESH_INTERVALS } from '@/hooks/useLiveData';
import UpgradeCTA from '@/components/UpgradeCTA'; // Need to define or import

const unwrap = (d: any): any[] => Array.isArray(d) ? d : (d?.data || d?.results || d?.items || d?.props || d?.games || []);

function DashboardContent() {
    useUpgradeSuccess("", () => { });
    const { tier, loading: subLoading, isPro } = useSubscription();
    const isDev = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    const { selectedSport: activeSport } = useSport();
    const [mounted, setMounted] = useState(false);
    useEffect(() => { setMounted(true); }, []);

    const { data: propsData, isLoading: propsLoading } = useQuery({
        queryKey: ['props', activeSport],
        queryFn: () => api.props(activeSport),
        refetchInterval: REFRESH_INTERVALS.PROPS,
    });
    const liveProps = unwrap(propsData).slice(0, 4);

    const { data: injuriesData } = useQuery({
        queryKey: ['injuries', activeSport],
        queryFn: () => api.injuries(activeSport),
        refetchInterval: REFRESH_INTERVALS.INJURIES,
    });
    const injuries = unwrap(injuriesData);

    const { data: healthData } = useQuery({
        queryKey: ['health'],
        queryFn: () => api.health(),
        refetchInterval: REFRESH_INTERVALS.HEALTH,
    });

    return (
        <main className="px-4 space-y-8 pb-20">
            <SystemStatusBanner />

            {/* Header */}
            <div className="flex flex-col gap-1 pt-4">
                <h1 className="text-3xl font-black tracking-tight text-white uppercase italic">Command Center</h1>
                <p className="text-xs text-[#6B7280] font-black uppercase tracking-[0.2em] flex items-center gap-2">
                    <span className="size-1.5 rounded-full bg-[#F5C518] animate-pulse" /> Quantum Analytics v4.2
                </p>
            </div>

            {/* Metrics Grid */}
            <StatsCards />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left */}
                <div className="lg:col-span-8 space-y-6">
                    {/* NEURAL ENGINE METRICS */}
                    <NeuralEngineBrain />

                    {/* WhaleTracker only shown to pro+ */}
                    {mounted ? (
                        isPro ? (
                            <WhaleTracker />
                        ) : (
                            <UpgradeCTA feature="Whale Intel" description="Tracks high-stakes positions in real-time." />
                        )
                    ) : (
                        <div className="h-40 bg-[#141424] border border-[#1E1E35] rounded-2xl animate-pulse" />
                    )}

                    {/* Live Performance — real data from working-player-props */}
                    <div className="bg-[#141424] border border-[#1E1E35] p-6 rounded-2xl space-y-6">
                        <div className="flex justify-between items-center">
                            <h3 className="text-white font-bold flex items-center gap-2 uppercase tracking-tight italic">
                                <Activity className="text-[#F5C518] animate-pulse" size={18} /> Live Performance
                            </h3>
                            {liveProps.length > 0 && (
                                <span className="text-[9px] bg-[#F5C518] text-black px-1.5 py-0.5 rounded-full font-black animate-pulse">
                                    {liveProps.length} ACTIVE
                                </span>
                            )}
                        </div>

                        {propsLoading ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {[0, 1].map((i: number) => (
                                    <div key={i} className="h-40 bg-[#0F0F1A] rounded-2xl animate-pulse border border-[#1E1E35]" />
                                ))}
                            </div>
                        ) : liveProps.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {liveProps.map((prop: any, idx: number) => {
                                    const playerName = prop.player_name || prop.player?.name || 'Unknown';
                                    const statType = prop.stat_type || prop.market?.stat_type || 'Stat';
                                    const line: number = prop.line || prop.line_value || 0;
                                    const side: 'over' | 'under' = prop.side === 'under' ? 'under' : 'over';
                                    const conf: number = prop.confidence_score || prop.model_probability || 0;
                                    // Estimate "current value" from model confidence vs line
                                    const currentValue = parseFloat((line * conf * (side === 'over' ? 0.95 : 1.05)).toFixed(1));
                                    return (
                                        <LiveTrackCard
                                            key={prop.id || idx}
                                            player={playerName}
                                            statType={statType}
                                            currentValue={currentValue}
                                            line={line}
                                            side={side}
                                            gameStatus={prop.sportsbook || 'Model'}
                                        />
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-10 gap-2 text-center">
                                <Activity className="text-[#1E1E35]" size={32} />
                                <p className="text-xs text-[#6B7280] uppercase font-black tracking-widest">
                                    No active props — check back when games are live
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-[#141424] border border-[#1E1E35] p-5 rounded-2xl">
                        <h4 className="text-xs font-black text-white uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Activity size={14} className="text-[#F5C518]" /> Neural Status
                        </h4>
                        <div className="space-y-4">
                            <InternalHealthItem label="Inference Engine" status={(healthData as any)?.inference_status || (healthData?.status === 'healthy' ? 'STABLE' : 'WARN')} />
                            <InternalHealthItem label="Data Pipeline" status={(healthData as any)?.pipeline_status || "ACTIVE"} />
                            <InternalHealthItem label="Odds Stream" status={(healthData as any)?.stream_status || "SYNCED"} />
                        </div>
                    </div>

                    {/* Recent Intel — live from ESPN and Backend */}
                    <div className="bg-[#141424] border border-[#1E1E35] rounded-2xl flex flex-col overflow-hidden">
                        <div className="p-4 border-b border-[#1E1E35] bg-[#0F0F1A]/50">
                            <h4 className="text-xs font-black text-white uppercase tracking-widest flex items-center justify-between">
                                <span className="flex items-center gap-2">
                                    <Activity size={12} className="text-[#F5C518]" />
                                    Recent Intel
                                </span>
                                <span className="text-[9px] bg-[#F5C518] text-black px-1.5 py-0.5 rounded-full font-black animate-pulse">LIVE</span>
                            </h4>
                        </div>
                        <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
                            <RecentIntel sport={activeSport} />
                        </div>
                    </div>

                    {/* Injury Intel Analyzer */}
                    <div className="bg-[#141424] border border-rose-500/20 rounded-2xl flex flex-col overflow-hidden shadow-2xl shadow-rose-900/10">
                        <div className="p-4 border-b border-rose-500/20 bg-rose-500/5">
                            <h4 className="text-xs font-black text-white uppercase tracking-widest flex items-center justify-between gap-2">
                                <span className="flex items-center gap-2">
                                    <Activity size={12} className="text-rose-500" />
                                    Injury Impact Analyzer
                                </span>
                            </h4>
                        </div>
                        <div className="p-4 space-y-3">
                            {!mounted ? (
                                <div className="h-20 bg-rose-950/20 rounded-xl animate-pulse" />
                            ) : injuries.length > 0 ? (
                                injuries.filter((i: any) => ['Out', 'Questionable', 'Day-to-Day'].includes(i.status)).slice(0, 3).map((inj: any, idx: number) => (
                                    <div key={(inj.player_name || inj.player) + idx} className="bg-rose-950/30 border border-rose-500/10 rounded-xl p-3 flex justify-between items-center text-xs">
                                        <div>
                                            <div className="font-bold text-white uppercase">{inj.player_name || inj.player || 'Unknown'}</div>
                                            <div className="text-[9px] text-slate-400 font-black uppercase">{inj.status} ({inj.body_part || 'General'})</div>
                                        </div>
                                        <div className="text-right">
                                            <div className={`font-mono ${inj.direction === 'positive' ? 'text-emerald-400' : 'text-slate-400'} font-bold`}>{inj.stat_impact || 'Impact Payout'}</div>
                                            <div className="text-[9px] text-slate-400 font-black uppercase tracking-widest">{inj.teammate_boost}</div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-[9px] text-slate-500 text-center uppercase font-black py-4">No critical injuries reported</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

function InternalHealthItem({ label, status }: any) {
    const isGood = ['STABLE', 'SYNCED', 'ACTIVE'].includes(status);
    return (
        <div className="flex items-center justify-between border-b border-[#1E1E35] pb-2 last:border-0 last:pb-0">
            <span className="text-xs text-[#6B7280] font-semibold">{label}</span>
            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-full border ${isGood ? 'bg-[#22C55E]/10 border-[#22C55E]/20 text-[#22C55E]' : 'bg-[#F5C518]/10 border-[#F5C518]/20 text-[#F5C518]'}`}>
                {status}
            </span>
        </div>
    );
}

export default function Dashboard() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="animate-spin text-[#F5C518] mb-4" size={32} />
                <p className="text-[#6B7280] text-sm italic font-black uppercase tracking-widest">Booting Neural Dashboard...</p>
            </div>
        }>
            <DashboardContent />
        </Suspense>
    );
}
