"use client";

import React, { useState, Suspense, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";

import { api } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import SportSelector from "@/components/shared/SportSelector";
import { ArrowRightLeft, Calculator, Zap, Star, Info, Scaling } from "lucide-react";
import { clsx } from "clsx";
import { EmptyState } from "@/components/shared/EmptyState";

export default function ArbitragePage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING ARB SCANNER...</div>}>
      <ArbitrageContent />
    </Suspense>
  );
}

function ArbitrageContent() {
  const { sport } = useSport();

  // On-demand computation trigger
  useEffect(() => {
    const triggerCompute = async () => {
      try {
        await fetch(`/api/compute?sport=${sport}`, { method: 'POST' });
        console.log(`[ARB] Intelligence cycle triggered for ${sport}`);
      } catch (err) {
        console.error("[ARB] Compute trigger failed:", err);
      }
    };
    triggerCompute();
  }, [sport]);
  const [totalStake, setTotalStake] = useState(100);

  const { data: arbData, isLoading, isError, refetch } = useQuery({
    queryKey: ['arbitrage', sport],
    queryFn: async () => {
      const { data } = await api.get(`/api/arbitrage?sport=${sport}`, {
        timeout: 10_000,
      });
      return data;
    },
    refetchInterval: 30_000,
    staleTime: 15_000,
    retry: false,
  });

  const isLocked = false;
  const isGateLoading = false;
  const opportunities = arbData?.opportunities || [];

  if (isLoading || isGateLoading) {
    return (
      <div className="space-y-6 pt-6 px-4">
        <Skeleton className="h-10 w-48 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-64 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-6 pt-10 max-w-lg mx-auto">
        <EmptyState
          title="No arbitrage opportunities found."
          description="Unable to connect to backend. Data will populate once API is online."
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  return (
    <div className="pb-24 space-y-8 pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-success/10 p-2 rounded-lg border border-brand-success/20">
              <ArrowRightLeft size={24} className="text-brand-success shadow-glow shadow-brand-success/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Arbitrage Scanner</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">Risk-Free Market Extraction</p>
          <SportSelector />
        </div>
        <div className="flex items-center gap-4 bg-lucrix-surface border border-lucrix-border rounded-xl px-4 py-2">
          <Calculator size={16} className="text-brand-success" />
          <span className="text-[10px] font-black text-white uppercase tracking-widest">Total Stake:</span>
          <input 
            type="number" 
            title="Total Stake Amount"
            aria-label="Total Stake Amount"
            className="bg-transparent text-white font-mono font-black text-sm w-20 outline-none border-b border-brand-success/20 focus:border-brand-success transition-colors" 
            value={totalStake} 
            onChange={(e) => setTotalStake(parseInt(e.target.value) || 0)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">


        {opportunities.map((opp: any, i: number) => {
          // Calculation logic
          const overOdds = opp.over_odds;
          const underOdds = opp.under_odds;
          
          const overMultiplier = overOdds > 0 ? (overOdds/100 + 1) : (100/Math.abs(overOdds) + 1);
          const underMultiplier = underOdds > 0 ? (underOdds/100 + 1) : (100/Math.abs(underOdds) + 1);
          
          const overProb = 1 / overMultiplier;
          const underProb = 1 / underMultiplier;
          const totalProb = overProb + underProb;
          
          const overStake = (overProb / totalProb) * totalStake;
          const underStake = (underProb / totalProb) * totalStake;
          const profit = (totalStake / totalProb) - totalStake;
          const profitPct = (profit / totalStake) * 100;

          return (
            <div 
              key={i} 
              className={clsx(
                "bg-lucrix-surface border rounded-2xl p-6 transition-all relative overflow-hidden group",
                "bg-lucrix-surface border rounded-2xl p-6 transition-all relative overflow-hidden group border-brand-success/20 hover:border-brand-success/40 shadow-card"
              )}
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <div className="text-lg font-black text-white font-display italic uppercase tracking-tight group-hover:text-brand-success transition-colors">{opp.player_name}</div>
                  <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-1">
                    {opp.market} — {opp.line}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-black text-brand-success font-display italic">+{profitPct.toFixed(2)}%</div>
                  <div className="text-[9px] font-black text-textMuted uppercase tracking-widest">Guaranteed Return</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <StakeBox 
                  side="OVER" 
                  odds={overOdds} 
                  book={opp.over_book} 
                  stake={overStake} 
                  payout={overStake * overMultiplier}
                />
                <StakeBox 
                  side="UNDER" 
                  odds={underOdds} 
                  book={opp.under_book} 
                  stake={underStake} 
                  payout={underStake * underMultiplier}
                />
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-lucrix-border">
                <div className="flex items-center gap-1.5 text-[9px] font-black text-textMuted uppercase tracking-widest italic">
                  <Info size={11} className="text-brand-success" />
                  Locked Profit: ${profit.toFixed(2)}
                </div>
                <div className="text-[9px] font-black text-textMuted uppercase tracking-widest">
                  Updated: Just Now
                </div>
              </div>
            </div>
          );
        })}

        {opportunities.length === 0 && (
          <div className="col-span-full">
            <EmptyState
              title="No arbitrage opportunities found."
              description="No data available. Waiting for market sync."
              onRetry={() => refetch()}
            />
          </div>
        )}
      </div>
    </div>
  );
}

function StakeBox({ side, odds, book, stake, payout }: any) {
  return (
    <div className="bg-lucrix-dark/50 border border-lucrix-border rounded-xl p-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">{side} @ {book}</span>
        <span className="font-mono font-black text-xs text-white">{odds > 0 ? `+${odds}` : odds}</span>
      </div>
      <div className="flex justify-between items-end">
        <div>
          <div className="text-[8px] font-black text-textMuted uppercase mb-0.5">Stake</div>
          <div className="text-lg font-black text-white font-mono">${stake.toFixed(2)}</div>
        </div>
        <div className="text-right">
          <div className="text-[8px] font-black text-textMuted uppercase mb-0.5">Payout</div>
          <div className="text-xs font-black text-brand-success font-mono">${payout.toFixed(2)}</div>
        </div>
      </div>
    </div>
  );
}
