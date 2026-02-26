"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { useBrainData } from '@/hooks/useBrainData';
import { Database, MemoryStick as Memory, Globe, Activity, Brain, Loader2, Target, TrendingUp } from 'lucide-react';
import Link from 'next/link';
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

export default function Dashboard() {
    const { decisions, loading } = useBrainData();
    const [metrics, setMetrics] = useState<BrainMetrics | null>(null);
    const [healing, setHealing] = useState<HealingStatus | null>(null);
    const [metricsLoading, setMetricsLoading] = useState(true);
    const [healingTime, setHealingTime] = useState('—');

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const backendUrl = "http://localhost:8000";
                const [metricsRes, healingRes] = await Promise.all([
                    fetch(`${backendUrl}/immediate/brain-metrics`),
                    fetch(`${backendUrl}/immediate/brain-healing-status`)
                ]);
                const metricsData = await metricsRes.json();
                const healingData = await healingRes.json();
                setMetrics(metricsData);
                setHealing(healingData);
            } catch (err) {
                console.error("Failed to fetch dashboard metrics:", err);
            } finally {
                setMetricsLoading(false);
            }
        };
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 15000);
        // Client-only time updater to avoid hydration mismatch
        setHealingTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
        const timeInterval = setInterval(() => setHealingTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })), 1000);
        return () => { clearInterval(interval); clearInterval(timeInterval); };
    }, []);

    return (
        <div className="space-y-8">
            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {metricsLoading ? (
                    <div className="col-span-4 py-8 text-center"><Loader2 className="animate-spin text-primary mx-auto" size={24} /></div>
                ) : (
                    <>
                        <MetricCard
                            label="Rec. Hit Rate"
                            value={metrics ? `${(metrics.recommendation_hit_rate * 100).toFixed(1)}%` : '—'}
                            trend={metrics ? `+${((metrics.recommendation_hit_rate - 0.55) * 100).toFixed(1)}%` : undefined}
                            sparkline={true}
                        />
                        <MetricCard
                            label="Average EV"
                            value={metrics ? `+${(metrics.average_ev * 100).toFixed(1)}%` : '—'}
                            trend={metrics ? `+${((metrics.average_ev - 0.15) * 100).toFixed(1)}%` : undefined}
                            progress={metrics ? Math.round(metrics.average_ev * 300) : 0}
                            progressLabel="EV performance vs historical average"
                        />
                        <MetricCard
                            label="Total Recommendations"
                            value={metrics ? metrics.total_recommendations.toLocaleString() : '—'}
                            badge="Live"
                            stats={[{ label: 'Volume', value: metrics?.prop_volume?.toLocaleString() || '—' }, { label: 'Confidence', value: metrics ? `${(metrics.user_confidence_score * 100).toFixed(0)}%` : '—' }]}
                        />
                        <MetricCard
                            label="API Health Status"
                            value={healing?.status === 'healthy' ? '99.9%' : 'Degraded'}
                            status={healing?.status === 'healthy' ? 'healthy' : undefined}
                            subMetrics={[
                                { label: 'Latency', value: metrics ? `${metrics.api_response_time_ms}ms` : '—' },
                                { label: 'Error Rate', value: metrics ? `${(metrics.error_rate * 100).toFixed(2)}%` : '—' }
                            ]}
                        />
                    </>
                )}
            </div>

            {/* Main Dashboard Area */}
            <div className="flex flex-col lg:flex-row gap-6 h-auto min-h-[500px]">
                {/* Left Column: Analytics & Chart */}
                <div className="flex-1 flex flex-col gap-6">
                    <div className="flex items-center border-b border-slate-800">
                        <button className="px-6 py-3 text-sm font-medium text-primary border-b-2 border-primary focus:outline-none bg-surface/30 rounded-t-lg">
                            Performance Analytics
                        </button>
                        <button className="px-6 py-3 text-sm font-medium text-secondary hover:text-white border-b-2 border-transparent hover:border-slate-600 focus:outline-none transition-colors">
                            System Health
                        </button>
                    </div>

                    <div className="glass-panel p-6 rounded-xl flex-1 flex flex-col min-h-[400px]">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-white font-semibold flex items-center gap-2">
                                <span className="material-symbols-outlined text-primary text-xl">show_chart</span>
                                Hit Rate vs. CLV Trend
                            </h3>
                            <div className="flex gap-2 bg-surface rounded-lg p-1 border border-slate-700">
                                {['30D', '7D', '24H'].map((t) => (
                                    <button key={t} className={`px-3 py-1 text-xs font-medium rounded transition-colors ${t === '30D' ? 'text-white bg-slate-700 shadow-sm' : 'text-secondary hover:text-white'}`}>
                                        {t}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Chart Visual Representation using SVG */}
                        <div className="flex-1 w-full relative">
                            <div className="absolute left-0 top-0 bottom-8 w-8 flex flex-col justify-between text-xs text-secondary/50 font-mono">
                                <span>80%</span><span>60%</span><span>40%</span><span>20%</span><span>0%</span>
                            </div>
                            <svg className="w-full h-full pl-10 pb-8 overflow-visible" preserveAspectRatio="none" viewBox="0 0 800 300">
                                <line opacity="0.3" stroke="#334155" strokeDasharray="4" x1="0" x2="800" y1="0" y2="0"></line>
                                <line opacity="0.3" stroke="#334155" strokeDasharray="4" x1="0" x2="800" y1="75" y2="75"></line>
                                <line opacity="0.3" stroke="#334155" strokeDasharray="4" x1="0" x2="800" y1="150" y2="150"></line>
                                <line opacity="0.3" stroke="#334155" strokeDasharray="4" x1="0" x2="800" y1="225" y2="225"></line>
                                <defs>
                                    <linearGradient id="chartGradient" x1="0" x2="0" y1="0" y2="1">
                                        <stop offset="0%" stopColor="#0dccf2" stopOpacity="0.2"></stop>
                                        <stop offset="100%" stopColor="#0dccf2" stopOpacity="0"></stop>
                                    </linearGradient>
                                </defs>
                                <path d="M0,200 C50,180 100,220 150,150 C200,80 250,100 300,90 C350,80 400,120 450,100 C500,80 550,40 600,50 C650,60 700,90 750,80 L800,60" fill="none" stroke="#0dccf2" strokeWidth="3"></path>
                                <path d="M0,200 C50,180 100,220 150,150 C200,80 250,100 300,90 C350,80 400,120 450,100 C500,80 550,40 600,50 C650,60 700,90 750,80 L800,60 V300 H0 Z" fill="url(#chartGradient)"></path>
                                <path d="M0,240 C60,230 120,200 180,190 C240,180 300,150 360,160 C420,170 480,140 540,130 C600,120 660,100 720,110 L800,90" fill="none" opacity="0.6" stroke="#94a3b8" strokeDasharray="6,4" strokeWidth="2"></path>
                                <circle cx="600" cy="50" fill="#0f1719" r="4" stroke="#0dccf2" strokeWidth="2"></circle>
                            </svg>
                        </div>
                    </div>
                </div>

                {/* Right Column: System Logs & Health */}
                <div className="w-full lg:w-96 flex flex-col gap-6">
                    <div className="glass-panel p-5 rounded-xl">
                        <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                            <Activity size={16} /> Brain Health
                        </h4>
                        <div className="space-y-4">
                            <HealthItem icon={<Database size={18} />} label="Data Pipeline" status={healing?.status === 'healthy' ? 'HEALTHY' : 'WARNING'} />
                            <HealthItem icon={<Memory size={18} />} label="Inference Engine" status={healing?.system_metrics_evaluated ? ((healing.system_metrics_evaluated.cpu_usage ?? 0) < 0.8 ? 'HEALTHY' : 'SCALING') : 'UNKNOWN'} color={(healing?.system_metrics_evaluated?.cpu_usage ?? 0) >= 0.8 ? 'text-accent-orange' : undefined} />
                            <HealthItem icon={<Globe size={18} />} label="Odds Stream" status={healing?.system_metrics_evaluated ? (healing.system_metrics_evaluated.error_rate < 0.01 ? 'HEALTHY' : 'DEGRADED') : 'UNKNOWN'} />
                        </div>
                    </div>

                    <WhaleTracker />

                    <div className="glass-panel rounded-xl flex-1 flex flex-col overflow-hidden max-h-[400px]">
                        <div className="p-4 border-b border-slate-700/50 bg-surface/30">
                            <h4 className="text-sm font-semibold text-white uppercase tracking-wider flex items-center justify-between">
                                <span>Healing Actions</span>
                                <span className="text-[10px] bg-primary/20 text-primary px-1.5 rounded">{healing?.active_healing ? 'ACTIVE' : 'IDLE'}</span>
                            </h4>
                        </div>
                        <div className="overflow-y-auto flex flex-col">
                            {healing?.ai_evaluation ? (
                                <LogItem
                                    type={healing.ai_evaluation.action || 'Monitoring'}
                                    time={healingTime}
                                    message={`[${healing.ai_evaluation.target || 'System'}] ${healing.ai_evaluation.reason || 'All systems nominal.'}`}
                                    color={healing.ai_evaluation.is_critical ? 'text-accent-orange' : 'text-accent-green'}
                                />
                            ) : (
                                <LogItem type="Monitoring" time={healingTime} message="Awaiting healing cycle data..." color="text-primary" />
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Live Track Section */}
            <div className="glass-panel p-6 rounded-xl space-y-6">
                <div className="flex justify-between items-center">
                    <h3 className="text-white font-semibold flex items-center gap-2">
                        <Activity className="text-primary animate-pulse" size={20} /> Live Beta Tracking
                    </h3>
                    <div className="flex items-center gap-2">
                        <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">4 Active Plays</span>
                    </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    <LiveTrackCard
                        player="LeBron James"
                        statType="Points"
                        currentValue={23.5}
                        line={25.5}
                        side="over"
                        gameStatus="4Q 4:12"
                        hedgeRecommendation="Lock in profit: Hedge Under if odds hit +200."
                    />
                    <LiveTrackCard
                        player="Tyrese Haliburton"
                        statType="Assists"
                        currentValue={11}
                        line={10.5}
                        side="over"
                        gameStatus="FINAL"
                    />
                    <LiveTrackCard
                        player="Connor McDavid"
                        statType="SOG"
                        currentValue={2}
                        line={4.5}
                        side="over"
                        gameStatus="2P 10:00"
                        hedgeRecommendation="Under-pacing: Monitor closely."
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

            {/* AI Decisions Section */}
            <div className="glass-panel p-6 rounded-xl">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="text-white font-semibold flex items-center gap-2">
                        <Brain className="text-primary" size={20} /> Recent AI Decisions
                    </h3>
                    <Link href="/player-props" className="text-xs text-primary hover:text-white transition-colors flex items-center gap-1">
                        View All <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                    </Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {decisions.slice(0, 3).map((dec, i) => (
                        <DecisionCard key={i} decision={dec} />
                    ))}
                    {!loading && decisions.length === 0 && (
                        <p className="col-span-full text-center text-slate-500 py-8">No active decisions found.</p>
                    )}
                </div>
            </div>
        </div>
    );
}

function MetricCard({ label, value, trend, sparkline, progress, progressLabel, badge, stats, status, subMetrics }: any) {
    return (
        <div className="glass-panel p-5 rounded-xl flex flex-col gap-4 relative overflow-hidden group hover:border-primary/30 transition-colors">
            <div className="flex justify-between items-start z-10">
                <div>
                    <p className="text-secondary text-xs font-medium uppercase tracking-wider">{label}</p>
                    <h3 className="text-2xl font-bold text-white mt-1">{value}</h3>
                </div>
                {trend && (
                    <span className="bg-accent-green/10 text-accent-green text-xs font-bold px-2 py-1 rounded-md flex items-center gap-1">
                        <span className="material-symbols-outlined text-[14px]">trending_up</span> {trend}
                    </span>
                )}
                {badge && (
                    <span className="bg-primary/10 text-primary text-xs font-bold px-2 py-1 rounded-md">{badge}</span>
                )}
                {status === 'healthy' && (
                    <div className="h-6 w-6 rounded-full bg-accent-green/20 flex items-center justify-center animate-pulse">
                        <div className="h-2.5 w-2.5 rounded-full bg-accent-green shadow-[0_0_8px_#0bda54]"></div>
                    </div>
                )}
            </div>

            {sparkline && (
                <div className="h-10 w-full flex items-end gap-1 z-10 opacity-70 group-hover:opacity-100 transition-opacity">
                    {[30, 45, 35, 60, 50, 75, 65, 85, 80, 95].map((h, i) => (
                        <div key={i} className={`w-1/12 rounded-t-sm ${i === 9 ? 'bg-primary shadow-[0_0_10px_rgba(13,242,51,0.5)]' : 'bg-primary/' + (20 + i * 5)}`} style={{ height: `${h}%` }}></div>
                    ))}
                </div>
            )}

            {progress && (
                <div className="mt-auto pt-4">
                    <div className="w-full bg-slate-700/50 rounded-full h-1.5">
                        <div className="bg-gradient-to-r from-accent-green to-primary h-1.5 rounded-full" style={{ width: `${progress}%` }}></div>
                    </div>
                    <p className="text-xs text-secondary mt-2">{progressLabel}</p>
                </div>
            )}

            {stats && (
                <div className="mt-auto grid grid-cols-2 gap-2 pt-2">
                    {stats.map((s: any, i: any) => (
                        <div key={i} className="bg-surface-highlight/50 p-2 rounded border border-slate-700/50">
                            <p className="text-[10px] text-secondary">{s.label}</p>
                            <p className="text-sm font-semibold text-white">{s.value}</p>
                        </div>
                    ))}
                </div>
            )}

            {subMetrics && (
                <div className="mt-auto flex flex-col gap-2 pt-2">
                    {subMetrics.map((m: any, i: any) => (
                        <div key={i} className="flex items-center justify-between text-xs">
                            <span className="text-secondary">{m.label}</span>
                            <span className="text-accent-green font-mono">{m.value}</span>
                        </div>
                    ))}
                </div>
            )}

            <div className="absolute -right-6 -top-6 w-24 h-24 bg-primary/10 rounded-full blur-2xl group-hover:bg-primary/20 transition-all"></div>
        </div>
    );
}

function HealthItem({ icon, label, status }: any) {
    return (
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
                <div className="bg-surface p-1.5 rounded-lg border border-slate-700 text-secondary">
                    {icon}
                </div>
                <span className="text-sm text-slate-200">{label}</span>
            </div>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold bg-current opacity-10 ${status === 'HEALTHY' ? 'bg-accent-green/10 text-accent-green' : 'bg-accent-orange/10 text-accent-orange'} border border-current`}>
                {status}
            </span>
        </div>
    );
}

function LogItem({ type, time, message, color }: any) {
    return (
        <div className="border-b border-slate-800/50 p-3 hover:bg-white/5 transition-colors cursor-default">
            <div className="flex justify-between items-center mb-1">
                <span className={`${color} text-xs font-bold`}>{type}</span>
                <span className="text-[10px] text-secondary font-mono">{time}</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">{message}</p>
        </div>
    );
}

function DecisionCard({ decision }: any) {
    return (
        <div className="bg-surface border border-slate-700/50 rounded-lg p-4 hover:border-primary/50 transition-all cursor-pointer group">
            <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center overflow-hidden">
                        <Brain size={18} className="text-primary" />
                    </div>
                    <div>
                        <p className="text-white font-bold text-sm">{decision.details.player_name} {decision.details.side.toUpperCase()}</p>
                        <p className="text-xs text-secondary">{decision.details.stat_type} • {decision.details.line_value}</p>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-accent-green font-mono font-bold text-sm">+{(decision.details.edge * 100).toFixed(1)}% EV</p>
                    <p className="text-[10px] text-secondary">Confidence: {(decision.details.confidence * 100).toFixed(0)}%</p>
                </div>
            </div>
            <div className="h-px bg-slate-700/50 my-3"></div>
            <div>
                <p className="text-slate-300 text-xs leading-5">
                    <span className="text-primary font-semibold">Reasoning:</span> {decision.reasoning}
                </p>
            </div>
            <div className="mt-3 flex items-center justify-between">
                <span className="text-[10px] text-secondary bg-surface-highlight px-2 py-0.5 rounded">Model: NeuralProphet-V4</span>
                <span className="text-[10px] text-secondary">Live</span>
            </div>
        </div>
    );
}

