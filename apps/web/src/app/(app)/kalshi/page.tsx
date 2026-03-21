"use client";

import React, { Suspense } from "react";
import { useWSFallback } from "@/hooks/useWSFallback";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Activity, Zap, ArrowDown, ArrowUp, Clock, Info } from "lucide-react";
import { clsx } from "clsx";

export default function KalshiPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING PREDICTION MARKET...</div>}>
      <KalshiContent />
    </Suspense>
  );
}

function KalshiContent() {
  const { sport } = useSport();

  const { data: kalshiData, isLoading, isError, isWSOpen } = useWSFallback({
    wsEndpoint: "/api/ws_kalshi",
    queryKey: ["kalshi", sport],
    queryFn: () => fetch(`${API_BASE}/api/kalshi?sport=${sport}`).then(r => r.json()),
    refetchInterval: 10_000,
  });

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-96 w-full rounded-3xl" />
          <Skeleton className="h-96 w-full rounded-3xl" />
        </div>
      </div>
    );
  }

  if (isError) {
    return <div className="p-6"><ErrorBanner message="Kalshi Data Stream Offline." /></div>;
  }

  const markets = kalshiData?.markets || [];

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-purple/10 p-2 rounded-lg border border-brand-purple/20">
              <Activity size={24} className="text-brand-purple shadow-glow shadow-brand-purple/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Kalshi Markets</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">
            {isWSOpen ? "Live Order Book Stream" : "Polling Mode (10s)"}
          </p>
          <SportSelector />
        </div>
        <div className="text-right">
           <div className="flex gap-2 mb-2">
             <div className="bg-brand-success/10 px-2 py-0.5 rounded border border-brand-success/20 text-[8px] font-black text-brand-success uppercase tracking-widest">Exchange Grade</div>
             <div className="bg-brand-cyan/10 px-2 py-0.5 rounded border border-brand-cyan/20 text-[8px] font-black text-brand-cyan uppercase tracking-widest">Real Money</div>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {markets.map((market: any, i: number) => (
          <div key={i} className="bg-lucrix-surface border border-lucrix-border rounded-3xl overflow-hidden shadow-card hover:border-brand-purple/20 transition-all">
            <div className="p-6 border-b border-lucrix-border bg-lucrix-dark/30">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-black text-white font-display italic uppercase tracking-tight">{market.title}</h3>
                <div className="bg-lucrix-dark px-3 py-1.5 rounded-xl border border-lucrix-border font-mono font-black text-brand-cyan text-xs">
                  {market.mid_price}% Prob
                </div>
              </div>
              <div className="flex items-center gap-4 text-[9px] font-black text-textMuted uppercase tracking-widest">
                <span className="flex items-center gap-1.5"><Clock size={12} /> Expiry: {market.expiry}</span>
                <span className="flex items-center gap-1.5"><Zap size={12} /> Volume: {market.volume}</span>
              </div>
            </div>

            <div className="p-6">
               <div className="grid grid-cols-2 gap-6">
                 <div>
                   <div className="text-[9px] font-black text-brand-success uppercase tracking-widest mb-3 flex items-center justify-between">
                     <span>Bids (Yes)</span>
                     <ArrowUp size={10} />
                   </div>
                   <div className="space-y-1">
                      {market.bids?.slice(0, 5).map((bid: any, idx: number) => (
                        <div key={idx} className="flex justify-between items-center text-xs font-mono py-1 border-b border-lucrix-border/30 px-1 opacity-80 hover:opacity-100 transition-opacity">
                           <span className="font-black text-brand-success">¢{bid.price}</span>
                           <span className="text-textMuted font-bold">{bid.size}</span>
                        </div>
                      ))}
                   </div>
                 </div>
                 <div>
                   <div className="text-[9px] font-black text-brand-danger uppercase tracking-widest mb-3 flex items-center justify-between">
                     <span>Asks (No)</span>
                     <ArrowDown size={10} />
                   </div>
                   <div className="space-y-1">
                      {market.asks?.slice(0, 5).map((ask: any, idx: number) => (
                        <div key={idx} className="flex justify-between items-center text-xs font-mono py-1 border-b border-lucrix-border/30 px-1 opacity-80 hover:opacity-100 transition-opacity">
                           <span className="font-black text-brand-danger">¢{ask.price}</span>
                           <span className="text-textMuted font-bold">{ask.size}</span>
                        </div>
                      ))}
                   </div>
                 </div>
               </div>
               
               <div className="mt-8 pt-6 border-t border-lucrix-border">
                 <div className="flex justify-between items-end">
                    <div>
                      <div className="text-[8px] font-black text-textMuted uppercase mb-1">Implied Probability</div>
                      <div className="h-1.5 w-48 bg-lucrix-dark rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-brand-purple shadow-glow shadow-brand-purple/40 transition-all duration-700" 
                          style={{ width: `${market.mid_price}%` }} 
                        />
                      </div>
                    </div>
                    <button className="bg-white text-black px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-brand-purple hover:text-white transition-all shadow-glow shadow-brand-purple/10">
                      Predict on Kalshi →
                    </button>
                 </div>
               </div>
            </div>
          </div>
        ))}

        {markets.length === 0 && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest bg-lucrix-dark/20 rounded-3xl border border-dashed border-lucrix-border">
            <Info size={32} className="mx-auto mb-4 opacity-20" />
            <p>Scanning prediction markets for event liquidity...</p>
          </div>
        )}
      </div>
    </div>
  );
}
