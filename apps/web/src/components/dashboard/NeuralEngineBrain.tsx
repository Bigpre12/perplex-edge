"use client";
import { useEffect, useState } from "react";
import { useSubscription } from "@/hooks/useSubscription";
import { API, isApiError } from "@/lib/api";

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
        // Props count
        const props = await API.playerProps(30, 50);
        if (!isApiError(props)) {
          setData(prev => ({ ...prev, props_scored: props?.total ?? props?.items?.length ?? 0 }));
        }
        // Injury impacts & Stats
        const stats = await API.picksStats();
        if (!isApiError(stats)) {
          setData(prev => ({ 
            ...prev, 
            injury_impacts: stats?.injury_impacts ?? stats?.injury_count ?? 0,
            active_edges: stats?.total_picks ?? 0
          }));
        }
        // Brain decisions & Health
        const brain = await API.brainDecisions(5);
        if (!isApiError(brain)) {
          setData(prev => ({ ...prev, decisions: brain?.items ?? brain?.decisions ?? [] }));
        }
        
        const health = await API.brainHealth();
        if (!isApiError(health)) {
          setData(prev => ({ 
            ...prev, 
            brain_health: health?.overall_status ?? health?.status ?? 'Active',
            clv_enabled: health?.clv_tracking ?? true
          }));
        }
      } catch (err) {
        console.error("Brain data load error:", err);
      }
    };
    load();
    const interval = setInterval(load, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  if (!mounted) {
    return (
      <div className="bg-[#0d1117] border border-white/10 rounded-xl p-6 min-h-[150px] animate-pulse">
        <div className="h-4 w-32 bg-white/5 rounded mb-4" />
        <div className="grid grid-cols-3 gap-3">
          <div className="h-16 bg-white/5 rounded-lg" />
          <div className="h-16 bg-white/5 rounded-lg" />
          <div className="h-16 bg-white/5 rounded-lg" />
        </div>
        <div className="grid grid-cols-3 gap-3 mt-3">
          <div className="h-16 bg-white/5 rounded-lg" />
          <div className="h-16 bg-white/5 rounded-lg" />
          <div className="h-16 bg-white/5 rounded-lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#0d1117] border border-white/10 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-green-400">⚡</span>
        <h2 className="text-sm font-bold tracking-widest text-white uppercase">Neural Engine Brain</h2>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-3">
        {/* Card 1 — Brain Decisions (tier-gated) */}
        {isPro ? (
          <BrainCard label="BRAIN DECISIONS" value={String(data.decisions.length)} />
        ) : (
          <LockedCard />
        )}
        {/* Card 2 — also tier-gated */}
        {isPro ? (
          <BrainCard label="ACTIVE EDGES" value={data.active_edges > 0 ? String(data.active_edges) : "Scanning..."} />
        ) : (
          <LockedCard />
        )}
        {/* Card 3 — tier-gated */}
        {isPro ? (
          <BrainCard label="CLV TRACKED" value={data.clv_enabled ? "ON" : "OFF"} />
        ) : (
          <LockedCard />
        )}
      </div>

      <div className="grid grid-cols-3 gap-3">
        <BrainCard label="INJURY IMPACTS" value={`${data.injury_impacts} Critical`} />
        <BrainCard label="PROPS SCORED"   value={String(data.props_scored)} />
        {isPro ? (
          <BrainCard label="AI REASONING" value={data.brain_health === 'initializing' ? 'BOOTING...' : data.brain_health?.toUpperCase() || 'ACTIVE'} />
        ) : (
          <LockedCard />
        )}
      </div>
    </div>
  );
}

function BrainCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-black/30 border border-white/10 rounded-lg p-3 text-center">
      <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">{label}</p>
      <p className="text-sm font-bold text-white">{value}</p>
    </div>
  );
}

function LockedCard() {
  return (
    <div className="bg-black/30 border border-white/10 rounded-lg p-3 text-center">
      <p className="text-xs font-bold text-gray-400 uppercase tracking-wide">PREMIUM</p>
      <p className="text-[10px] text-gray-600 mt-0.5">Upgrade to unlock</p>
    </div>
  );
}
