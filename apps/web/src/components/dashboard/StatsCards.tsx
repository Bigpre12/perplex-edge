"use client";
import { useEffect, useState } from "react";
import { API, isApiError } from "@/lib/api";
import ApiHealthCard from "./ApiHealthCard";

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
        // Try brain metrics endpoint
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
        // Keep nulls — display handles them
      } finally {
        setLoading(false);
      }
    };
    load();
    const id = setInterval(load, 60_000);
    return () => clearInterval(id);
  }, []);

  const fmt = (v: number | null, suffix = "") =>
    v === null ? "—" : `${v.toFixed(1)}${suffix}`;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="REC. HIT RATE"  value={fmt(stats.hit_rate, "%")}  loading={loading} />
      <StatCard label="AVERAGE EV"     value={fmt(stats.avg_ev,  "%")}  loading={loading} />
      <StatCard label="LIVE VOLUME"    value={String(stats.live_volume)} badge="Active" loading={loading} />
      <ApiHealthCard />  {/* reuse from Fix 2 */}
    </div>
  );
}

function StatCard({ label, value, badge, loading }: {
  label: string; value: string; badge?: string; loading: boolean;
}) {
  return (
    <div className="bg-lucrix-surface border border-lucrix-border rounded-xl p-5 shadow-sm hover:shadow-card transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs text-textSecondary uppercase tracking-widest font-black leading-none">{label}</p>
        {badge && <span className="text-[9px] font-black bg-brand-success/10 border border-brand-success/20 text-brand-success px-2 py-0.5 rounded-sm uppercase tracking-widest">{badge}</span>}
      </div>
      <p className={`text-3xl font-black text-white font-display mt-3 leading-none ${loading ? "animate-pulse opacity-40 text-transparent bg-lucrix-elevated rounded-md w-24 h-8" : ""}`}>
        {value}
      </p>
    </div>
  );
}
