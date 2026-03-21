"use client";

import React, { Suspense } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Newspaper, Clock, TrendingUp, Zap, MessageSquare, ExternalLink } from "lucide-react";
import { clsx } from "clsx";

export default function NewsPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING NEWS HUB...</div>}>
      <NewsContent />
    </Suspense>
  );
}

function NewsContent() {
  const { sport } = useSport();

  const { data: news, isLoading, error, refetch } = useQuery({
    queryKey: ['news', sport],
    queryFn: () => fetch(`${API_BASE}/api/news?sport=${sport}`).then(r => r.json()),
    refetchInterval: 900_000, // 15 minutes
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-64 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="p-6"><ErrorBanner message="News Feed Interrupted." onRetry={refetch} /></div>;
  }

  const newsList = Array.isArray(news) ? news : news?.results || [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Newspaper size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Intel Hub</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Sentiment & Market Correlation</p>
          <SportSelector />
        </div>
        <div className="text-right">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center justify-end gap-1.5">
            <Clock size={12} className="text-brand-cyan" />
            Sync: 15m
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {newsList.map((item: any, i: number) => (
          <div key={i} className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 hover:border-brand-cyan/30 transition-all group relative overflow-hidden flex flex-col shadow-card">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-2">
                <span className="text-[8px] font-black text-brand-cyan uppercase tracking-widest bg-brand-cyan/10 px-1.5 py-0.5 rounded border border-brand-cyan/20 lowercase first-letter:uppercase">
                  {item.category || "General"}
                </span>
                <span className="text-[8px] font-black text-textMuted uppercase tracking-widest">{new Date(item.timestamp).toLocaleDateString()}</span>
              </div>
              <div className={clsx(
                "px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest border flex items-center gap-1",
                item.impact === "HIGH" ? "bg-brand-danger/10 text-brand-danger border-brand-danger/20" : 
                item.impact === "MEDIUM" ? "bg-brand-warning/10 text-brand-warning border-brand-warning/20" : 
                "bg-brand-success/10 text-brand-success border-brand-success/20"
              )}>
                <Zap size={10} /> Market Impact: {item.impact}
              </div>
            </div>

            <div className="flex-1">
              <h3 className="text-lg font-black text-white font-display italic uppercase tracking-tight group-hover:text-brand-cyan transition-colors mb-3 leading-tight">{item.headline}</h3>
              <p className="text-[11px] font-bold text-textSecondary italic leading-relaxed line-clamp-3 mb-6">"{item.summary}"</p>
            </div>

            <div className="mt-auto pt-4 border-t border-lucrix-border flex items-center justify-between">
              <div className="flex -space-x-2">
                {[1, 2].map((p) => (
                  <div key={p} className="w-6 h-6 rounded-full border border-lucrix-surface bg-lucrix-dark flex items-center justify-center text-[8px] font-black text-white">
                    {p}
                  </div>
                ))}
              </div>
              <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-[9px] font-black text-brand-cyan uppercase tracking-widest flex items-center gap-1.5 hover:underline">
                Read Direct <ExternalLink size={10} />
              </a>
            </div>
          </div>
        ))}
        {newsList.length === 0 && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest">
            Scanning institutional wire for market-moving intel...
          </div>
        )}
      </div>
    </div>
  );
}
