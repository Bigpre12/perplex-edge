"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
    TrendingUp,
    ShieldCheck,
    Clock,
    ArrowLeft,
    Brain,
    Loader2,
    PieChart,
    BarChart3,
    Activity,
    ShieldAlert,
    AlertTriangle,
    Zap,
    Download
} from "lucide-react";
import { getAuthToken } from "@/lib/auth";
import Link from "next/link";
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    ZAxis,
    Tooltip,
    ResponsiveContainer,
    Cell
} from 'recharts';

export default function PortfolioAnalytics() {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    const handleExport = async (format: 'csv' | 'json') => {
        const token = getAuthToken();
        if (!token) return;

        try {
            const res = await fetch(`http://localhost:8000/reporting/export/${format}`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `perplex_ledger_export.${format}`;
                document.body.appendChild(a);
                a.click();
                a.remove();
            }
        } catch (err) {
            console.error(`Export to ${format} failed:`, err);
        }
    };

    useEffect(() => {
        const fetchStats = async () => {
            const token = getAuthToken();
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const res = await fetch("http://localhost:8000/ledger/stats", {
                    headers: { "Authorization": `Bearer ${token}` }
                });
                if (res.ok) setStats(await res.json());
            } catch (err) {
                console.error("Failed to fetch statistics:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return (
            <div className="h-[60vh] flex items-center justify-center">
                <Loader2 className="animate-spin text-primary" size={40} />
            </div>
        );
    }

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/ledger" className="p-2 hover:bg-white/5 rounded-full text-slate-400 hover:text-white transition-all">
                        <ArrowLeft size={20} />
                    </Link>
                    <div>
                        <h1 className="text-3xl font-black text-white tracking-tight">Portfolio Deep-Dive</h1>
                        <p className="text-secondary text-sm mt-1 italic">Advanced ROI Correlation & Risk Analysis</p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={() => handleExport('csv')}
                        className="flex items-center gap-2 px-4 py-2 bg-surface border border-white/10 rounded-lg text-xs font-bold text-slate-400 hover:text-white transition-all"
                    >
                        <Download size={14} /> CSV Audit
                    </button>
                    <button
                        onClick={() => handleExport('json')}
                        className="flex items-center gap-2 px-4 py-2 bg-surface border border-white/10 rounded-lg text-xs font-bold text-slate-400 hover:text-white transition-all"
                    >
                        <Download size={14} /> JSON Ledger
                    </button>
                    <div className="px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                        <p className="text-[10px] text-emerald-500 font-black uppercase">Net Profit</p>
                        <p className="text-xl font-black text-white">${stats?.profit_loss || '0.00'}</p>
                    </div>
                </div>
            </div>

            {/* Top Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-premium p-6 rounded-2xl border-white/[0.05] relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                        <ShieldCheck size={80} />
                    </div>
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Success Probability</p>
                    <h3 className="text-4xl font-black text-white">{stats?.win_rate}%</h3>
                    <div className="mt-4 flex items-center gap-2">
                        <div className="h-1.5 flex-1 bg-slate-800 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${stats?.win_rate}%` }}
                                className="h-full bg-primary"
                            />
                        </div>
                    </div>
                </div>

                <div className="glass-premium p-6 rounded-2xl border-white/[0.05] relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                        <TrendingUp size={80} />
                    </div>
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Market Efficiency</p>
                    <h3 className="text-4xl font-black text-white">+8.4%</h3>
                    <p className="text-[10px] text-emerald-500 font-bold mt-2 flex items-center gap-1">
                        <Activity size={12} /> Beating Closing Line
                    </p>
                </div>

                <div className="glass-premium p-6 rounded-2xl border-white/[0.05] relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                        <Clock size={80} />
                    </div>
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Total Volume</p>
                    <h3 className="text-4xl font-black text-white">{stats?.total_bets}</h3>
                    <p className="text-[10px] text-slate-400 font-bold mt-2 uppercase tracking-tighter">Bets Tracked</p>
                </div>

                {/* Risk Governance & Alerts */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
                        <RiskMetricCard
                            label="Max Drawdown"
                            value={stats?.risk_metrics?.max_drawdown || '0%'}
                            sub="Peak-to-Trough"
                            color="text-red-400"
                        />
                        <RiskMetricCard
                            label="Risk of Ruin"
                            value={stats?.risk_metrics?.risk_of_ruin || '0%'}
                            sub="Institutional Model"
                            color="text-amber-400"
                        />
                        <RiskMetricCard
                            label="Stability Score"
                            value={stats?.risk_metrics?.stability_score || '0'}
                            sub="Governance Rating"
                            color="text-primary"
                        />
                    </div>

                    <div className="glass-panel p-6 rounded-2xl border-white/[0.05] bg-gradient-to-br from-red-500/5 to-transparent flex flex-col justify-center">
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                            <ShieldAlert size={14} className="text-red-500" /> Executive Alerts
                        </h3>
                        <div className="space-y-3">
                            {stats?.risk_metrics?.alerts?.filter((a: any) => a).map((alert: string, i: number) => (
                                <div key={i} className="flex items-start gap-2 text-[10px] font-bold text-slate-300 leading-tight">
                                    <AlertTriangle size={12} className="text-amber-500 shrink-0 mt-0.5" />
                                    {alert}
                                </div>
                            ))}
                            {(!stats?.risk_metrics?.alerts || stats.risk_metrics.alerts.filter((a: any) => a).length === 0) && (
                                <p className="text-[10px] text-slate-500 italic">Portfolio status: Nominal. No critical risk alerts detected.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Heatmaps */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* ROI by Sport Heatmap */}
                <div className="glass-panel p-8 rounded-3xl border-white/[0.05]">
                    <div className="flex items-center justify-between mb-8">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
                            <PieChart size={18} className="text-primary" /> ROI Heatmap: Sports
                        </h3>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                        {stats?.heatmaps?.by_sport?.map((item: any, i: number) => (
                            <HeatmapCell key={i} label={item.label} value={item.value} intensity={item.intensity} />
                        ))}
                        {(!stats?.heatmaps?.by_sport || stats.heatmaps.by_sport.length === 0) && (
                            <p className="text-xs text-slate-500 italic col-span-full py-12 text-center">No sport data available</p>
                        )}
                    </div>
                </div>

                {/* ROI by Market Heatmap */}
                <div className="glass-panel p-8 rounded-3xl border-white/[0.05]">
                    <div className="flex items-center justify-between mb-8">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
                            <BarChart3 size={18} className="text-primary" /> ROI Heatmap: Markets
                        </h3>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                        {stats?.heatmaps?.by_market?.map((item: any, i: number) => (
                            <HeatmapCell key={i} label={item.label} value={item.value} intensity={item.intensity} />
                        ))}
                        {(!stats?.heatmaps?.by_market || stats.heatmaps.by_market.length === 0) && (
                            <p className="text-xs text-slate-500 italic col-span-full py-12 text-center">No market data available</p>
                        )}
                    </div>
                </div>
            </div>

            {/* Risk vs Reward Scatter Plot */}
            <div className="glass-panel p-8 rounded-3xl border-white/[0.05]">
                <div className="flex items-center justify-between mb-8">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2 uppercase tracking-widest">
                        <Brain size={18} className="text-primary" /> Volatility Spectrum (Risk vs Reward)
                    </h3>
                    <div className="flex gap-4 text-[10px] font-black uppercase tracking-tighter">
                        <div className="flex items-center gap-1.5">
                            <div className="size-2 rounded-full bg-emerald-500"></div>
                            <span className="text-slate-400">Wins</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <div className="size-2 rounded-full bg-red-500"></div>
                            <span className="text-slate-400">Losses</span>
                        </div>
                    </div>
                </div>

                <div className="h-[400px] w-full mt-4">
                    <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                            <XAxis
                                type="number"
                                dataKey="odds"
                                name="Odds"
                                unit=""
                                stroke="#475569"
                                fontSize={10}
                                tickFormatter={(val) => val > 0 ? `+${val}` : val}
                            />
                            <YAxis
                                type="number"
                                dataKey="profit"
                                name="Profit"
                                unit="u"
                                stroke="#475569"
                                fontSize={10}
                            />
                            <ZAxis type="number" range={[100, 100]} />
                            <Tooltip
                                cursor={{ strokeDasharray: '3 3' }}
                                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }}
                                itemStyle={{ color: '#fff', fontSize: '12px' }}
                            />
                            <Scatter name="Bets" data={stats?.risk_reward || []}>
                                {stats?.risk_reward?.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={entry.status === 'won' ? '#10b981' : '#ef4444'} />
                                ))}
                            </Scatter>
                        </ScatterChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}

function HeatmapCell({ label, value, intensity }: any) {
    return (
        <motion.div
            whileHover={{ scale: 1.05 }}
            className={`p-4 rounded-xl border flex flex-col justify-between h-24 transition-all duration-500`}
            style={{
                backgroundColor: `rgba(13, 242, 51, ${intensity * 0.2})`,
                borderColor: `rgba(13, 242, 51, ${intensity * 0.4})`
            }}
        >
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-tighter truncate">{label}</p>
            <p className={`text-lg font-black ${value >= 0 ? 'text-primary' : 'text-red-400'}`}>
                {value >= 0 ? '+' : ''}{value}u
            </p>
        </motion.div>
    )
}

function RiskMetricCard({ label, value, sub, color }: any) {
    return (
        <div className="glass-premium p-6 rounded-2xl border-white/[0.05] flex flex-col justify-center">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{label}</p>
            <h3 className={`text-2xl font-black ${color}`}>{value}</h3>
            <p className="text-[10px] text-slate-500 font-bold mt-1 uppercase tracking-tighter">{sub}</p>
        </div>
    );
}
