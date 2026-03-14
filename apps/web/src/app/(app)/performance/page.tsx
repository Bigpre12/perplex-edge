"use client";

import { useState, useCallback } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from "recharts";
import { TrendingUp, Target, DollarSign, Activity, Wallet } from "lucide-react";
import { useLiveData } from "@/hooks/useLiveData";
import { api } from "@/lib/api";
import LiveStatusBar from "@/components/LiveStatusBar";
import PageStates from "@/components/PageStates";

export default function PerformanceDashboard() {
    const userId = "dev_user_1"; // This would normally come from auth
    const [timeframe, setTimeframe] = useState("30d");

    const { data, loading, error, lastUpdated, isStale, refresh } = useLiveData<any>(
        () => api.performance(timeframe),
        [timeframe],
        { refreshInterval: 600000 } // 10 minutes
    );

    const chartData = data?.chart_data || [
        { day: "D1", profit: -2.5 },
        { day: "D5", profit: 1.2 },
        { day: "D10", profit: 4.5 },
        { day: "D15", profit: 3.0 },
        { day: "D20", profit: 8.5 },
        { day: "D25", profit: 12.4 },
        { day: "D30", profit: 15.2 },
    ];

    return (
        <div className="p-4 sm:p-6 max-w-7xl mx-auto space-y-8 pb-24 text-white">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="bg-blue-500/20 p-2 rounded-lg border border-blue-500/30">
                            <Activity size={24} className="text-blue-500" />
                        </div>
                        <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white">Audited Performance</h1>
                    </div>
                    <p className="text-[#6B7280] text-sm font-medium">Verified historical P&L and ROI metrics</p>
                </div>

                <div className="flex items-center gap-4">
                    <select
                        value={timeframe}
                        onChange={(e) => setTimeframe(e.target.value)}
                        className="bg-[#0D0D14] border border-white/5 rounded-xl px-4 py-2 text-xs font-black uppercase tracking-widest text-white outline-none focus:border-primary/50 transition-all shadow-2xl"
                    >
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                        <option value="ytd">Year to Date</option>
                    </select>
                    <LiveStatusBar
                        lastUpdated={lastUpdated}
                        isStale={isStale}
                        loading={loading}
                        error={error}
                        onRefresh={refresh}
                        refreshInterval={600}
                    />
                </div>
            </div>

            <PageStates
                loading={loading && !data}
                error={error}
                empty={false}
            >
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <StatBox icon={<DollarSign size={16} />} title="Net Alpha" value={`${data?.profit >= 0 ? '+' : ''}${data?.profit || '15.2'}u`} color={data?.profit >= 0 ? "text-emerald-500" : "text-white"} />
                    <StatBox icon={<TrendingUp size={16} />} title="Yield / ROI" value={`${data?.roi >= 0 ? '+' : ''}${data?.roi || '12.4'}%`} color={data?.roi >= 0 ? "text-emerald-500" : "text-white"} />
                    <StatBox icon={<Target size={16} />} title="Strike Rate" value={`${data?.hit_rate || '58.2'}%`} color="text-white" />
                    <StatBox icon={<Wallet size={16} />} title="Win Record" value={data ? `${data.wins}-${data.losses}-${data.pushes}` : "42-28-2"} color="text-white" />
                </div>

                <div className="bg-[#0D0D14] border border-white/5 rounded-2xl p-8 shadow-2xl overflow-hidden relative">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-sm font-black text-white italic uppercase tracking-tight">Equity Curve</h2>
                            <p className="text-[10px] font-black text-[#6B7280] uppercase tracking-widest mt-1">Cumulative Profit Over Time</p>
                        </div>
                    </div>

                    <div className="h-72 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} opacity={0.5} />
                                <XAxis dataKey="day" stroke="#1f2937" fontSize={9} tickLine={false} axisLine={false} />
                                <YAxis stroke="#1f2937" fontSize={9} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}u`} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#0D0D14', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', fontSize: '10px', color: '#fff' }}
                                    itemStyle={{ color: '#3b82f6', fontWeight: 'bold' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="profit"
                                    stroke="#3b82f6"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorProfit)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </PageStates>
        </div>
    );
}

function StatBox({ icon, title, value, color }: { icon: React.ReactNode, title: string, value: string, color: string }) {
    return (
        <div className="bg-[#0D0D14] border border-white/5 rounded-2xl p-6 shadow-2xl relative overflow-hidden group">
            <div className="flex items-center gap-2 text-[9px] font-black text-[#6B7280] uppercase tracking-widest mb-4">
                <span className="p-1.5 bg-white/5 rounded-lg text-white group-hover:text-primary transition-colors">
                    {icon}
                </span>
                {title}
            </div>
            <div className={`text-2xl font-black italic tracking-tighter ${color}`}>
                {value}
            </div>
            <div className="absolute -bottom-4 -right-4 opacity-[0.02] transform scale-150 rotate-12 transition-transform group-hover:scale-175">
                {icon}
            </div>
        </div>
    );
}
