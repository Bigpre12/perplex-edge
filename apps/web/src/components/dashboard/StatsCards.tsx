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
        // Try picks statistics endpoint
        const result = await API.picksStats();
        if (!isApiError(result)) {
          setStats({
            hit_rate:    result?.hit_rate ?? result?.win_rate ?? result?.avg_confidence ?? null,
            avg_ev:      result?.avg_ev ?? null,
            live_volume: result?.total_picks ?? 0,
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
    <div className="bg-[#0d1117] border border-white/10 rounded-xl p-5">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs text-gray-500 uppercase tracking-widest">{label}</p>
        {badge && <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">{badge}</span>}
      </div>
      <p className={`text-3xl font-bold text-white ${loading ? "animate-pulse opacity-40" : ""}`}>
        {value}
      </p>
    </div>
  );
}
