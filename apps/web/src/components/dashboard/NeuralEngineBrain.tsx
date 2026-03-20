"use client";
import { useEffect, useState } from "react";
import { useSubscription } from "@/hooks/useSubscription";
import { API, isApiError } from "@/lib/api";
import { useSport } from "@/context/SportContext";

interface BrainData {
  props_scored:    number;
  injury_impacts:  number;
  decisions:       any[];
  active_edges:    number;
  clv_enabled:     boolean;
  brain_health:    string;
}

export default function NeuralEngineBrain() {
  const { isPro } = useSubscription();
  const isDev = typeof window !== 'undefined' && 
               (window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1' ||
                process.env.NEXT_PUBLIC_DEV_MODE === 'true');
  
  const { selectedSport } = useSport();
  const [mounted, setMounted] = useState(false);
  const [data, setData] = useState<BrainData>({ 
    props_scored: 0, 
    injury_impacts: 0, 
    decisions: [],
    active_edges: 0,
    clv_enabled: true,
    brain_health: 'initializing'
  });

  useEffect(() => {
    setMounted(true);
    const load = async () => {
      try {
        const brainStatus = await API.brain.status();
        if (!isApiError(brainStatus)) {
          const stats = (brainStatus as any).metrics || {};
          setData({
            props_scored: stats.props_scored_today ?? 0,
            injury_impacts: stats.injury_impacts ?? 0,
            decisions: stats.decisions ?? [],
            active_edges: stats.active_edges ?? stats.elite_signals ?? 0,
            clv_enabled: stats.clv_enabled ?? true,
            brain_health: (brainStatus as any).inference_engine ?? 'IDLE'
          });
        }
      } catch (err) {
        console.error("Brain data load error:", err);
      }
    };
    load();
    const interval = setInterval(load, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [selectedSport]);

  if (!mounted) {
    return (
      <div className="bg-lucrix-surface border border-lucrix-border rounded-xl p-6 min-h-[150px] animate-pulse shadow-card">
        <div className="h-4 w-32 bg-lucrix-elevated rounded mb-4" />
        <div className="grid grid-cols-3 gap-3">
          <div className="h-16 bg-lucrix-elevated rounded-lg" />
          <div className="h-16 bg-lucrix-elevated rounded-lg" />
          <div className="h-16 bg-lucrix-elevated rounded-lg" />
        </div>
        <div className="grid grid-cols-3 gap-3 mt-3">
          <div className="h-16 bg-lucrix-elevated rounded-lg" />
          <div className="h-16 bg-lucrix-elevated rounded-lg" />
          <div className="h-16 bg-lucrix-elevated rounded-lg" />
        </div>
      </div>
    );
  }

  const showAll = isPro || isDev;

  return (
    <div className="bg-lucrix-surface border border-lucrix-border rounded-xl p-6 shadow-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
            <span className="text-brand-success animate-pulse">⚡</span>
            <h2 className="text-sm font-black tracking-widest text-white uppercase font-display">Neural Engine Brain</h2>
        </div>
        <span className="text-[9px] bg-brand-success/10 border border-brand-success/20 text-brand-success px-1.5 py-0.5 rounded-sm uppercase tracking-widest font-black shrink-0">
          Connected
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-3">
        {/* Card 1 — Brain Decisions (tier-gated) */}
        {showAll ? (
          <BrainCard label="BRAIN DECISIONS" value={String(data.decisions.length)} />
        ) : (
          <LockedCard />
        )}
        {/* Card 2 — also tier-gated */}
        {showAll ? (
          <BrainCard label="ACTIVE EDGES" value={data.active_edges > 0 ? String(data.active_edges) : "Awaiting..."} />
        ) : (
          <LockedCard />
        )}
        {/* Card 3 — tier-gated */}
        {showAll ? (
          <BrainCard label="CLV TRACKED" value={data.clv_enabled ? "ON" : "OFF"} />
        ) : (
          <LockedCard />
        )}
      </div>

      <div className="grid grid-cols-3 gap-3">
        <BrainCard label="INJURY IMPACTS" value={data.injury_impacts > 0 ? `${data.injury_impacts} Critical` : "Awaiting..."} />
        <BrainCard label="PROPS SCORED"   value={data.props_scored > 0 ? String(data.props_scored) : "Awaiting..."} />
        {showAll ? (
          <BrainCard label="AI REASONING" value={data.brain_health === 'initializing' ? 'AWAITING...' : String(data.brain_health ?? 'ACTIVE').toUpperCase()} />
        ) : (
          <LockedCard />
        )}
      </div>
    </div>
  );
}

function BrainCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-lucrix-dark/50 border border-lucrix-border/50 rounded-lg p-3 text-center transition-colors hover:bg-lucrix-elevated">
      <p className="text-[10px] text-textMuted uppercase tracking-widest mb-1.5 font-bold">{label}</p>
      <p className="text-sm font-bold text-white font-mono">{value}</p>
    </div>
  );
}

function LockedCard() {
  return (
    <div className="bg-lucrix-dark/30 border border-lucrix-border/30 rounded-lg p-3 text-center flex flex-col items-center justify-center">
      <p className="text-[10px] font-black text-textMuted uppercase tracking-widest leading-none mb-1">ELITE</p>
      <p className="text-[9px] text-textSecondary font-medium leading-none">Upgrade to unlock</p>
    </div>
  );
}
