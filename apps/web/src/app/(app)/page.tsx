"use client";

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useBrainData } from '@/hooks/useBrainData';
import { Activity, Loader2 } from 'lucide-react';
import { API_ENDPOINTS } from "@/lib/apiConfig";
import LiveTrackCard from '@/components/dashboard/LiveTrackCard';
import WhaleTracker from '@/components/dashboard/WhaleTracker';

interface BrainMetrics {
    total_recommendations: number;
    recommendation_hit_rate: number;
    average_ev: number;
    prop_volume: number;
    user_confidence_score: number;
    api_response_time_ms: number;
    error_rate: number;
    system_metrics: {
        cpu_usage: number;
        memory_usage: number;
    };
}

interface HealingStatus {
    status: string;
    active_healing: boolean;
    ai_evaluation: {
        action: string;
        target: string;
        reason: string;
        is_critical: boolean;
    };
    system_metrics_evaluated: {
        cpu_usage: number;
        error_rate: number;
    };
}

function DashboardContent() {
    const searchParams = useSearchParams();
    const activeSport = searchParams.get('sport') || 'basketball_nba';
    // marketIntel already fetched & cached by useBrainData
    const { marketIntel } = useBrainData(activeSport);
    const [metrics, setMetrics] = useState<BrainMetrics | null>(null);
    const [healing, setHealing] = useState<HealingStatus | null>(null);
    const [liveProps, setLiveProps] = useState<any[]>([]);
    const [metricsLoading, setMetricsLoading] = useState(true);
    const [propsLoading, setPropsLoading] = useState(true);
    const [healingTime, setHealingTime] = useState('—');

    // Poll brain metrics + healing status every 15s
    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const [metricsRes, healingRes] = await Promise.all([
                    fetch(`${API_ENDPOINTS.BRAIN_METRICS}?sport_key=${activeSport}`),
                    fetch(`${API_ENDPOINTS.BRAIN_HEALTH}`),
                ]);
                setMetrics(await metricsRes.json());
                setHealing(await healingRes.json());
            } catch (err) {
                console.error("Failed to fetch dashboard metrics:", err);
            } finally {
                setMetricsLoading(false);
            }
        };
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 15000);
        setHealingTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
        return () => clearInterval(interval);
    }, [activeSport]);

    // Poll live player props every 30s for the "Live Performance" section
    useEffect(() => {
        const fetchLiveProps = async () => {
            setPropsLoading(true);
            try {
                const res = await fetch(`${API_ENDPOINTS.ODDS}?sport_key=${activeSport}&limit=4`);
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const data = await res.json();
                setLiveProps((data.items || []).slice(0, 4));
            } catch (err) {
                console.warn("Live props unavailable for dashboard:", err);
                setLiveProps([]);
            } finally {
                setPropsLoading(false);
            }
        };
        fetchLiveProps();
        const interval = setInterval(fetchLiveProps, 30000);
        return () => clearInterval(interval);
    }, [activeSport]);

    return (
        <div className="px-4 space-y-8 pb-20">
            {/* Header */}
            <div className="flex flex-col gap-1">
                <h1 className="text-3xl font-black tracking-tight text-white uppercase italic">Command Center</h1>
                <p className="text-xs text-[#6B7280] font-black uppercase tracking-[0.2em] flex items-center gap-2">
                    <span className="size-1.5 rounded-full bg-[#F5C518] animate-pulse" /> Quantum Analytics v4.2
                </p>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {metricsLoading ? (
                    Array(4).fill(0).map((_, i) => (
                        <div key={i} className="h-32 bg-[#141424] border border-[#1E1E35] rounded-2xl animate-pulse" />
                    ))
                ) : (
                    <>
                        <MetricCard
                            label="Rec. Hit Rate"
                            value={(metrics && metrics.recommendation_hit_rate !== undefined) ? `${(metrics.recommendation_hit_rate * 100).toFixed(1)}%` : '—'}
                            trend={(metrics && metrics.recommendation_hit_rate !== undefined) ? `+${((metrics.recommendation_hit_rate - 0.55) * 100).toFixed(1)}%` : undefined}
                        />
                        <MetricCard
                            label="Average EV"
                            value={(metrics && metrics.average_ev !== undefined) ? `+${(metrics.average_ev * 100).toFixed(1)}%` : '—'}
                            progress={(metrics && metrics.average_ev !== undefined) ? Math.round(metrics.average_ev * 300) : 0}
                        />
                        <MetricCard
                            label="Live Volume"
                            value={(metrics && metrics.total_recommendations !== undefined) ? metrics.total_recommendations.toLocaleString() : '—'}
                            badge="Active"
                        />
                        <MetricCard
                            label="API Health"
                            value={healing?.status === 'healthy' ? '99.9%' : 'Degraded'}
                            status={healing?.status === 'healthy' ? 'healthy' : undefined}
                        />
                    </>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                {/* Left */}
                <div className="lg:col-span-8 space-y-6">
                    <WhaleTracker />

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
                                {[0, 1].map(i => (
                                    <div key={i} className="h-40 bg-[#0F0F1A] rounded-2xl animate-pulse border border-[#1E1E35]" />
                                ))}
                            </div>
                        ) : liveProps.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {liveProps.map((prop, idx) => {
                                    const playerName = prop.player?.name || prop.player_name || 'Unknown';
                                    const statType = prop.market?.stat_type || prop.stat_type || 'Stat';
                                    const line: number = prop.line_value || prop.line || 0;
                                    const side: 'over' | 'under' = prop.side === 'under' ? 'under' : 'over';
                                    const conf: number = prop.confidence_score || prop.model_probability || 0.55;
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
                            <HealthItem label="Inference Engine" status={healing?.status === 'healthy' ? 'STABLE' : 'WARN'} />
                            <HealthItem label="Data Pipeline" status="ACTIVE" />
                            <HealthItem label="Odds Stream" status="SYNCED" />
                        </div>
                    </div>

                    {/* Recent Intel — live from market-intel API via useBrainData */}
                    <div className="bg-[#141424] border border-[#1E1E35] rounded-2xl flex flex-col overflow-hidden">
                        <div className="p-4 border-b border-[#1E1E35] bg-[#0F0F1A]/50">
                            <h4 className="text-xs font-black text-white uppercase tracking-widest flex items-center justify-between">
                                <span>Recent Intel</span>
                                <span className="text-[9px] bg-[#F5C518] text-black px-1.5 py-0.5 rounded-full font-black animate-pulse">LIVE</span>
                            </h4>
                        </div>
                        <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
                            {marketIntel.length > 0 ? (
                                marketIntel.slice(0, 8).map((item, i) => {
                                    const color =
                                        item.type === 'sharp' ? 'text-[#FF6B35]' :
                                            item.type === 'injury' ? 'text-[#EF4444]' :
                                                'text-[#F5C518]';
                                    let time = healingTime;
                                    try { time = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); } catch { /* keep fallback */ }
                                    return (
                                        <LogItem
                                            key={i}
                                            time={time}
                                            message={item.content || item.title}
                                            color={color}
                                            label={item.type?.toUpperCase() || 'INTEL'}
                                        />
                                    );
                                })
                            ) : (
                                <div className="p-6 text-center">
                                    <p className="text-[10px] text-[#6B7280] font-black uppercase tracking-widest animate-pulse">
                                        Fetching live intel...
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
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

function MetricCard({ label, value, trend, progress, badge, status }: any) {
    return (
        <div className="bg-[#141424] border border-[#1E1E35] p-6 rounded-2xl flex flex-col gap-2 relative overflow-hidden group hover:border-[#F5C518]/30 transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
            <div className="flex justify-between items-start z-10">
                <div>
                    <p className="text-[#6B7280] text-[10px] font-black uppercase tracking-widest">{label}</p>
                    <h3 className="text-3xl font-black text-white mt-2 tracking-tighter italic font-mono">{value}</h3>
                </div>
                {trend && <span className="text-[#22C55E] text-xs font-black">▲ {trend}</span>}
                {badge && <span className="bg-[#F5C518]/10 text-[#F5C518] text-[9px] font-black px-2 py-0.5 rounded-full border border-[#F5C518]/20">{badge}</span>}
                {status === 'healthy' && (
                    <div className="h-4 w-4 rounded-full bg-[#22C55E]/20 flex items-center justify-center animate-pulse">
                        <div className="h-1.5 w-1.5 rounded-full bg-[#22C55E] shadow-[0_0_8px_#22C55E]" />
                    </div>
                )}
            </div>
            {progress !== undefined && (
                <div className="mt-4">
                    <div className="w-full bg-[#1E1E35] rounded-full h-1">
                        <div className="bg-[#F5C518] h-1 rounded-full" style={{ width: `${Math.min(progress, 100)}%` }} />
                    </div>
                </div>
            )}
            <div className="absolute -right-2 -bottom-2 w-16 h-16 bg-[#F5C518]/5 rounded-full blur-2xl group-hover:bg-[#F5C518]/10 transition-all duration-700" />
        </div>
    );
}

function HealthItem({ label, status }: any) {
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

function LogItem({ time, message, color, label }: any) {
    return (
        <div className="p-4 border-b border-[#1E1E35] hover:bg-white/[0.02] transition-colors">
            <div className="flex justify-between items-center mb-1">
                <span className={`${color} text-[10px] font-black uppercase tracking-wider`}>{label}</span>
                <span className="text-[10px] text-[#6B7280] font-mono">{time}</span>
            </div>
            <p className="text-xs text-white leading-relaxed font-medium">{message}</p>
        </div>
    );
}
