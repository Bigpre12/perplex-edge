'use client';

import React from 'react';
import { useHitRate, useHitRatePlayers, HitRateStats } from '@/hooks/useHitRate';
import { DataTable } from '@/components/shared/DataTable';
import { LoadingSkeleton } from '@/components/shared/LoadingSkeleton';
import { ErrorRetry } from '@/components/shared/ErrorRetry';
import { Trophy, TrendingUp, BarChart3, Activity } from 'lucide-react';
import { useSport } from '@/hooks/useSport';
import SportSelector from '@/components/shared/SportSelector';
import { clsx } from "clsx";
import DataFreshnessBanner from '@/components/shared/DataFreshnessBanner';

function safeDivide(a: number, b: number): number {
  if (b === 0 || !Number.isFinite(b)) return 0;
  return a / b;
}

/** Backend /by-player may use 0–100 or 0–1; cap display at 100%. */
function displayHitRatePct(raw: unknown): string {
  const n = Number(raw);
  if (!Number.isFinite(n)) return "—";
  let pct = n > 1 ? n : n * 100;
  if (!Number.isFinite(pct) || pct < 0) return "—";
  if (pct > 100) pct = 100;
  return `${pct.toFixed(1)}%`;
}

function displayRoiPct(raw: unknown): string {
  if (raw === undefined || raw === null) return "—";
  const n = Number(raw);
  if (!Number.isFinite(n)) return "—";
  const pct = Math.abs(n) > 1 ? n : n * 100;
  if (!Number.isFinite(pct)) return "—";
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct.toFixed(1)}%`;
}

function playerDisplayName(p: Record<string, unknown>): string {
  const o = p as { player_name?: unknown; player?: unknown; name?: unknown };
  const a = o.player_name ?? o.player ?? o.name;
  return typeof a === "string" && a.length > 0 ? a : "Unknown Player";
}

/** Stat card: overall hit rate may be fraction (0–1) or percent (0–100). */
function statPlatformAccuracyPct(stats: HitRateStats | unknown[] | undefined): string {
  const raw = !Array.isArray(stats)
    ? (stats as HitRateStats | undefined)?.overall_hit_rate
    : (stats as { hit_rate?: number }[])?.[0]?.hit_rate;
  const n = Number(raw);
  if (!Number.isFinite(n)) return "0%";
  const pct = n > 1 ? n : n * 100;
  const capped = Math.min(Math.max(pct, 0), 100);
  return `${Math.round(capped)}%`;
}

function statAverageRoi(stats: HitRateStats | unknown[] | undefined): string {
  const raw = !Array.isArray(stats)
    ? (stats as HitRateStats | undefined)?.roi
    : (stats as { roi?: number }[])?.[0]?.roi;
  const s = displayRoiPct(raw);
  return s === "—" ? "0.0%" : s;
}

function statGradedPicks(stats: HitRateStats | unknown[] | undefined): string {
  const n = !Array.isArray(stats)
    ? (stats as HitRateStats | undefined)?.graded_picks
    : (stats as unknown[])?.length;
  const num = Number(n);
  return Number.isFinite(num) ? String(Math.round(num)) : "0";
}

export default function HitRatePage() {
  const { sport } = useSport();
  const { data: stats, isLoading: statsLoading, isError: statsError, lastUpdated } = useHitRate(sport);
  const { 
    data: players, 
    isLoading: playersLoading, 
    isError: playersError, 
    refetch 
  } = useHitRatePlayers(sport);

  const columns = [
    { 
      header: 'Player', 
      accessor: (p: any) => (
        <span className="font-bold text-white">{playerDisplayName(p)}</span>
      ) 
    },
    { 
      header: 'Hit Rate', 
      accessor: (p: any) => {
        const hits = Number(p.hits);
        const total = Number(p.total_picks ?? p.picks ?? p.sample_size);
        const derived =
          Number.isFinite(hits) && Number.isFinite(total) && total > 0
            ? safeDivide(hits, total) * 100
            : Number(p.hit_rate);
        return (
        <span className="text-green-400 font-black">{displayHitRatePct(derived)}</span>
        );
      }
    },
    { 
      header: 'ROI', 
      accessor: (p: any) => {
        const roiNum = Number(p.roi);
        const pos = Number.isFinite(roiNum) && roiNum > 0;
        const neg = Number.isFinite(roiNum) && roiNum < 0;
        return (
        <span className={`font-mono ${pos ? 'text-green-400' : neg ? 'text-red-400' : 'text-white/50'}`}>
          {displayRoiPct(p.roi)}
        </span>
        );
      }
    },
    { header: 'Total Picks', accessor: (p: any) => p.total_picks ?? p.picks ?? p.sample_size ?? '—', className: 'text-white/40' },
    { 
      header: 'Streak', 
      accessor: (p: any) => {
        const s = p.streak;
        const n = typeof s === 'number' ? s : NaN;
        if (!Number.isFinite(n)) return <span className="text-xs font-bold text-white/40">—</span>;
        return (
        <span className={`text-xs font-bold ${n > 0 ? 'text-green-500' : 'text-red-500'}`}>
          {n > 0 ? `W${n}` : n < 0 ? `L${Math.abs(n)}` : '-'}
        </span>
        );
      }
    },
  ];

  const StatCard = ({ label, value, icon: Icon, color }: { label: string, value: string, icon: any, color: 'blue' | 'green' | 'purple' | 'yellow' }) => {
    const colorMap = {
      blue: { bg: 'bg-blue-500/20', text: 'text-blue-400', blur: 'bg-blue-500/10' },
      green: { bg: 'bg-green-500/20', text: 'text-green-400', blur: 'bg-green-500/10' },
      purple: { bg: 'bg-purple-500/20', text: 'text-purple-400', blur: 'bg-purple-500/10' },
      yellow: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', blur: 'bg-yellow-500/10' }
    };

    const style = colorMap[color];

    return (
      <div className="bg-white/5 border border-white/10 p-6 rounded-3xl relative overflow-hidden">
        <div className="flex justify-between items-start relative z-10">
          <div>
            <p className="text-white/40 text-xs font-black uppercase tracking-widest mb-1">{label}</p>
            <h3 className="text-3xl font-black">{value}</h3>
          </div>
          <div className={clsx("p-2 rounded-xl", style.bg, style.text)}>
            <Icon className="w-5 h-5" />
          </div>
        </div>
        <div className={clsx("absolute bottom-0 right-0 p-4 blur-2xl w-24 h-24 rounded-full -mr-12 -mb-12", style.blur)} />
      </div>
    );
  };

  const isLoading = statsLoading || playersLoading;
  const isError = statsError || playersError;

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 pb-24">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Header */}
        <div className="flex flex-col space-y-4">
           <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 text-[10px] font-black uppercase tracking-[0.2em] w-fit">
              <Trophy className="w-3 h-3" />
              <span>Performance Analytics</span>
           </div>
           <h1 className="text-5xl font-black tracking-tighter uppercase italic">
             HIT RATE <span className="text-blue-500 not-italic">TRACKER</span>
           </h1>
           <SportSelector />
           <DataFreshnessBanner lastUpdated={lastUpdated} label="Hit-rate sync" />
        </div>

        {/* Global Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
           <StatCard 
             label="Platform Accuracy" 
             value={statPlatformAccuracyPct(stats)} 
             icon={Activity} 
             color="blue" 
           />
           <StatCard 
             label="Average ROI" 
             value={statAverageRoi(stats)} 
             icon={TrendingUp} 
             color="green" 
           />
           <StatCard 
             label="Graded Picks" 
             value={statGradedPicks(stats)} 
             icon={BarChart3} 
             color="purple" 
           />
           <StatCard 
             label="Accuracy Trend" 
             value={
               !Array.isArray(stats) && stats?.streak != null && Number.isFinite(Number(stats.streak))
                 ? String(stats.streak)
                 : "—"
             } 
             icon={Trophy} 
             color="yellow" 
           />
        </div>

        <div className="flex justify-end">
           <button 
             onClick={async () => {
                const confirmed = confirm("This will trigger a final score pull and grade all of yesterday's pending props. Proceed?");
                if (!confirmed) return;
                try {
                  const res = await fetch('/backend/api/admin/trigger-ingestion', { method: 'POST' });
                  const data = await res.json();
                  alert(`Sync requested: ${data.status || "ok"}.`);
                  refetch();
                } catch (e) {
                  alert("Grading service failed to respond.");
                }
             }}
             className="text-[10px] font-black uppercase tracking-widest text-white/40 hover:text-blue-400 transition-colors border border-white/10 px-4 py-2 rounded-xl"
           >
             Trigger Result Sync ↻
           </button>
        </div>

        {/* Leaderboard Table */}
        <div className="space-y-6">
           <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-black uppercase italic tracking-tight">
                  Player <span className="text-blue-500 not-italic">Leaderboard</span>
                </h2>
                <p className="text-white/30 text-sm">Top performers across all tracked athletes.</p>
              </div>
           </div>

           {isLoading ? (
             <LoadingSkeleton rows={10} />
           ) : isError ? (
             <ErrorRetry onRetry={() => refetch()} />
           ) : (
             <DataTable 
               columns={columns} 
               data={players || []} 
               onRowClick={(p) => console.log('Clicked player:', p)}
             />
           )}
        </div>
      </div>
    </div>
  );
}
