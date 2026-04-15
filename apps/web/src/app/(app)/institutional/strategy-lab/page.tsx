"use client";

import { useState, useEffect, Suspense } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Scale, Zap, Cpu, Download, ArrowRight, Filter, Target, ShieldAlert, TrendingUp, History, Timer, Play, Settings2, BarChart3, LineChart, FlaskConical, Loader2 } from "lucide-react";
import {
    Area,
    AreaChart,
    ResponsiveContainer,
    Tooltip,
    YAxis,
    XAxis,
    CartesianGrid,
    Line,
    LineChart as RechartLine
} from "recharts";
import API, { isApiError } from "@/lib/api";
import GateLock from "@/components/GateLock";
import { useGate } from "@/hooks/useGate";

function StrategyContent() {
    const [loading, setLoading] = useState(false);
    const [backtestResult, setBacktestResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [params, setParams] = useState({
        initial_bankroll: 1000,
        min_ev: 3.5,
        bet_sizing_model: "half_kelly",
        unit_size: 1.0,
        days: 30
    });

    const runBacktest = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await API.backtestRun({
                ...params,
                start_date: new Date(Date.now() - params.days * 24 * 60 * 60 * 1000).toISOString()
            });

            if (isApiError(data)) {
                if (data.status === 401) {
                    setError("Session expired. Please login again.");
                } else {
                    setError(data.message || "Simulation failed. Check backend logs.");
                }
                return;
            }

            setBacktestResult(data);
        } catch (err) {
            setError("Cannot connect to simulation engine. Check that backend is running.");
            console.error("Backtest failed:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8 pb-12">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-primary/20 rounded-lg text-primary shadow-[0_0_15px_rgba(13,242,51,0.2)]">
                            <FlaskConical size={24} />
                        </div>
                        <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic">Institutional Strategy Lab</h1>
                    </div>
                    <p className="text-secondary text-sm font-medium">Backtest and optimize wagering models against historical market depth.</p>
                </div>
                <button
                    onClick={runBacktest}
                    disabled={loading}
                    className="px-8 py-3 bg-gradient-to-r from-primary to-emerald-400 text-background-dark font-black rounded-2xl hover:scale-105 active:scale-95 transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(13,242,51,0.3)] disabled:opacity-50"
                >
                    {loading ? <Timer className="animate-spin" size={20} /> : <Play size={20} />}
                    {loading ? "SIMULATING..." : "RUN SIMULATION"}
                </button>
            </div>

            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-sm text-red-400 font-bold">
                    ⚠️ {error}
                </div>
            )}

            <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
                {/* Configuration Sidebar */}
                <div className="xl:col-span-1 space-y-6">
                    <div className="glass-panel p-6 rounded-3xl border-white/[0.05]">
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Settings2 size={14} /> Global Parameters
                        </h3>
                        <div className="space-y-6">
                            <ParamInput
                                label="Initial Bankroll"
                                value={params.initial_bankroll}
                                onChange={(v: any) => setParams({ ...params, initial_bankroll: parseInt(v) })}
                            />
                            <ParamInput
                                label="Execution Horizon (Days)"
                                value={params.days}
                                onChange={(v: any) => setParams({ ...params, days: parseInt(v) })}
                                max={90}
                            />
                            <div className="space-y-2">
                                <label className="text-[9px] font-black text-slate-500 uppercase tracking-tighter">Wagering Model</label>
                                <select
                                    className="w-full bg-black/20 border border-white/5 rounded-xl px-4 py-3 text-xs text-white focus:outline-none"
                                    value={params.bet_sizing_model}
                                    onChange={(e) => setParams({ ...params, bet_sizing_model: e.target.value })}
                                    aria-label="Wagering Model"
                                >
                                    <option value="fixed">Fixed Unit (Initial)</option>
                                    <option value="kelly">Full Kelly</option>
                                    <option value="half_kelly">Half Kelly (Fractional)</option>
                                    <option value="cppi">CPPI (Risk Protection)</option>
                                </select>
                            </div>
                            <ParamInput
                                label="Minimum EV% Guard"
                                value={params.min_ev}
                                onChange={(v: any) => setParams({ ...params, min_ev: parseFloat(v) })}
                                step={0.1}
                            />
                        </div>
                    </div>

                    <div className="p-6 rounded-3xl bg-slate-900 border border-white/[0.05] relative overflow-hidden group hover:border-amber-500/30 transition-colors">
                        <div className="absolute top-0 right-0 p-4 opacity-10 text-amber-500 group-hover:rotate-12 transition-transform">
                            <ShieldAlert size={60} />
                        </div>
                        <h4 className="text-[10px] font-black text-amber-500 uppercase tracking-widest mb-2">Backtest Constraints</h4>
                        <p className="text-[10px] text-slate-400 font-medium leading-relaxed italic z-10 relative">
                            Simulations use "Closing Line Value" proxies where settle data is absent. Slippage of 0.5% is assumed for high-volume execution.
                        </p>
                    </div>
                </div>

                {/* Main Results Area */}
                <div className="xl:col-span-3 space-y-8">
                    {backtestResult ? (
                        <>
                            {/* Key Stats Cards */}
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                                <StatsCard label="Total Return" value={`+${backtestResult.summary.total_return_pct}%`} sub="ROI" color="primary" />
                                <StatsCard label="Win Rate" value={`${backtestResult.summary.win_rate}%`} sub={`${backtestResult.summary.wins}W / ${backtestResult.summary.losses}L`} color="emerald-500" />
                                <StatsCard label="Sharpe Ratio" value={backtestResult.summary.sharpe_ratio} sub="Risk-Adj Performance" color="amber-500" />
                                <StatsCard label="Volatility" value={`${backtestResult.summary.volatility}%`} sub="Expected StdDev" color="red-500" />
                            </div>

                            {/* Equity Curve Chart */}
                            <div className="h-[450px] w-full min-w-0">
                                    <ResponsiveContainer width="100%" height="85%" minHeight={1} minWidth={1}>
                                    <AreaChart data={backtestResult.equity_curve}>
                                        <defs>
                                            <linearGradient id="colorBalance" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#0df233" stopOpacity={0.1} />
                                                <stop offset="95%" stopColor="#0df233" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
                                        <XAxis
                                            dataKey="timestamp"
                                            hide
                                        />
                                        <YAxis
                                            orientation="right"
                                            stroke="#475569"
                                            fontSize={10}
                                            tickFormatter={(val) => `$${val}`}
                                            axisLine={false}
                                            tickLine={false}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0c1416', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', fontSize: '10px' }}
                                            labelStyle={{ display: 'none' }}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="balance"
                                            stroke="#0df233"
                                            strokeWidth={3}
                                            fillOpacity={1}
                                            fill="url(#colorBalance)"
                                            animationDuration={2000}
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Performance Breakdown Table */}
                            <div className="glass-panel p-8 rounded-3xl border-white/[0.05]">
                                <div className="flex items-center justify-between mb-8">
                                    <h3 className="text-sm font-black text-white uppercase italic tracking-widest flex items-center gap-2">
                                        <Zap size={18} className="text-primary" /> Simulation Execution Logs
                                    </h3>
                                    <button className="text-[10px] font-black text-slate-500 hover:text-white transition-all flex items-center gap-1 uppercase">
                                        <Download size={14} /> Export CSV
                                    </button>
                                </div>
                                <div className="space-y-2">
                                    {backtestResult.equity_curve.slice(-8).reverse().map((trade: any, idx: number) => (
                                        <div key={idx} className="flex items-center justify-between py-3 border-b border-white/[0.03] last:border-0">
                                            <div className="flex items-center gap-4">
                                                <span className={`text-[10px] font-black px-2 py-0.5 rounded ${trade.profit > 0 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'}`}>
                                                    {trade.profit > 0 ? 'WIN' : 'LOSS'}
                                                </span>
                                                <div>
                                                    <p className="text-[11px] font-bold text-white">Execution Result: {trade.profit > 0 ? `+$${trade.profit}` : `-$${Math.abs(trade.profit)}`}</p>
                                                    <p className="text-[9px] text-slate-500 font-mono uppercase">Bankroll: ${trade.balance}</p>
                                                </div>
                                            </div>
                                            <span className="text-[9px] font-bold text-slate-600 italic uppercase">Settled @ Closing</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="h-[600px] glass-panel rounded-3xl border-white/[0.05] flex flex-col items-center justify-center text-center p-12">
                            <div className="size-20 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-6 animate-pulse shadow-[0_0_30px_rgba(13,242,51,0.1)]">
                                <FlaskConical size={40} />
                            </div>
                            <h2 className="text-2xl font-black text-white uppercase tracking-tighter italic mb-4">Laboratory Idle</h2>
                            <p className="max-w-md text-slate-500 font-medium leading-relaxed text-sm">
                                Configure your wagering parameters on the left and trigger the simulation engine to generate historical performance metrics.
                            </p>
                            <div className="grid grid-cols-3 gap-8 mt-12 w-full max-w-lg">
                                <PlaceholderTip icon={<Cpu size={24} />} label="HPC Simulation" />
                                <PlaceholderTip icon={<Target size={24} />} label="Result Grading" />
                                <PlaceholderTip icon={<Scale size={24} />} label="Risk Auditing" />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function ParamInput({ label, value, onChange, type = "number", max, step, ...props }: any) {
    return (
        <div className="space-y-2">
            <label className="text-[9px] font-black text-slate-500 uppercase tracking-tighter">{label}</label>
            <input
                type={type}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="w-full bg-black/20 border border-white/5 rounded-xl px-4 py-3 text-xs text-white font-mono focus:outline-none focus:border-primary/50"
                {...props}
                max={max}
                step={step}
            />
        </div>
    );
}

function StatsCard({ label, value, sub, color = "primary" }: any) {
    const isPrimary = color === "primary";
    return (
        <div className={`p-6 rounded-3xl border border-white/[0.05] relative overflow-hidden group hover:border-white/10 transition-all ${isPrimary ? "bg-[#0df233]/10" : "bg-[#0c1416]/90 backdrop-blur-md"}`}>
            <div className={`absolute -right-10 -top-10 size-40 rounded-full blur-3xl opacity-20 ${isPrimary ? "bg-[#0df233]" : `bg-${color}`}`}></div>
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">{label}</p>
            <h3 className={`text-4xl font-black ${isPrimary ? "text-[#0df233]" : "text-white"} tracking-tighter`}>{value}</h3>
            <p className="text-xs text-slate-400 font-medium mt-2">{sub}</p>
        </div>
    );
}

function PlaceholderTip({ icon, label }: any) {
    return (
        <div className="flex flex-col items-center gap-3">
            <div className="size-12 rounded-2xl bg-white/[0.03] border border-white/[0.05] flex items-center justify-center text-slate-600">
                {icon}
            </div>
            <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">{label}</span>
        </div>
    );
}

export default function StrategyLab() {
    return (
        <Suspense fallback={
            <div className="h-[60vh] flex flex-col items-center justify-center gap-4 text-primary">
                <Loader2 size={40} className="animate-spin" />
                <p className="text-sm font-bold uppercase tracking-widest text-slate-400">Simulation Engine Initializing...</p>
            </div>
        }>
            <StrategyContent />
        </Suspense>
    );
}
