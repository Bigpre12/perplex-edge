"use client";

import React, { Suspense, useState } from "react";
import { useSport } from "@/hooks/useSport";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { History, TrendingUp, Activity, CheckCircle2, XCircle } from "lucide-react";
import { usePropsHistory, PropsHistoryRecord } from "@/hooks/usePropsHistory";
import { DataTable } from "@/components/shared/DataTable";
import { Sparklines, SparklinesLine, SparklinesSpots } from "react-sparklines";
import { clsx } from "clsx";
import { EmptyState } from "@/components/shared/EmptyState";

export default function PropsHistoryPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">RETRIEVING SETTLED DATA...</div>}>
      <PropsHistoryContent />
    </Suspense>
  );
}

function PropsHistoryContent() {
  const { sport } = useSport();
  const { data: history, isLoading, error, refetch } = usePropsHistory(sport);

  const columns = [
    { 
      header: 'Player / Event', 
      accessor: (p: PropsHistoryRecord) => (
        <div className="flex flex-col">
          <span className="font-bold text-white">{p.player_name}</span>
          <span className="text-[10px] text-white/40 uppercase font-mono">{p.market_key}</span>
        </div>
      ) 
    },
    { header: 'Line', accessor: (p: PropsHistoryRecord) => <span className="font-mono text-white/80">{p.line}</span> },
    { 
      header: 'Actual', 
      accessor: (p: PropsHistoryRecord) => (
         <span className="font-mono text-brand-cyan font-black">{p.actual_score ?? p.result_value ?? '—'}</span>
      )
    },
    { 
      header: 'Result', 
      accessor: (p: PropsHistoryRecord) => {
        const isHit = p.status === 'HIT';
        return (
          <div className={clsx(
            "flex items-center space-x-1.5 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest w-fit",
            isHit ? "bg-green-500/10 text-green-500 border border-green-500/20" : "bg-red-500/10 text-red-500 border border-red-500/20"
          )}>
            {isHit ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
            <span>{p.status}</span>
          </div>
        );
      }
    },
    {
      header: 'Trend',
      accessor: (p: PropsHistoryRecord) => (
        <div className="w-16 h-8 opacity-60 grayscale hover:grayscale-0 transition-all">
          <Sparklines data={p.history_sparkline || [10, 12, 8, 15, 10, 20]} margin={2}>
            <SparklinesLine color={p.status === 'HIT' ? "#10b981" : "#ef4444"} style={{ fill: "none", strokeWidth: 3 }} />
            <SparklinesSpots size={2} />
          </Sparklines>
        </div>
      )
    },
    { 
      header: 'Confidence', 
      accessor: (p: PropsHistoryRecord) => (
        <span className="text-[10px] font-black text-white/30 italic uppercase">
          {p.confidence ? `${(p.confidence * 100).toFixed(0)}%` : 'HIGH'}
        </span>
      )
    }
  ];

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="space-y-4">
          {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-16 w-full rounded-xl" />)}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 space-y-4">
        <ErrorBanner message="Settlement stream interrupted." onRetry={refetch} />
        <EmptyState
          title="No data available. Waiting for market sync."
          description="Settled props history requires graded results from the backend."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  const rows = Array.isArray(history) ? history : [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Activity size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Settlement Log</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Historical Verification & Model Grader</p>
          <SportSelector />
        </div>
        <div className="flex gap-4">
           <div className="bg-lucrix-surface border border-lucrix-border px-4 py-2 rounded-xl text-right">
             <div className="text-[8px] font-black text-textMuted uppercase tracking-widest">Global Win Rate</div>
             <div className="text-xl font-black text-white italic font-display">
               {rows.length ? ((rows.filter(p => p.status === 'HIT').length / rows.length) * 100).toFixed(1) : '00.0'}%
             </div>
           </div>
        </div>
      </div>

      <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl shadow-card overflow-hidden">
        <DataTable 
          columns={columns} 
          data={rows} 
          onRowClick={(p) => console.log('Historical record:', p)}
        />
      </div>

      {rows.length === 0 && (
        <EmptyState
          title="No data available. Waiting for market sync."
          description="No settled props for this sport yet. Grading runs after games complete."
          onRetry={() => refetch()}
        />
      )}
    </div>
  );
}
