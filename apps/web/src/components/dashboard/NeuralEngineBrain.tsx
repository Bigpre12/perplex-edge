"use client";

import React, { useEffect, useState } from "react";
import { API, isApiError } from "@/lib/api";
import { useSport } from "@/context/SportContext";
import { motion, AnimatePresence } from "framer-motion";
import { Cpu, Zap, Shield, Activity, BarChart, Lock } from "lucide-react";
import { useLucrixStore } from "@/store";

interface BrainData {
  props_scored:    number;
  injury_impacts:  number;
  decisions:       any[];
  active_edges:    number;
  clv_enabled:     boolean;
  brain_health:    string;
}

export default function NeuralEngineBrain() {
  const { userTier, backendOnline } = useLucrixStore();
  const isPro = userTier === 'pro' || userTier === 'elite';
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
          const stats = (brainStatus as any)?.metrics || (brainStatus as any)?.brain?.metrics || (brainStatus as any) || {};
          setData({
            props_scored: stats?.props_scored_today ?? stats?.props_scored ?? 0,
            injury_impacts: stats?.injury_impacts ?? 0,
            decisions: stats?.decisions ?? [],
            active_edges: stats?.active_edges ?? stats?.elite_signals ?? stats?.edges ?? 0,
            clv_enabled: stats?.clv_enabled ?? true,
            brain_health: (brainStatus as any)?.inference_engine ?? (brainStatus as any)?.brain?.status ?? 'IDLE'
          });
        }
      } catch (err) {
        console.error("Brain data load error:", err);
      }
    };
    load();
    const interval = setInterval(load, 60000);
    return () => clearInterval(interval);
  }, [selectedSport]);

  if (!mounted) {
    return (
      <div className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8 min-h-[250px] animate-pulse space-y-6">
        <div className="h-6 w-48 bg-white/5 rounded-lg" />
        <div className="grid grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <div key={i} className="h-20 bg-white/5 rounded-2xl" />)}
        </div>
      </div>
    );
  }

  const showAll = isPro || isDev;

  return (
    <div className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl relative overflow-hidden group">
      {/* Background Decorator */}
      <div className="absolute top-0 right-0 w-64 h-64 -mr-32 -mt-32 bg-brand-primary/10 rounded-full blur-[100px] animate-pulse" />
      
      <div className="flex items-center justify-between mb-8 relative z-10">
        <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-primary/20 rounded-xl border border-brand-primary/30 shadow-glow shadow-brand-primary/10">
                <Cpu size={20} className="text-brand-primary animate-pulse" />
            </div>
            <div>
                <h2 className="text-lg font-black italic tracking-tighter text-white uppercase leading-none mb-1">Neural Core</h2>
                <p className="text-[10px] text-textMuted font-black uppercase tracking-widest italic">Quantum Inference Matrix</p>
            </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-success/10 border border-brand-success/20">
            <span className="flex h-1.5 w-1.5 rounded-full bg-brand-success animate-ping" />
            <span className="text-[9px] font-black text-brand-success uppercase tracking-widest">Connected</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 relative z-10">
        <BrainCard 
            label="BRAIN DECISIONS" 
            value={showAll ? (backendOnline ? String(data.decisions.length) : "--") : null} 
            icon={<Zap size={14} className="text-brand-primary" />}
            isLocked={!showAll}
        />
        <BrainCard 
            label="ACTIVE EDGES" 
            value={showAll ? (backendOnline ? (data.active_edges > 0 ? String(data.active_edges) : "0") : "--") : null} 
            icon={<BarChart size={14} className="text-brand-cyan" />}
            isLocked={!showAll}
        />
        <BrainCard 
            label="CLV ENGINE" 
            value={showAll ? (data.clv_enabled ? "OPTIMIZED" : "STBY") : null} 
            icon={<Shield size={14} className="text-brand-success" />}
            isLocked={!showAll}
        />
        <BrainCard 
            label="INJURY IMPACT" 
            value={backendOnline ? (data.injury_impacts > 0 ? `${data.injury_impacts} ACT` : "NOMINAL") : "--"} 
            icon={<Activity size={14} className="text-brand-danger" />}
            color="text-brand-danger"
        />
        <BrainCard 
            label="PROPS SCORED"   
            value={backendOnline ? (data.props_scored > 0 ? String(data.props_scored) : "0") : "--"} 
            icon={<Activity size={14} className="text-brand-purple" />}
            color="text-brand-purple"
        />
        <BrainCard 
            label="AI REASONING" 
            value={showAll ? (data.brain_health === 'initializing' ? 'INITIALIZING' : String(data.brain_health ?? 'ACTIVE').toUpperCase()) : null} 
            icon={<Cpu size={14} className="text-brand-cyan" />}
            isLocked={!showAll}
        />
      </div>
    </div>
  );
}

function BrainCard({ label, value, icon, isLocked, color = "text-white" }: { label: string; value: string | null; icon: React.ReactNode; isLocked?: boolean; color?: string }) {
  return (
    <motion.div 
        whileHover={{ scale: 1.02 }}
        className="relative p-4 rounded-2xl bg-lucrix-dark/40 border border-white/5 hover:border-white/10 hover:bg-white/5 transition-all overflow-hidden group/card"
    >
        <div className="flex items-center gap-2 mb-3">
            {icon}
            <p className="text-[9px] text-textMuted uppercase tracking-widest font-black italic">{label}</p>
        </div>
        
        {isLocked ? (
            <div className="flex items-center gap-2">
                <Lock size={12} className="text-white/20" />
                <span className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em]">ELITE-ONLY</span>
            </div>
        ) : (
            <p className={`text-lg font-black italic tracking-tight uppercase ${color}`}>{value || "---"}</p>
        )}

        {/* Hover Glow */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 via-transparent to-transparent opacity-0 group-hover/card:opacity-100 transition-opacity" />
    </motion.div>
  );
}
