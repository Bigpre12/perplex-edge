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

type HistoryRow = { id: string; date: string; sport: string; player: string; market: string; line: string; result: string; ev: number; clv: number };

export default function HistoryPage() {
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const [sport, setSport] = useState<SportKey>("basketball_nba");
  const [period, setPeriod] = useState("Last 30d");
  const [resultFilter, setResultFilter] = useState("All");
  const [page, setPage] = useState(1);
  const [rows, setRows] = useState<HistoryRow[]>([]);
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
        const periodMap: Record<string, string> = { "Last 7d": "7d", "Last 30d": "30d", "This Month": "month", "All Time": "all" };
        const resultMap: Record<string, string> = { All: "all", Won: "won", Lost: "lost", Push: "push" };
        const url = `${API_BASE}/api/picks/history?sport=${sport}&period=${periodMap[period]}&result=${resultMap[resultFilter]}&page=${page}&limit=50`;
        let json = await fetch(url).then((r) => r.json());
        let data = Array.isArray(json?.data) ? json.data : Array.isArray(json?.items) ? json.items : Array.isArray(json) ? json : null;
        if (!data) {
          json = await fetch(`${API_BASE}/api/brain/picks?limit=200`).then((r) => r.json());
          data = Array.isArray(json?.data) ? json.data : Array.isArray(json) ? json : [];
        }
        let mapped: HistoryRow[] = data.map((r: any, idx: number) => ({
          id: String(r?.id ?? idx),
          date: r?.created_at ?? r?.date ?? "",
          sport: r?.sport ?? sport,
          player: r?.player_name ?? r?.selection ?? "—",
          market: r?.market ?? r?.market_key ?? "—",
          line: r?.line != null ? String(r.line) : "—",
          result: String(r?.result ?? r?.status ?? "PENDING").toUpperCase(),
          ev: Number(r?.ev_at_time ?? r?.ev_value ?? 0) || 0,
          clv: Number(r?.clv ?? 0) || 0,
        }));
        mapped = mapped.filter((r) => r.sport === sport);
        if (resultFilter !== "All") mapped = mapped.filter((r) => r.result === resultFilter.toUpperCase());
        if (mounted) setRows(mapped.slice((page - 1) * 50, page * 50));
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
  }, [sport, period, resultFilter, page]);

  const stats = useMemo(() => {
    const graded = rows.filter((r) => ["WON", "LOST", "PUSH"].includes(r.result));
    const won = graded.filter((r) => r.result === "WON").length;
    const accuracy = graded.length ? (won / graded.length) * 100 : 0;
    const bySport: Record<string, number> = {};
    graded.forEach((r) => { bySport[r.sport] = (bySport[r.sport] || 0) + (r.result === "WON" ? 1 : 0); });
    const bestSport = Object.keys(bySport)[0] ?? "—";
    const streak = graded.reduce((s, r) => (r.result === "WON" ? s + 1 : 0), 0);
    return { accuracy, total: graded.length, bestSport, streak };
  }, [rows]);

  if (authLoading || !token) return <LoadingSkeleton rows={5} />;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-black uppercase tracking-tight">Pick <span className="text-cyan-400">History</span></h1>
        <p className="text-white/50 text-sm">Full record of all platform signals and their outcomes</p>
      </div>
      {error ? <div className="border border-red-500/30 bg-red-500/10 p-3 rounded-xl text-sm">{error}</div> : null}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {[
          ["ALL-TIME ACCURACY", `${stats.accuracy.toFixed(1)}%`],
          ["TOTAL PICKS GRADED", String(stats.total)],
          ["BEST SPORT", stats.bestSport],
          ["WIN STREAK", String(stats.streak)],
        ].map(([k, v]) => <div key={k} className="bg-[#111] border border-[#222] rounded-xl p-4"><div className="text-[10px] uppercase font-black text-white/50">{k}</div><div className="text-xl font-black">{v}</div></div>)}
      </div>

      <div className="flex flex-wrap gap-2">
        {PILL_SPORTS.map((k) => <button key={k} onClick={() => setSport(k)} className={`px-3 py-1 rounded-full border text-xs font-black uppercase ${sport === k ? "bg-cyan-500 text-black border-cyan-500" : "bg-[#111] border-[#222] text-white/70"}`}>{SPORTS_CONFIG[k].label}</button>)}
      </div>

      <div className="flex flex-wrap gap-2">
        <select value={period} onChange={(e) => setPeriod(e.target.value)} className="bg-[#111] border border-[#222] rounded px-3 py-1 text-xs"><option>Last 7d</option><option>Last 30d</option><option>This Month</option><option>All Time</option></select>
        <select value={resultFilter} onChange={(e) => setResultFilter(e.target.value)} className="bg-[#111] border border-[#222] rounded px-3 py-1 text-xs"><option>All</option><option>Won</option><option>Lost</option><option>Push</option></select>
      </div>

      {loading ? <LoadingSkeleton rows={5} /> : (
        <div className="border border-[#222] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-[#111] text-white/50 text-[10px] uppercase"><tr>{["DATE","SPORT","PLAYER","MARKET","LINE","RESULT","EV AT TIME","CLV"].map((h)=><th key={h} className="px-3 py-2 text-left">{h}</th>)}</tr></thead>
            <tbody>
              {rows.length === 0 ? <tr><td colSpan={8} className="text-center py-10 text-white/40">No data available</td></tr> : rows.map((r) => (
                <tr key={r.id} className="border-t border-[#222]">
                  <td className="px-3 py-2">{r.date ? new Date(r.date).toLocaleDateString() : "—"}</td><td className="px-3 py-2">{r.sport}</td><td className="px-3 py-2">{r.player}</td><td className="px-3 py-2">{r.market}</td><td className="px-3 py-2">{r.line}</td>
                  <td className="px-3 py-2"><span className={`px-2 py-1 rounded text-[10px] font-black ${r.result === "WON" ? "bg-green-500/20 text-green-300" : r.result === "LOST" ? "bg-red-500/20 text-red-300" : "bg-gray-500/20 text-gray-300"}`}>{r.result}</span></td>
                  <td className="px-3 py-2">{r.ev.toFixed(2)}%</td><td className={`px-3 py-2 ${r.clv >= 0 ? "text-green-300" : "text-red-300"}`}>{r.clv.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex justify-between p-3 border-t border-[#222] bg-[#111]">
            <button onClick={() => setPage((p) => Math.max(1, p - 1))} className="px-3 py-1 border border-[#333] rounded text-xs">← Prev</button>
            <span className="text-xs text-white/60">Page {page}</span>
            <button onClick={() => setPage((p) => p + 1)} className="px-3 py-1 border border-[#333] rounded text-xs">Next →</button>
          </div>
        </div>
      )}
    </div>
  );
}
