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

type EvRow = { id: string; player: string; market: string; line: string; fairOdds: string; bookOdds: string; ev: number; expires: string };

export default function EVPlusPage() {
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const [sport, setSport] = useState<SportKey>("basketball_nba");
  const [minEv, setMinEv] = useState(2);
  const [rows, setRows] = useState<EvRow[]>([]);
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
        const res = await fetch(`${API_BASE}/api/ev?sport=${sport}&min_ev=${minEv}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        const json = await res.json();
        const data = Array.isArray(json?.data)
          ? json.data
          : Array.isArray(json?.items)
            ? json.items
            : Array.isArray(json?.results)
              ? json.results
              : Array.isArray(json)
                ? json
                : [];
        const mapped: EvRow[] = data
          .map((r: any, idx: number) => ({
            id: String(r?.id ?? idx),
            player: r?.player_name ?? "—",
            market: r?.market_label ?? r?.market_key ?? "—",
            line: r?.line != null ? String(r.line) : "—",
            fairOdds: r?.fair_odds != null ? String(r.fair_odds) : "—",
            bookOdds: r?.book_odds != null ? String(r.book_odds) : "—",
            ev: Number(r?.ev_value ?? r?.ev_percentage ?? 0) || 0,
            expires: r?.expires_at ? new Date(r.expires_at).toLocaleTimeString() : "—",
          }))
          .sort((a: EvRow, b: EvRow) => b.ev - a.ev);
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
  }, [sport, minEv]);

  const stats = useMemo(() => {
    const total = rows.length;
    const avg = total ? rows.reduce((s, r) => s + r.ev, 0) / total : 0;
    const high = total ? Math.max(...rows.map((r) => r.ev)) : 0;
    const eff = 100 - Math.min(100, avg * 4);
    return { total, avg, high, eff };
  }, [rows]);

  if (authLoading || !token) return <LoadingSkeleton rows={5} />;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-black uppercase tracking-tight">EV+ <span className="text-cyan-400">Finder</span></h1>
        <p className="text-white/50 text-sm">Identify positive expected value opportunities before the market corrects</p>
      </div>
      {error ? <div className="border border-red-500/30 bg-red-500/10 p-3 rounded-xl text-sm">{error}</div> : null}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {[
          ["TOTAL EV+ PROPS", String(stats.total)],
          ["AVG EDGE", `${stats.avg.toFixed(2)}%`],
          ["HIGHEST EV", `${stats.high.toFixed(2)}%`],
          ["MARKET EFFICIENCY", `${stats.eff.toFixed(1)}%`],
        ].map(([k, v]) => (
          <div key={k} className="bg-[#111] border border-[#222] rounded-xl p-4"><div className="text-[10px] uppercase font-black text-white/50">{k}</div><div className="text-xl font-black">{v}</div></div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        {PILL_SPORTS.map((k) => (
          <button key={k} onClick={() => setSport(k)} className={`px-3 py-1 rounded-full border text-xs font-black uppercase ${sport === k ? "bg-cyan-500 text-black border-cyan-500" : "bg-[#111] border-[#222] text-white/70"}`}>{SPORTS_CONFIG[k].label}</button>
        ))}
      </div>

      <div className="bg-[#111] border border-[#222] rounded-xl p-4">
        <div className="text-xs uppercase font-black text-white/60 mb-2">Min EV%: {minEv}</div>
        <input type="range" min={1} max={20} value={minEv} onChange={(e) => setMinEv(Number(e.target.value))} className="w-full accent-cyan-400" />
      </div>

      {loading ? (
        <LoadingSkeleton rows={5} />
      ) : (
        <div className="border border-[#222] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-[#111] text-white/50 text-[10px] uppercase">
              <tr>{["PLAYER","MARKET","LINE","FAIR ODDS","BOOK ODDS","EV %","CONFIDENCE","EXPIRES"].map((h)=><th key={h} className="px-3 py-2 text-left">{h}</th>)}</tr>
            </thead>
            <tbody>
              {rows.length === 0 ? <tr><td colSpan={8} className="text-center py-10 text-white/40">No data available</td></tr> : rows.map((r) => {
                const dots = Math.max(1, Math.min(5, Math.round(r.ev / 4)));
                return (
                  <tr key={r.id} className={`border-t border-[#222] ${r.ev > 10 ? "shadow-[inset_3px_0_0_0_rgba(34,211,238,0.7)]" : ""}`}>
                    <td className="px-3 py-2">{r.player}</td><td className="px-3 py-2">{r.market}</td><td className="px-3 py-2">{r.line}</td><td className="px-3 py-2">{r.fairOdds}</td><td className="px-3 py-2">{r.bookOdds}</td>
                    <td className="px-3 py-2 font-black text-cyan-300">{r.ev.toFixed(2)}%</td>
                    <td className="px-3 py-2">{[0,1,2,3,4].map((d)=><span key={d} className={`inline-block w-2 h-2 rounded-full mr-1 ${d < dots ? "bg-cyan-400" : "bg-white/20"}`} />)}</td>
                    <td className="px-3 py-2">{r.expires}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
