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

type ArbRow = { id: string; event: string; market: string; book1: string; odds1: number; book2: string; odds2: number; arbPct: number; stakeA: number; stakeB: number; profit: number };

const implied = (odds: number) => (odds > 0 ? 100 / (odds + 100) : Math.abs(odds) / (Math.abs(odds) + 100));

export default function ArbPage() {
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const [sport, setSport] = useState<SportKey>("basketball_nba");
  const [rows, setRows] = useState<ArbRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    if (!authLoading && !token) router.replace("/login");
  }, [authLoading, token, router]);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE}/api/props/live?sport=${sport}&limit=200`);
        const json = await res.json();
        const data = Array.isArray(json?.data) ? json.data : Array.isArray(json) ? json : [];
        const grouped: Record<string, any[]> = {};
        data.forEach((r: any) => {
          const key = `${r?.game_id ?? "g"}__${r?.market_label ?? r?.market_key ?? "m"}`;
          grouped[key] = grouped[key] || [];
          grouped[key].push(r);
        });
        const arbs: ArbRow[] = [];
        Object.entries(grouped).forEach(([key, list], idx) => {
          if (list.length < 2) return;
          for (let i = 0; i < list.length; i += 1) for (let j = i + 1; j < list.length; j += 1) {
            const a = Number(list[i]?.book_odds ?? list[i]?.odds ?? NaN);
            const b = Number(list[j]?.book_odds ?? list[j]?.odds ?? NaN);
            if (!Number.isFinite(a) || !Number.isFinite(b)) continue;
            const sum = implied(a) + implied(b);
            if (sum >= 1) continue;
            const arbPct = (1 - sum) * 100;
            const total = 100;
            const stakeA = total * (implied(a) / sum);
            const stakeB = total - stakeA;
            const decA = a > 0 ? 1 + a / 100 : 1 + 100 / Math.abs(a);
            const payout = stakeA * decA;
            arbs.push({
              id: `${key}-${idx}-${i}-${j}`,
              event: list[i]?.player_name ?? list[i]?.home_team ?? "Event",
              market: list[i]?.market_label ?? list[i]?.market_key ?? "Market",
              book1: list[i]?.book ?? list[i]?.bookmaker ?? "Book 1",
              odds1: a,
              book2: list[j]?.book ?? list[j]?.bookmaker ?? "Book 2",
              odds2: b,
              arbPct,
              stakeA,
              stakeB,
              profit: payout - 100,
            });
          }
        });
        if (mounted) setRows(arbs.sort((x, y) => y.arbPct - x.arbPct));
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
    const live = rows.length;
    const avg = live ? rows.reduce((s, r) => s + r.arbPct, 0) / live : 0;
    const best = live ? Math.max(...rows.map((r) => r.arbPct)) : 0;
    const books = new Set(rows.flatMap((r) => [r.book1, r.book2])).size;
    return { live, avg, best, books };
  }, [rows]);

  async function syncBooks() {
    setSyncing(true);
    try {
      await fetch(`${API_BASE}/api/sync/trigger`, { method: "POST" });
    } finally {
      setSyncing(false);
    }
  }

  if (authLoading || !token) return <LoadingSkeleton rows={5} />;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-black uppercase tracking-tight">Arb <span className="text-cyan-400">Scanner</span></h1>
        <p className="text-white/50 text-sm">Guaranteed profit opportunities across books</p>
      </div>
      {error ? <div className="border border-red-500/30 bg-red-500/10 p-3 rounded-xl text-sm">{error}</div> : null}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {[
          ["LIVE ARB OPS", String(stats.live)],
          ["AVG PROFIT %", `${stats.avg.toFixed(2)}%`],
          ["BEST OPP", `${stats.best.toFixed(2)}%`],
          ["BOOKS MONITORED", String(stats.books)],
        ].map(([k, v]) => <div key={k} className="bg-[#111] border border-[#222] rounded-xl p-4"><div className="text-[10px] uppercase font-black text-white/50">{k}</div><div className="text-xl font-black">{v}</div></div>)}
      </div>
      <div className="flex flex-wrap gap-2">
        {PILL_SPORTS.map((k) => <button key={k} onClick={() => setSport(k)} className={`px-3 py-1 rounded-full border text-xs font-black uppercase ${sport === k ? "bg-cyan-500 text-black border-cyan-500" : "bg-[#111] border-[#222] text-white/70"}`}>{SPORTS_CONFIG[k].label}</button>)}
      </div>

      {loading ? <LoadingSkeleton rows={5} /> : (
        <div className="border border-[#222] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-[#111] text-white/50 text-[10px] uppercase"><tr>{["EVENT","MARKET","BOOK 1","ODDS 1","BOOK 2","ODDS 2","ARB %","STAKE ($100)","PROFIT"].map((h)=><th key={h} className="px-3 py-2 text-left">{h}</th>)}</tr></thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-10 text-white/40">
                    No arbitrage opportunities detected. Market is efficient right now — check back shortly.
                    <div className="mt-3"><button onClick={syncBooks} className="px-3 py-1 border border-[#333] rounded text-xs font-black">{syncing ? "SYNCING..." : "SYNC BOOKS"}</button></div>
                  </td>
                </tr>
              ) : rows.map((r) => (
                <tr key={r.id} className="border-t border-[#222]">
                  <td className="px-3 py-2">{r.event}</td><td className="px-3 py-2">{r.market}</td><td className="px-3 py-2">{r.book1}</td><td className="px-3 py-2">{r.odds1}</td>
                  <td className="px-3 py-2">{r.book2}</td><td className="px-3 py-2">{r.odds2}</td>
                  <td className="px-3 py-2"><span className="px-2 py-1 rounded bg-green-500/20 text-green-300 font-black text-[10px]">{r.arbPct.toFixed(2)}%</span></td>
                  <td className="px-3 py-2">${r.stakeA.toFixed(2)} / ${r.stakeB.toFixed(2)}</td><td className="px-3 py-2 text-green-300 font-black">${r.profit.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
