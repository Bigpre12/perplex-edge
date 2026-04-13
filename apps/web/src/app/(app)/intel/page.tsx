"use client";

import React, { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Radio, Zap, Shield, Clock, TrendingUp, Info } from "lucide-react";
import { clsx } from "clsx";

export default function IntelPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">GATHERING MARKET INTEL...</div>}>
      <IntelContent />
    </Suspense>
  );
}

function IntelContent() {
  const { sport } = useSport();

  const { data: intel, isLoading, error, refetch } = useQuery({
    queryKey: ['intel', sport],
    queryFn: () => fetch(`${API_BASE}/api/intel?sport=${sport}`).then(r => r.json()),
    refetchInterval: 60_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-64 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message="Intel Feed Interrupted." onRetry={refetch} /></div>;
  }

  const reports = intel?.reports || [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Radio size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Intel Feed</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Aggregated Institutional Signal Stream</p>
          <SportSelector />
        </div>
        <div className="text-right">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center justify-end gap-1.5">
            <Clock size={12} className="text-brand-cyan" />
            Live Sync: 60s
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {reports.map((report: any, i: number) => (
          <div key={i} className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 hover:border-brand-cyan/30 transition-all group overflow-hidden shadow-card">
            <div className="flex justify-between items-start mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-lucrix-dark rounded-xl border border-lucrix-border group-hover:bg-brand-cyan/10 transition-colors">
                  <Shield size={18} className="text-brand-cyan" />
                </div>
                <div>
                  <div className="text-lg font-black text-white font-display italic uppercase tracking-tight">{report.event}</div>
                  <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-0.5">{report.source} — {report.type}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1">Confidence</div>
                <div className="text-lg font-black text-brand-success font-display italic">{report.confidence}%</div>
              </div>
            </div>

            <div className="bg-lucrix-dark/50 border border-lucrix-border/50 rounded-xl p-4 mb-6">
              <p className="text-[11px] font-bold text-textSecondary italic leading-relaxed">
                "{report.summary || "High-volume sharp money detected on current market line. Institutional orders entering via Pinnacle with significant retail fade."}"
              </p>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex flex-col">
                  <span className="text-[8px] font-black text-textMuted uppercase mb-0.5">Vigorish</span>
                  <span className="text-xs font-black text-white italic">{report.vig || '4.2%'}</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[8px] font-black text-textMuted uppercase mb-0.5">Market Cap</span>
                  <span className="text-xs font-black text-white italic">{report.cap || '$2.4M'}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="bg-brand-success/10 px-2 py-1 rounded border border-brand-success/20 flex items-center gap-1">
                  <TrendingUp size={10} className="text-brand-success" />
                  <span className="text-[8px] font-black text-brand-success uppercase tracking-widest">Bullish</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        {reports.length === 0 && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            Awaiting fresh institutional intelligence...
          </div>
        )}
      </div>
    </div>
  );
}
