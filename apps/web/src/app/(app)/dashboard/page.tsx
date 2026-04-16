"use client";

import { useState, useEffect, Suspense } from 'react';
import { useUpgradeSuccess } from '@/hooks/useUpgradeSuccess';
import { useSubscription } from '@/hooks/useSubscription';
import { Activity, Loader2 } from "lucide-react";
import { ErrorBoundary } from 'react-error-boundary';

import SystemStatusBanner from "@/components/SystemStatusBanner";
import DataDegradationBanner from "@/components/DataDegradationBanner";
import StatsCards from "@/components/dashboard/StatsCards";
import NeuralEngineBrain from "@/components/dashboard/NeuralEngineBrain";
import { WhaleTracker } from '@/components/dashboard/WhaleTracker';
import LiveTrackCard from '@/components/dashboard/LiveTrackCard';
import RecentIntel from '@/components/RecentIntel';

import { useSport } from '@/context/SportContext';
import { api } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';
import { REFRESH_INTERVALS } from '@/hooks/useLiveData';
import UpgradeCTA from '@/components/UpgradeCTA';

const unwrap = (d: any): any[] => {
    if (!d) return [];
    if (Array.isArray(d)) return d;
    return (d?.data || d?.results || d?.items || d?.props || d?.games || []);
};

function FallbackUI({ error }: { error: any }) {
    return (
        <div className="flex flex-col items-center justify-center h-64 gap-4 bg-lucrix-surface border border-white/10 rounded-xl p-8 shadow-xl">
            <p className="text-red-400 font-black uppercase tracking-widest italic">Dashboard failed to load</p>
            <p className="text-textMuted text-[10px] font-medium max-w-md text-center">{error?.message || "Quantum synchronization failure"}</p>
            <button 
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-brand-primary/20 hover:bg-brand-primary/30 border border-brand-primary/40 text-brand-primary rounded-lg text-xs font-black uppercase tracking-widest transition-all"
            >
                Reload Matrix
            </button>
        </div>
    );
}

