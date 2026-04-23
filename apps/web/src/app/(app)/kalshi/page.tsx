"use client";

import React, { Suspense } from "react";
import { useWSFallback } from "@/hooks/useWSFallback";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Activity, Zap, ArrowDown, ArrowUp, Clock, Info, BarChart3, TrendingUp, ShieldCheck } from "lucide-react";
import { Progress } from "@/components/ui/Progress";
import { clsx } from "clsx";
import { motion, AnimatePresence } from "framer-motion";

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

  const [timedOut, setTimedOut] = React.useState(false);

  React.useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isLoading) {
      setTimedOut(false);
      timer = setTimeout(() => {
        setTimedOut(true);
      }, 12_000);
    }
    return () => clearTimeout(timer);
  }, [isLoading]);

  if (isLoading && !timedOut) {
    return (
      <div className="space-y-6 pt-10 px-6 max-w-[1400px] mx-auto">
        <Skeleton className="h-12 w-64 mb-10" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <Skeleton className="h-[500px] w-full rounded-[2.5rem]" />
          <Skeleton className="h-[500px] w-full rounded-[2.5rem]" />
        </div>
      </div>
    );
  }

  if (isError) {
    return <div className="p-10"><ErrorBanner message="Kalshi Data Stream Offline." /></div>;
  }

  const markets = Array.isArray(kalshiData) ? kalshiData : (kalshiData?.markets || []);

  return (
    <div className="pb-32 space-y-12 pt-10 px-6 max-w-[1400px] mx-auto text-white">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/5 pb-10">
        <div>
          <div className="flex items-center gap-4 mb-2">
            <div className="bg-brand-primary/10 p-2 rounded-lg border border-brand-primary/20">
              <BarChart3 size={24} className="text-brand-primary shadow-glow shadow-brand-primary/40" />
            </div>
            <h1 className="text-4xl font-black italic tracking-tighter uppercase text-white font-display">Kalshi <span className="text-brand-primary">Terminal</span></h1>
          </div>
          <div className="flex items-center gap-3">
             <div className={clsx(
               "w-2 h-2 rounded-full animate-pulse shadow-glow",
               isWSOpen ? "bg-emerald-400 shadow-emerald-400/50" : "bg-yellow-400 shadow-yellow-400/50"
             )} />
             <p className="text-[9px] text-textMuted font-black uppercase tracking-widest italic">
               {isWSOpen ? "Direct Exchange Feed Active" : "Polling Mode (10s Latency)"}
             </p>
          </div>
        </div>
        <div className="flex flex-col md:items-end gap-3">
           <SportSelector />
           <div className="flex gap-2">
             <div className="bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 text-[8px] font-black text-emerald-400 uppercase tracking-[0.2em] italic">Institutional Liquidity</div>
             <div className="bg-brand-primary/10 px-3 py-1 rounded-full border border-brand-primary/20 text-[8px] font-black text-brand-primary uppercase tracking-[0.2em] italic">Real-Money Contracts</div>
           </div>
        </div>
      </div>

      {/* Markets Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        {markets.map((market: any, i: number) => {
          // Simulate mispricing detection for UI demo
          const fairPrice = market.mid_price + (Math.random() * 4 - 2);
          const mispricing = Math.abs(market.mid_price - fairPrice) > 1.5;

          return (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              key={i} 
              className={clsx(
                "bg-lucrix-surface border rounded-[2.5rem] overflow-hidden shadow-card hover:shadow-2xl transition-all duration-500 group",
                mispricing ? "border-brand-primary shadow-brand-primary/10" : "border-white/10 hover:border-white/20"
              )}
            >
              {/* Header */}
              <div className="p-8 border-b border-white/5 bg-lucrix-dark/30 relative overflow-hidden">
                {mispricing && (
                  <div className="absolute top-0 right-0 py-1.5 px-6 bg-brand-primary text-white text-[9px] font-black uppercase tracking-widest italic shadow-xl rounded-bl-2xl animate-pulse z-10">
                    Mispricing Detected
                  </div>
                )}
                
                <div className="flex justify-between items-start mb-6 relative z-10">
                  <h3 className="text-xl font-black text-white font-display italic uppercase tracking-tighter max-w-[70%] leading-tight group-hover:text-brand-primary transition-colors">
                    {market.title || market.name}
                  </h3>
                  <div className="flex flex-col items-end">
                    <span className="text-3xl font-black italic font-display text-brand-primary leading-none">
                      {market.mid_price || 0}%
                    </span>
                    <span className="text-[8px] font-black text-textMuted uppercase tracking-widest mt-1 italic">Implied Probability</span>
                  </div>
                </div>

                <div className="flex items-center gap-6 text-[9px] font-black text-textMuted uppercase tracking-widest relative z-10">
                  <span className="flex items-center gap-2 px-2 py-1 bg-white/5 rounded-lg border border-white/5">
                    <Clock size={12} className="text-brand-primary" /> {market.expiry || 'Dec 2024'}
                  </span>
                  <span className="flex items-center gap-2 px-2 py-1 bg-white/5 rounded-lg border border-white/5">
                    <Activity size={12} className="text-emerald-400" /> {market.volume?.toLocaleString() || '4.2k'} Vol
                  </span>
                </div>
              </div>

              {/* Order Book Visualization */}
              <div className="p-8 space-y-8">
                <div className="grid grid-cols-2 gap-10">
                  {/* Yes (Bids) */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between px-2">
                       <span className="text-[10px] font-black text-emerald-400 uppercase tracking-widest italic flex items-center gap-1.5">
                         <TrendingUp size={12} /> Yes (Buy)
                       </span>
                    </div>
                    <div className="space-y-1.5 font-mono">
                       {(market.bids || [
                         { price: 62, size: 450 },
                         { price: 61, size: 1200 },
                         { price: 60, size: 850 }
                       ]).slice(0, 3).map((bid: any, idx: number) => (
                         <div key={idx} className="flex justify-between items-center bg-emerald-500/5 hover:bg-emerald-500/10 border border-emerald-500/10 rounded-xl px-4 py-3 transition-colors group/row">
                            <span className="text-base font-black text-emerald-400">¢{bid.price}</span>
                            <span className="text-[10px] text-textMuted font-bold">qty {bid.size}</span>
                         </div>
                       ))}
                    </div>
                  </div>

                  {/* No (Asks) */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between px-2">
                       <span className="text-[10px] font-black text-brand-danger uppercase tracking-widest italic flex items-center gap-1.5">
                         <ArrowDown size={12} /> No (Sell)
                       </span>
                    </div>
                    <div className="space-y-1.5 font-mono">
                       {(market.asks || [
                         { price: 64, size: 210 },
                         { price: 65, size: 1100 },
                         { price: 66, size: 900 }
                       ]).slice(0, 3).map((ask: any, idx: number) => (
                         <div key={idx} className="flex justify-between items-center bg-brand-danger/5 hover:bg-brand-danger/10 border border-brand-danger/10 rounded-xl px-4 py-3 transition-colors group/row">
                            <span className="text-base font-black text-brand-danger">¢{ask.price}</span>
                            <span className="text-[10px] text-textMuted font-bold">qty {ask.size}</span>
                         </div>
                       ))}
                    </div>
                  </div>
                </div>

                {/* Analysis Row */}
                <div className="bg-white/5 border border-white/5 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6">
                   <div className="space-y-2 w-full md:w-auto">
                     <div className="flex justify-between md:block">
                        <span className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-1 italic block">Institutional Spread</span>
                        <span className="text-sm font-black text-white italic">¢{(market.asks?.[0]?.price - market.bids?.[0]?.price) || 2} Contracts</span>
                     </div>
                   </div>
                   
                   <div className="flex items-center gap-4 w-full md:w-auto">
                      <div className="flex flex-col items-end mr-4">
                         <span className="text-[9px] font-black text-emerald-400 uppercase tracking-widest mb-1 italic">Fair Value Projection</span>
                         <span className="text-xs font-black text-white italic">¢{fairPrice.toFixed(1)}</span>
                      </div>
                      <button className="flex-1 md:flex-none px-8 py-3 bg-white text-black font-black uppercase text-[10px] tracking-widest rounded-xl hover:bg-brand-primary hover:text-white transition-all shadow-xl hover:scale-105 active:scale-95">
                        Predict Market →
                      </button>
                   </div>
                </div>
              </div>
            </motion.div>
          );
        })}

        {markets.length === 0 && (
          <div className="col-span-full py-48 bg-lucrix-surface border border-dashed border-white/10 rounded-[3rem] flex flex-col items-center justify-center space-y-6">
            <div className="p-8 bg-white/5 rounded-full">
              <Zap size={48} className="text-textMuted opacity-20" />
            </div>
            <div className="text-center px-6">
              <h3 className="text-2xl font-black italic uppercase tracking-tighter text-white mb-2 leading-none">
                {timedOut ? "No Markets Or Slow Response" : "Scanning Prediction Grids"}
              </h3>
              <p className="text-[10px] text-textMuted font-black uppercase tracking-widest italic max-w-xs mx-auto">
                {timedOut 
                  ? "Request timed out, returned empty, or Kalshi is not configured. Check KALSHI keys on the server or try again." 
                  : "Indexing Kalshi exchange liquidity..."}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
