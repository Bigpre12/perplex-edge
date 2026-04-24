"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import { DISPLAY_SPORTS, SPORTS_CONFIG, SportKey } from "@/lib/sports.config";
import { useAuth } from "@/hooks/useAuth";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";

const PILL_LABELS = ["NBA", "NFL", "MLB", "NHL", "NCAAF", "NCAAB", "WNBA", "EPL", "UCL", "UFC", "MLS"];
const PILL_SPORTS = DISPLAY_SPORTS.filter((k) => PILL_LABELS.includes(SPORTS_CONFIG[k].label)).sort(
  (a, b) => PILL_LABELS.indexOf(SPORTS_CONFIG[a].label) - PILL_LABELS.indexOf(SPORTS_CONFIG[b].label)
);

type MoveRow = { id: string; event: string; market: string; open: string; current: string; move: number; side: string; time: string; isSharp: boolean };

export default function MovePage() {
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const [sport, setSport] = useState<SportKey>("basketball_nba");
  const [rows, setRows] = useState<MoveRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !token) router.replace("/login");
  }, [authLoading, token, router]);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/api/sharp/signals?sport=${sport}&limit=50`);
        const json = await res.json();
        const data = Array.isArray(json?.data) ? json.data : Array.isArray(json?.items) ? json.items : Array.isArray(json) ? json : [];
        const mapped: MoveRow[] = data.map((r: any, idx: number) => ({
          id: String(r?.id ?? idx),
          event: r?.selection ?? r?.event ?? "—",
          market: r?.market_key ?? r?.market ?? "—",
          open: r?.line_open != null ? String(r.line_open) : "—",
          current: r?.line_current != null ? String(r.line_current) : "—",
          move: Number(r?.line_movement ?? r?.severity ?? 0) || 0,
          side: r?.signal_type ?? "—",
          time: r?.detected_at ?? r?.created_at ?? "",
          isSharp: String(r?.signal_type ?? "").toLowerCase().includes("steam") || String(r?.signal_type ?? "").toLowerCase().includes("sharp"),
        }));
        if (mounted) setRows(mapped);
      } catch {
        if (mounted) {
          setRows([]);
          setError("Unable to connect to backend. Data will populate once API is online.");
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, [sport]);

  const stats = useMemo(() => {
    const active = rows.length;
    const steam = rows.filter((r) => r.isSharp).length;
    const rlm = rows.filter((r) => r.move < 0).length;
    const avg = active ? rows.reduce((s, r) => s + Math.abs(r.move), 0) / active : 0;
    return { active, steam, rlm, avg };
  }, [rows]);

  if (authLoading || !token) return <LoadingSkeleton rows={5} />;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-black uppercase tracking-tight">Line <span className="text-cyan-400">Movement</span></h1>
        <p className="text-white/50 text-sm">Track steam moves and sharp line shifts in real time</p>
      </div>
      {error ? <div className="border border-red-500/30 bg-red-500/10 p-3 rounded-xl text-sm">{error}</div> : null}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {[
          ["ACTIVE MOVES", String(stats.active)],
          ["STEAM ALERTS", String(stats.steam)],
          ["REVERSE LINE", String(stats.rlm)],
          ["AVG MOVE SIZE", stats.avg.toFixed(2)],
        ].map(([k, v]) => <div key={k} className="bg-[#111] border border-[#222] rounded-xl p-4"><div className="text-[10px] uppercase font-black text-white/50">{k}</div><div className="text-xl font-black">{v}</div></div>)}
      </div>
      <div className="flex flex-wrap gap-2">
        {PILL_SPORTS.map((k) => <button key={k} onClick={() => setSport(k)} className={`px-3 py-1 rounded-full border text-xs font-black uppercase ${sport === k ? "bg-cyan-500 text-black border-cyan-500" : "bg-[#111] border-[#222] text-white/70"}`}>{SPORTS_CONFIG[k].label}</button>)}
      </div>

      {loading ? (
        <LoadingSkeleton rows={5} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="border border-[#222] rounded-xl overflow-hidden">
            <div className="bg-[#111] px-3 py-2 text-[10px] uppercase font-black text-white/60">Steam Moves</div>
            <table className="w-full text-sm">
              <thead className="bg-[#111] text-white/50 text-[10px] uppercase"><tr>{["EVENT","MARKET","OPEN","CURRENT","MOVE","SIDE","TIME"].map((h)=><th key={h} className="px-2 py-2 text-left">{h}</th>)}</tr></thead>
              <tbody>
                {rows.length === 0 ? <tr><td colSpan={7} className="text-center py-10 text-white/40">No data available</td></tr> : rows.map((r) => (
                  <tr key={r.id} className="border-t border-[#222]">
                    <td className="px-2 py-2">{r.event}</td><td className="px-2 py-2">{r.market}</td><td className="px-2 py-2">{r.open}</td><td className="px-2 py-2">{r.current}</td>
                    <td className={`px-2 py-2 font-black ${r.move >= 0 ? "text-green-400" : "text-red-400"}`}>{r.move >= 0 ? "+" : ""}{r.move.toFixed(2)}</td>
                    <td className="px-2 py-2">{r.side}</td><td className="px-2 py-2">{r.time ? new Date(r.time).toLocaleTimeString() : "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="border border-[#222] rounded-xl p-3">
            <div className="text-[10px] uppercase font-black text-white/60 mb-2">Sharp Alerts</div>
            <div className="space-y-2">
              {rows.length === 0 ? <div className="text-white/40 text-center py-10">No data available</div> : rows.slice(0, 12).map((r) => (
                <div key={`feed-${r.id}`} className="bg-[#111] border border-[#222] rounded-lg p-3">
                  <div className="font-bold">{r.event}</div>
                  <div className="text-xs text-white/60">{r.market}</div>
                  <div className="text-sm mt-1">{r.move >= 0 ? <span className="text-green-400">▲</span> : <span className="text-red-400">▼</span>} {Math.abs(r.move).toFixed(2)} • {r.time ? `${Math.max(0, Math.floor((Date.now()-new Date(r.time).getTime())/60000))}m ago` : "recent"}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