function DashboardContent() {
    useUpgradeSuccess("", () => { });
    const { tier, loading: subLoading, isPro } = useSubscription();
    const isDev = typeof window !== 'undefined' && 
                 (window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' ||
                  process.env.NEXT_PUBLIC_DEV_MODE === 'true');
    
    const { selectedSport: activeSport } = useSport();
    const sportParam = (!activeSport || activeSport === 'all') ? '' : activeSport;
    const [mounted, setMounted] = useState(false);
    useEffect(() => { setMounted(true); }, []);

    const { data: propsData, isLoading: propsLoading } = useQuery({
        queryKey: ['props', sportParam || 'all'],
        queryFn: () => api.get<any>(sportParam ? `/api/props/graded?sport=${sportParam}` : '/api/props/graded').then((r: any) => r.data),
        refetchInterval: REFRESH_INTERVALS.PROPS,
    });
    const liveProps = unwrap(propsData);

    const { data: injuriesData } = useQuery({
        queryKey: ['injuries', sportParam || 'all'],
        queryFn: () => api.get<any>(sportParam ? `/api/injuries?sport=${sportParam}` : '/api/injuries').then((r: any) => r.data),
        refetchInterval: REFRESH_INTERVALS.INJURIES,
    });
    const injuries = unwrap(injuriesData);

    const { data: healthData } = useQuery({
        queryKey: ['health'],
        queryFn: () => api.get<any>('/api/health').then((r: any) => r.data),
        refetchInterval: REFRESH_INTERVALS.HEALTH,
    });

    return (
        <main className="space-y-6 pb-20">
            <SystemStatusBanner />
            <DataDegradationBanner />

            {/* Header */}
            <div className="flex flex-col gap-1 pt-2">
                <h1 className="text-3xl font-black tracking-tight text-white uppercase font-display italic">Command Center</h1>
                <p className="text-[10px] text-textMuted font-black uppercase tracking-[0.2em] flex items-center gap-2">
                    <span className="size-1.5 rounded-full bg-brand-cyan animate-pulse shadow-glow shadow-brand-cyan/50" /> Quantum Analytics v4.2
                </p>
            </div>

            {/* Metrics Grid */}
            <StatsCards />

            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
                {/* Left */}
                <div className="xl:col-span-8 space-y-6">
                    {/* NEURAL ENGINE METRICS */}
                    <NeuralEngineBrain />

                    {/* WhaleTracker only shown to pro+ */}
                    {mounted ? (
                        <WhaleTracker />
                    ) : (
                        <div className="h-40 bg-lucrix-surface border border-lucrix-border rounded-xl animate-pulse" />
                    )}

                    {/* Live Performance */}
                    <div className="bg-lucrix-surface border border-lucrix-border p-6 rounded-xl shadow-card">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-white font-bold flex items-center gap-2 uppercase tracking-tight font-display">
                                <Activity className="text-brand-purple animate-pulse" size={18} /> Live Performance
                            </h3>
                            {liveProps?.length > 0 && (
                                <span className="text-[9px] bg-brand-purple/20 text-brand-purple px-2 py-0.5 rounded-sm font-black animate-pulse border border-brand-purple/30">
                                    {liveProps.length} ACTIVE
                                </span>
                            )}
                        </div>

                        {propsLoading ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {[0, 1].map((i: number) => (
                                    <div key={i} className="h-40 bg-lucrix-dark rounded-xl animate-pulse border border-lucrix-border" />
                                ))}
                            </div>
                        ) : liveProps?.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {liveProps.map((prop: any, idx: number) => {
                                    const playerName = prop?.player_name || prop?.player?.name || 'Unknown';
                                    const statType = prop?.stat_type || prop?.market?.stat_type || 'Stat';
                                    const line: number = prop?.line || prop?.line_value || 0;
                                    const side: 'over' | 'under' = prop?.side === 'under' ? 'under' : 'over';
                                    const conf: number = prop?.confidence_score || prop?.model_score || prop?.model_probability || 0;
                                    const currentValue = parseFloat((line * (conf > 1 ? conf/100 : conf) * (side === 'over' ? 0.95 : 1.05)).toFixed(1));
                                    return (
                                        <LiveTrackCard
                                            key={prop?.id || idx}
                                            player={playerName}
                                            statType={statType}
                                            currentValue={currentValue}
                                            line={line}
                                            side={side}
                                            gameStatus={prop?.sportsbook || 'Model'}
                                            confidence={conf > 1 ? conf/100 : conf}
                                        />
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-12 gap-3 text-center bg-lucrix-dark/50 rounded-lg border border-lucrix-border/50">
                                <Activity className="text-textMuted" size={32} />
                                <p className="text-xs text-textSecondary uppercase font-black tracking-widest">
                                    No active props — check back when games are live
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right */}
                <div className="xl:col-span-4 space-y-6">
                    {/* Neural Status */}
                    <div className="bg-lucrix-surface border border-lucrix-border p-5 rounded-xl shadow-card">
                        <h4 className="text-xs font-black text-white uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Activity size={14} className="text-brand-success" /> Neural Status
                        </h4>
                        <div className="space-y-4">
                            <InternalHealthItem label="Inference Engine" status={(healthData as any)?.inference_status || "IDLE"} />
                            <InternalHealthItem label="Data Pipeline" status={(healthData as any)?.pipeline_status || "IDLE"} />
                            <InternalHealthItem 
                                label="Odds Stream" 
                                status={((healthData as any)?.odds_stream || "SYNCED") === "STALE" ? "DEGRADED" : ((healthData as any)?.odds_stream || "SYNCED")} 
                            />
                            <div className="pt-2 border-t border-lucrix-border/50">
                                <div className="flex justify-between items-center text-[8px] font-black uppercase tracking-widest text-textMuted italic">
                                    <span>Last Matrix Sync</span>
                                    <span>{healthData?.last_updated ? new Date(healthData.last_updated).toLocaleTimeString() : 'JUST NOW'}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Recent Intel */}
                    <div className="bg-lucrix-surface border border-lucrix-border rounded-xl flex flex-col overflow-hidden shadow-card">
                        <div className="p-4 border-b border-lucrix-border bg-lucrix-dark/50">
                            <h4 className="text-[10px] font-black text-textSecondary uppercase tracking-widest flex items-center justify-between">
                                <span className="flex items-center gap-2">
                                    <Activity size={12} className="text-brand-cyan" />
                                    Recent Intel Log
                                </span>
                                <span className="text-[9px] bg-brand-cyan/20 text-brand-cyan border border-brand-cyan/30 px-1.5 py-0.5 rounded-sm font-black animate-pulse">LIVE</span>
                            </h4>
                        </div>
                        <div className="max-h-[300px] overflow-y-auto scrollbar-none">
                            <RecentIntel sport={activeSport} />
                        </div>
                    </div>

                    {/* Injury Intel Analyzer */}
                    <div className="bg-lucrix-surface border border-brand-danger/30 rounded-xl flex flex-col overflow-hidden shadow-glow shadow-brand-danger/10">
                        <div className="p-4 border-b border-brand-danger/20 bg-brand-danger/5">
                            <h4 className="text-[10px] font-black text-textSecondary uppercase tracking-widest flex items-center justify-between gap-2">
                                <span className="flex items-center gap-2">
                                    <Activity size={12} className="text-brand-danger" />
                                    Injury Impact Analyzer
                                </span>
                            </h4>
                        </div>
                        <div className="p-4 space-y-3">
                            {!mounted ? (
                                <div className="h-20 bg-brand-danger/10 rounded-lg animate-pulse" />
                            ) : injuries?.length > 0 ? (
                                injuries.filter((i: any) => ['Out', 'Questionable', 'Day-to-Day'].includes(i?.status)).slice(0, 3).map((inj: any, idx: number) => (
                                    <div key={(inj?.player_name || inj?.player || 'Unknown') + idx} className="bg-brand-danger/5 border border-brand-danger/10 rounded-lg p-3 flex justify-between items-center text-xs transition-colors hover:bg-brand-danger/10">
                                        <div>
                                            <div className="font-bold text-white uppercase">{inj?.player_name || inj?.player || 'Unknown'}</div>
                                            <div className="text-[9px] text-brand-danger/80 font-black uppercase">{inj?.status} <span className="text-textMuted font-mono">({inj?.body_part || 'General'})</span></div>
                                        </div>
                                        <div className="text-right">
                                            <div className={`font-mono text-[10px] ${inj?.direction === 'positive' ? 'text-brand-success' : 'text-textSecondary'} font-bold`}>{inj?.stat_impact || 'Impact Payout'}</div>
                                            <div className="text-[9px] text-textMuted font-black uppercase tracking-widest">{inj?.teammate_boost}</div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <p className="text-[9px] text-textMuted text-center uppercase font-black py-4">Awaiting injury sync</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

function InternalHealthItem({ label, status }: any) {
    const isGood = ['STABLE', 'SYNCED', 'ACTIVE', 'HEALTHY', 'CONNECTED'].includes(String(status).toUpperCase());
    return (
        <div className="flex items-center justify-between border-b border-lucrix-border pb-2 last:border-0 last:pb-0">
            <span className="text-xs text-textSecondary font-semibold">{label}</span>
            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-sm border ${isGood ? 'bg-brand-success/10 border-brand-success/20 text-brand-success' : 'bg-brand-warning/10 border-brand-warning/20 text-brand-warning'}`}>
                {status}
            </span>
        </div>
    );
}

export default function Dashboard() {
    return (
        <ErrorBoundary FallbackComponent={FallbackUI}>
            <Suspense fallback={
                <div className="flex flex-col items-center justify-center py-24">
                    <Loader2 className="animate-spin text-brand-cyan mb-4" size={32} />
                    <p className="text-textMuted text-[10px] font-black uppercase tracking-widest">Booting Neural Dashboard...</p>
                </div>
            }>
                <DashboardContent />
            </Suspense>
        </ErrorBoundary>
    );
}
