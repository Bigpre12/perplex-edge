"use client";

import React, { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Activity, TrendingUp, Target, Wallet, Clock, Filter } from "lucide-react";
import { clsx } from "clsx";

export default function PerformancePage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">AUDITING PERFORMANCE...</div>}>
      <PerformanceContent />
    </Suspense>
  );
}

function PerformanceContent() {
  const { token, user } = useAuth();
  const [range, setRange] = useState("30d");

  const { data: perfData, isLoading, error, refetch } = useQuery({
    queryKey: ['performance', user?.id, range],
    queryFn: () => fetch(`${API_BASE}/api/performance?range=${range}`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.json()),
    enabled: !!token,
    staleTime: 300_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24 w-full rounded-2xl" />)}
        </div>
        <Skeleton className="h-80 w-full rounded-3xl" />
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message="Performance Audit Interrupted." onRetry={refetch} /></div>;
  }

  const stats = perfData?.stats || { profit: 0, roi: 0, win_rate: 0, record: "0-0-0" };
  const chartData = perfData?.chart_data || [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Activity size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Audited Performance</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Verified P&L & Equity Curve</p>
        </div>
        <div className="flex bg-lucrix-surface border border-lucrix-border rounded-xl p-1 shadow-inner">
          {["7d", "30d", "season"].map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={clsx(
                "px-4 py-2 text-[10px] font-black uppercase tracking-widest rounded-lg transition-all",
                range === r ? "bg-white text-black shadow-xl" : "text-textMuted hover:text-white"
              )}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard icon={<TrendingUp size={16} />} label="Net Alpha" value={`${stats.profit >= 0 ? '+' : ''}${stats.profit}U`} color={stats.profit >= 0 ? "text-brand-success" : "text-brand-danger"} />
        <StatCard icon={<Activity size={16} />} label="Yield / ROI" value={`${stats.roi >= 0 ? '+' : ''}${stats.roi}%`} color={stats.roi >= 0 ? "text-brand-success" : "text-brand-danger"} />
        <StatCard icon={<Target size={16} />} label="Win Rate" value={`${stats.win_rate}%`} />
        <StatCard icon={<Wallet size={16} />} label="Win Record" value={stats.record} />
      </div>

      <div className="bg-lucrix-surface border border-lucrix-border rounded-3xl p-8 shadow-card relative overflow-hidden">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h3 className="text-sm font-black text-white italic uppercase tracking-tight">Equity Curve</h3>
            <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mt-1">Cumulative Unit Growth</p>
          </div>
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center gap-1.5">
            <Clock size={12} className="text-brand-cyan" />
            Audited 1m ago
          </div>
        </div>

        <div className="h-72 w-full" style={{ minWidth: 0 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00f2ff" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#00f2ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} opacity={0.5} />
              <XAxis dataKey="date" stroke="#4b5563" fontSize={9} tickLine={false} axisLine={false} />
              <YAxis stroke="#4b5563" fontSize={9} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}U`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0D0D14', border: '1px solid #1e293b', borderRadius: '12px', fontSize: '10px' }}
                itemStyle={{ color: '#00f2ff', fontWeight: 'bold' }}
              />
              <Area
                type="monotone"
                dataKey="profit"
                stroke="#00f2ff"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorProfit)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color = "text-white" }: any) {
  return (
    <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 shadow-card hover:border-brand-cyan/20 transition-all group overflow-hidden relative">
      <div className="flex items-center gap-3 text-[10px] font-black text-textMuted uppercase tracking-widest mb-4">
        <div className="p-2 bg-lucrix-dark rounded-xl border border-lucrix-border group-hover:bg-brand-cyan/10 group-hover:text-brand-cyan transition-colors">
          {icon}
        </div>
        {label}
      </div>
      <div className={clsx("text-3xl font-black italic tracking-tighter font-display", color)}>
        {value}
      </div>
      <div className="absolute -bottom-4 -right-4 opacity-[0.03] transform scale-150 rotate-12 transition-transform group-hover:scale-175">
        {icon}
      </div>
    </div>
  );
}
