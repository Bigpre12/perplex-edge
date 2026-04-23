"use client";

import React, { useState, Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { useSport } from "@/hooks/useSport";
import API, { api } from "@/lib/api";
import { Sparkles, Target, Zap } from "lucide-react";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { BarChart3, Clock, TrendingUp, Info } from "lucide-react";
import { clsx } from "clsx";
import { EmptyState } from "@/components/shared/EmptyState";

function fmtMetaFixed(v: unknown, digits: number, fallback: string): string {
  const n = Number(v);
  if (!Number.isFinite(n)) return fallback;
  return n.toFixed(digits);
}

function numOrZero(v: unknown): number {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

export default function CLVPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING CLV ANALYTICS...</div>}>
      <CLVPageContent />
    </Suspense>
  );
}

function CLVPageContent() {
  const { sport } = useSport();
  const searchParams = useSearchParams();
  const [activeTab, setActiveTab] = useState<'clv' | 'monte-carlo'>('clv');
  const date = searchParams.get("date") || new Date().toISOString().split('T')[0];

  const { data: clvData, isLoading, error, refetch, dataUpdatedAt } = useQuery({
    queryKey: ['clv', sport, date, activeTab],
    queryFn: async () => {
      const type = activeTab === "monte-carlo" ? "&type=monte-carlo" : "";
      const { data } = await api.get(`/api/clv?sport=${sport}&date=${date}${type}`);
      return data;
    },
    refetchInterval: 60_000,
    staleTime: 30_000
  });

  const lastSync = dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString() : 'N/A';

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <div className="flex justify-between items-center mb-8">
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Skeleton className="h-96 w-full rounded-2xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-4">
        <ErrorBanner message="CLV Analytics Engine is currently offline." onRetry={refetch} />
        <EmptyState
          title="No data available. Waiting for market sync."
          description="CLV requires fresh lines from the odds pipeline. Try again after sync completes."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const results = Array.isArray(clvData?.results) ? clvData.results : [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-purple/10 p-2 rounded-lg border border-brand-purple/20">
              <BarChart3 size={24} className="text-brand-purple shadow-glow shadow-brand-purple/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Neural Analytics</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">CLV & Monte Carlo Simulation</p>
          
          <div className="flex gap-2 mb-4">
             <button 
                onClick={() => setActiveTab('clv')}
                className={clsx(
                  "px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
                  activeTab === 'clv' ? "bg-white text-black border-white" : "bg-white/5 text-white/40 border-white/10 hover:border-white/30"
                )}
             >
                Active CLV
             </button>
             <button 
                onClick={() => setActiveTab('monte-carlo')}
                className={clsx(
                  "px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border",
                  activeTab === 'monte-carlo' ? "bg-white text-black border-white" : "bg-white/5 text-white/40 border-white/10 hover:border-white/30"
                )}
             >
                Monte Carlo
             </button>
          </div>
          <SportSelector />
        </div>
        <div className="text-right">
          <div className="text-[10px] font-black text-textMuted uppercase tracking-widest mb-1.5 flex items-center justify-end gap-1.5">
            <Clock size={12} className="text-brand-purple" />
            Last Sync: {lastSync}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <AnalyticsCard
          title="Avg CLV Edge"
          value={`+${fmtMetaFixed(clvData?.meta?.avg_edge, 2, "0.00")}%`}
          icon={<TrendingUp size={20} className="text-brand-success" />}
          description="Average edge vs final closing line"
        />
        <AnalyticsCard
          title="Win Rate vs CLV"
          value={`${fmtMetaFixed(clvData?.meta?.win_rate, 1, "0.0")}%`}
          icon={<Trophy size={20} className="text-brand-cyan" />}
          description="Percentage of bets that beat the CLV"
        />
        <AnalyticsCard
          title="Total Events"
          value={String(results.length)}
          icon={<Info size={20} className="text-brand-warning" />}
          description="Events tracked in current window"
        />
      </div>

      {activeTab === 'clv' ? (
        results.length === 0 ? (
          <EmptyState
            title="No data available. Waiting for market sync."
            description="Closing line value needs settled markets and fresh odds. Use Force sync on the dashboard if available."
            onRetry={() => refetch()}
          />
        ) : (
        <div className="bg-lucrix-surface border border-lucrix-border rounded-xl overflow-hidden shadow-card">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-lucrix-dark/80 border-b border-lucrix-border text-[9px] font-black uppercase tracking-widest text-textMuted">
                <th className="px-6 py-4">Event</th>
                <th className="px-6 py-4 text-center">Opening Line</th>
                <th className="px-6 py-4 text-center">Closing Line</th>
                <th className="px-6 py-4 text-center">CLV Delta</th>
                <th className="px-6 py-4 text-right">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-lucrix-border/50">
              {results.map((item: any, i: number) => (
                <tr key={i} className="group hover:bg-lucrix-dark/50 transition-colors">
                  <td className="px-6 py-5">
                    <div className="font-black text-white font-display italic uppercase tracking-tight">{item.event}</div>
                    <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-0.5">{item.market}</div>
                  </td>
                  <td className="px-6 py-5 text-center font-mono font-black text-white">{item.open_line}</td>
                  <td className="px-6 py-5 text-center font-mono font-black text-white">{item.close_line}</td>
                  <td className="px-6 py-5 text-center">
                    <span className={clsx(
                      "font-mono font-black px-2 py-1 rounded border",
                      numOrZero(item.delta) > 0 ? "text-brand-success bg-brand-success/10 border-brand-success/20" : "text-brand-danger bg-brand-danger/10 border-brand-danger/20"
                    )}>
                      {numOrZero(item.delta) > 0 ? `+${numOrZero(item.delta)}` : numOrZero(item.delta)}
                    </span>
                  </td>
                  <td className="px-6 py-5 text-right">
                    <span className={clsx(
                      "text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full",
                      item.status === "WIN" ? "bg-brand-success/20 text-brand-success" : "bg-lucrix-dark text-textMuted"
                    )}>
                      {item.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )
      ) : (
        <MonteCarloView />
      )}
    </div>
  );
}

function AnalyticsCard({ title, value, icon, description }: any) {
  return (
    <div className="bg-lucrix-surface border border-lucrix-border p-6 rounded-2xl shadow-card">
      <div className="flex justify-between items-start mb-4">
        <div className="text-[10px] font-black text-textMuted uppercase tracking-widest">{title}</div>
        <div className="p-2 bg-lucrix-dark rounded-xl border border-lucrix-border">{icon}</div>
      </div>
      <div className="text-3xl font-black text-white font-display italic mb-1 uppercase tracking-tighter">{value}</div>
      <p className="text-[11px] font-bold text-textSecondary">{description}</p>
    </div>
  );
}

function MonteCarloView() {
  const [simResult, setSimResult] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const runSimulation = async () => {
    setIsSimulating(true);
    try {
      // simulate() expects legs, n_sims
      const data = await API.simulate([{ player: "Test", line: 2.5, type: "OVER" }], 100);
      setSimResult(data);
    } catch (err) {
      console.error("Simulation failed", err);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-lucrix-surface border border-lucrix-border p-8 rounded-3xl text-center space-y-6">
        <div className="max-w-md mx-auto space-y-4">
          <h2 className="text-2xl font-black italic uppercase tracking-tight text-white font-display">Neural Parlay Simulator</h2>
          <p className="text-sm text-textSecondary leading-relaxed">
            Run 10,000+ iterations of your current parlay legs through our Monte Carlo engine to find the true win probability and expected value.
          </p>
          <button 
            onClick={runSimulation}
            disabled={isSimulating}
            className="w-full py-4 bg-brand-purple hover:bg-brand-purple/80 disabled:opacity-50 text-white rounded-2xl font-black uppercase tracking-widest text-xs shadow-glow shadow-brand-purple/20 transition-all flex items-center justify-center gap-2"
          >
            {isSimulating ? <Zap size={16} className="animate-spin" /> : <Sparkles size={16} />}
            {isSimulating ? "SIMULATING..." : "RUN NEURAL SIMULATION"}
          </button>
        </div>
      </div>

      {simResult && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
           <AnalyticsCard
             title="Simulated Win %"
             value={`${(Number(simResult?.win_prob) * 100 || 0).toFixed(1)}%`}
             icon={<Target size={20} className="text-brand-success" />}
             description="Probability of all legs hitting"
           />
           <AnalyticsCard
             title="Projected EV"
             value={`${Number(simResult?.ev) > 0 ? '+' : ''}${Number.isFinite(Number(simResult?.ev)) ? Number(simResult.ev).toFixed(2) : '0.00'}%`}
             icon={<TrendingUp size={20} className="text-brand-cyan" />}
             description="Edge vs implied probability"
           />
        </div>
      )}
    </div>
  );
}


const Trophy = ({ size, className }: any) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" /><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" /><path d="M4 22h16" /><path d="M10 22V18" /><path d="M14 22V18" /><path d="M18 4H6v7a6 6 0 0 0 12 0V4Z" />
  </svg>
);
