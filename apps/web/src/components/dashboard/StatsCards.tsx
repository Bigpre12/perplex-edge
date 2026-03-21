"use client";

import React, { useEffect, useState } from "react";
import { API, isApiError } from "@/lib/api";
import ApiHealthCard from "./ApiHealthCard";
import { TrendingUp, Zap, Activity, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import CountUp from "react-countup";

interface Stats {
  hit_rate:   number | null;
  avg_ev:     number | null;
  live_volume: number;
}

export default function StatsCards() {
  const [stats, setStats] = useState<Stats>({ hit_rate: null, avg_ev: null, live_volume: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const result = await API.brainMetrics();
        if (!isApiError(result)) {
          const data = result as any;
          setStats({
            hit_rate:    data?.hit_rate ?? data?.win_rate ?? data?.avg_confidence ?? null,
            avg_ev:      data?.avg_ev ?? null,
            live_volume: data?.total_picks ?? data?.live_volume ?? 0,
          });
        }
      } catch {
        // Keep nulls
      } finally {
        setLoading(false);
      }
    };
    load();
    const id = setInterval(load, 60_000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard 
        label="Quantum Hit Rate"  
        value={stats.hit_rate} 
        suffix="%" 
        icon={<TrendingUp size={14} className="text-brand-success" />} 
        loading={loading} 
        color="text-brand-success"
      />
      <StatCard 
        label="Mean Alpha (EV)"     
        value={stats.avg_ev} 
        suffix="%" 
        icon={<ShieldCheck size={14} className="text-brand-cyan" />} 
        loading={loading} 
        color="text-brand-cyan"
      />
      <StatCard 
        label="Compute Volume"    
        value={stats.live_volume} 
        badge="Active" 
        icon={<Activity size={14} className="text-brand-purple" />} 
        loading={loading} 
        color="text-brand-purple"
      />
      <ApiHealthCard />
    </div>
  );
}

function StatCard({ label, value, suffix = "", badge, icon, loading, color }: {
  label: string; value: number | null; suffix?: string; badge?: string; icon: React.ReactNode; loading: boolean; color: string;
}) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl relative overflow-hidden group"
    >
      <div className="absolute top-0 right-0 w-24 h-24 -mr-12 -mt-12 bg-white/5 rounded-full blur-2xl group-hover:bg-white/10 transition-colors" />
      
      <div className="flex items-center justify-between mb-4 relative z-10">
        <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-lg bg-white/5 border border-white/5`}>
                {icon}
            </div>
            <p className="text-[10px] text-textMuted uppercase tracking-widest font-black leading-none italic">{label}</p>
        </div>
        {badge && (
            <span className="text-[8px] font-black bg-brand-success/10 border border-brand-success/20 text-brand-success px-2 py-0.5 rounded-md uppercase tracking-[0.2em] animate-pulse">
                {badge}
            </span>
        )}
      </div>
      
      <div className="relative z-10 flex items-baseline gap-1">
        <p className={`text-4xl font-black italic tracking-tighter leading-none ${color}`}>
            {loading || value === null ? "---" : (
                <CountUp end={value} decimals={value % 1 === 0 ? 0 : 1} duration={2} />
            )}
            {!loading && value !== null && <span className="text-xl ml-0.5 opacity-50 not-italic">{suffix}</span>}
        </p>
      </div>
      
      <div className="mt-4 flex items-center gap-2 relative z-10">
          <div className="flex-1 h-1 bg-white/5 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }}
                animate={{ width: "60%" }}
                className={`h-full opacity-50 rounded-full ${color.replace('text-', 'bg-')}`}
              />
          </div>
          <span className="text-[9px] font-black text-textMuted uppercase italic">Nominal</span>
      </div>
    </motion.div>
  );
}
