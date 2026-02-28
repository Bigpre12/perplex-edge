"use client";

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useBrainData } from '@/hooks/useBrainData';
import { Database, MemoryStick as Memory, Globe, Activity, Brain, Loader2, Target, TrendingUp, Zap, BarChart3, Fingerprint } from 'lucide-react';
import { API_ENDPOINTS, API_BASE_URL } from "@/lib/apiConfig";
import LiveTrackCard from '@/components/dashboard/LiveTrackCard';
import WhaleTracker from '@/components/dashboard/WhaleTracker';
import LiveMiddlesCard from '@/components/dashboard/LiveMiddlesCard';

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
    const { decisions, loading } = useBrainData(activeSport);
    const [metrics, setMetrics] = useState<BrainMetrics | null>(null);
    const [healing, setHealing] = useState<HealingStatus | null>(null);
    const [liveMiddles, setLiveMiddles] = useState<any[]>([]);
    const [metricsLoading, setMetricsLoading] = useState(true);
    const [healingTime, setHealingTime] = useState('—');

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const [metricsRes, healingRes, middlesRes] = await Promise.all([
                    fetch(`${API_ENDPOINTS.BRAIN_METRICS}?sport_key=${activeSport}`),
                    fetch(`${API_ENDPOINTS.BRAIN_HEALTH}`),
                    fetch(`${API_BASE_URL}/api/immediate/middles?sport_key=${activeSport}`).catch(() => null)
                ]);
                const metricsData = await metricsRes.json();
                const healingData = await healingRes.json();

                let middlesData = { items: [] };
                if (middlesRes && middlesRes.ok) {
                    middlesData = await middlesRes.json();
                }

                setMetrics(metricsData);
                setHealing(healingData);
                setLiveMiddles(middlesData.items || []);
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

    return (
        <div className="px-4 space-y-8 pb-20">
            {/* Header Area */}
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
                            sparkline={true}
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
                {/* Left Side: Analytics & Whale Tracking */}
                <div className="lg:col-span-8 space-y-6">
                    <WhaleTracker />

                    {/* Live Track Grid */}
                    <div className="bg-[#141424] border border-[#1E1E35] p-6 rounded-2xl space-y-6">
                        <div className="flex justify-between items-center">
                            <h3 className="text-white font-bold flex items-center gap-2 uppercase tracking-tight italic">
                                <Activity className="text-[#F5C518] animate-pulse" size={18} /> Live Performance
                            </h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <LiveTrackCard
                                player="LeBron James"
                                statType="Points"
                                currentValue={23.5}
                                line={25.5}
                                side="over"
                                gameStatus="4Q 4:12"
                            />
                            <LiveTrackCard
                                player="Luka Doncic"
                                statType="Rebounds"
                                currentValue={9}
                                line={8.5}
                                side="over"
                                gameStatus="HALFTIME"
                            />
                        </div>
                    </div>
                </div>

                {/* Right Side: Brain Health & Intel */}
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

                    <div className="bg-[#141424] border border-[#1E1E35] rounded-2xl flex flex-col overflow-hidden">
                        <div className="p-4 border-b border-[#1E1E35] bg-[#0F0F1A]/50">
                            <h4 className="text-xs font-black text-white uppercase tracking-widest flex items-center justify-between">
                                <span>Recent Intel</span>
                                <span className="text-[9px] bg-[#F5C518] text-black px-1.5 py-0.5 rounded-full font-black animate-pulse">LIVE</span>
                            </h4>
                        </div>
                        <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
                            <LogItem time={healingTime} message="Brain sync successful. Re-evaluating NBA injury risk factors." color="text-[#F5C518]" />
                            <LogItem time={healingTime} message="Oddstream detected +2.5% arbitrage opportunity in BOS@MIA." color="text-[#22C55E]" />
                            <LogItem time={healingTime} message="Whale activity spike on NYK Moneyline detected." color="text-[#FF6B35]" />
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

function MetricCard({ label, value, trend, sparkline, progress, badge, status }: any) {
    return (
        <div className="bg-[#141424] border border-[#1E1E35] p-6 rounded-2xl flex flex-col gap-2 relative overflow-hidden group hover:border-[#F5C518]/30 transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.3)]">
            <div className="flex justify-between items-start z-10">
                <div>
                    <p className="text-[#6B7280] text-[10px] font-black uppercase tracking-widest flex items-center gap-1.5">
                        {label}
                    </p>
                    <h3 className="text-3xl font-black text-white mt-2 tracking-tighter italic font-mono">{value}</h3>
                </div>
                {trend && (
                    <span className="text-[#22C55E] text-xs font-black flex items-center gap-0.5">
                        ▲ {trend}
                    </span>
                )}
                {badge && (
                    <span className="bg-[#F5C518]/10 text-[#F5C518] text-[9px] font-black px-2 py-0.5 rounded-full border border-[#F5C518]/20">{badge}</span>
                )}
                {status === 'healthy' && (
                    <div className="h-4 w-4 rounded-full bg-[#22C55E]/20 flex items-center justify-center animate-pulse">
                        <div className="h-1.5 w-1.5 rounded-full bg-[#22C55E] shadow-[0_0_8px_#22C55E]"></div>
                    </div>
                )}
            </div>

            {progress !== undefined && (
                <div className="mt-4">
                    <div className="w-full bg-[#1E1E35] rounded-full h-1">
                        <div className="bg-[#F5C518] h-1 rounded-full shadow-[0_0_10px_rgba(245,197,24,0.3)]" style={{ width: `${progress}%` }}></div>
                    </div>
                </div>
            )}

            <div className="absolute -right-2 -bottom-2 w-16 h-16 bg-[#F5C518]/5 rounded-full blur-2xl group-hover:bg-[#F5C518]/10 transition-all duration-700"></div>
        </div>
    );
}

function HealthItem({ label, status }: any) {
    return (
        <div className="flex items-center justify-between border-b border-[#1E1E35] pb-2 last:border-0 last:pb-0">
            <span className="text-xs text-[#6B7280] font-semibold">{label}</span>
            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-full border ${status === 'STABLE' || status === 'SYNCED' || status === 'ACTIVE' ? 'bg-[#22C55E]/10 border-[#22C55E]/20 text-[#22C55E]' : 'bg-[#F5C518]/10 border-[#F5C518]/20 text-[#F5C518]'}`}>
                {status}
            </span>
        </div>
    );
}

function LogItem({ time, message, color }: any) {
    return (
        <div className="p-4 border-b border-[#1E1E35] hover:bg-white/[0.02] transition-colors">
            <div className="flex justify-between items-center mb-1">
                <span className={`${color} text-[10px] font-black uppercase tracking-wider`}>System Log</span>
                <span className="text-[10px] text-[#6B7280] font-mono">{time}</span>
            </div>
            <p className="text-xs text-white leading-relaxed font-medium">{message}</p>
        </div>
    );
}
