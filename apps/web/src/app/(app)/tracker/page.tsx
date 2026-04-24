"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { API_BASE } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import { DISPLAY_SPORTS, SPORTS_CONFIG, SportKey } from "@/lib/sports.config";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";

type Bet = { id: string; created_at?: string; player_name?: string; market?: string; line?: number; odds?: number; stake?: number; status?: string; result?: string; pnl?: number };

export default function TrackerPage() {
  const router = useRouter();
  const { token, user, loading: authLoading } = useAuth();
  const [tab, setTab] = useState<"active" | "graded">("active");
  const [activeRows, setActiveRows] = useState<Bet[]>([]);
  const [gradedRows, setGradedRows] = useState<Bet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ sport: "basketball_nba", player: "", market: "", line: "", odds: "", stake: "" });

  useEffect(() => {
    if (!authLoading && !token) router.replace("/login");
  }, [authLoading, token, router]);

  async function load() {
    if (!user?.id) return;
    setLoading(true);
    setError(null);
    try {
      const [a, g] = await Promise.all([
        fetch(`${API_BASE}/api/bets?user_id=${user.id}&status=active`).then((r) => r.json()),
        fetch(`${API_BASE}/api/bets?user_id=${user.id}&status=graded`).then((r) => r.json()),
      ]);
      setActiveRows(Array.isArray(a?.data) ? a.data : Array.isArray(a) ? a : []);
      setGradedRows(Array.isArray(g?.data) ? g.data : Array.isArray(g) ? g : []);
    } catch {
      setActiveRows([]);
      setGradedRows([]);
      setError("Unable to connect to backend. Data will populate once API is online.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [user?.id]);

  const rows = tab === "active" ? activeRows : gradedRows;
  const stats = useMemo(() => {
    const graded = gradedRows.length;
    const won = gradedRows.filter((r) => String(r.status ?? r.result).toUpperCase() === "WON").length;
    const winRate = graded ? (won / graded) * 100 : 0;
    const roi = graded ? gradedRows.reduce((s, r) => s + Number(r.pnl ?? 0), 0) / graded : 0;
    return { winRate, roi, total: activeRows.length + gradedRows.length, active: activeRows.length };
  }, [activeRows, gradedRows]);

  async function logBet() {
    if (!user?.id) return;
    await fetch(`${API_BASE}/api/bets`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user.id,
        sport: form.sport,
        player_name: form.player,
        market: form.market,
        line: Number(form.line),
        odds: Number(form.odds),
        stake: Number(form.stake),
      }),
    });
    setOpen(false);
    await load();
  }

  async function gradeBet(id: string, status: "WON" | "LOST" | "PUSH") {
    await fetch(`${API_BASE}/api/bets/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    await load();
  }

  if (authLoading) return <LoadingSkeleton rows={5} />;
  if (!token) return null;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6 space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-4xl font-black uppercase tracking-tight">Bet <span className="text-cyan-400">Tracker</span></h1>
          <p className="text-white/50 text-sm">Track your picks, grade results, build your edge record</p>
        </div>
        <button onClick={() => setOpen(true)} className="px-3 py-2 rounded border border-[#333] bg-[#111] text-xs font-black">+ LOG BET</button>
      </div>
      {error ? <div className="border border-red-500/30 bg-red-500/10 p-3 rounded-xl text-sm">{error}</div> : null}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {[
          ["WIN RATE", `${stats.winRate.toFixed(1)}%`],
          ["ROI", `${stats.roi.toFixed(2)}%`],
          ["TOTAL BETS", String(stats.total)],
          ["ACTIVE PICKS", String(stats.active)],
        ].map(([k, v]) => <div key={k} className="bg-[#111] border border-[#222] rounded-xl p-4"><div className="text-[10px] uppercase font-black text-white/50">{k}</div><div className="text-xl font-black">{v}</div></div>)}
      </div>

      <div className="flex gap-2">
        <button onClick={() => setTab("active")} className={`px-3 py-1 rounded border text-xs font-black uppercase ${tab === "active" ? "bg-cyan-500 text-black border-cyan-500" : "bg-[#111] border-[#222]"}`}>Active</button>
        <button onClick={() => setTab("graded")} className={`px-3 py-1 rounded border text-xs font-black uppercase ${tab === "graded" ? "bg-cyan-500 text-black border-cyan-500" : "bg-[#111] border-[#222]"}`}>Graded</button>
      </div>

      {loading ? <LoadingSkeleton rows={5} /> : (
        <div className="border border-[#222] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-[#111] text-white/50 text-[10px] uppercase">
              <tr>{(tab === "active" ? ["DATE","PLAYER","MARKET","LINE","ODDS","STAKE","STATUS","ACTION"] : ["DATE","PLAYER","MARKET","LINE","ODDS","STAKE","STATUS","RESULT","P/L"]).map((h)=><th key={h} className="px-3 py-2 text-left">{h}</th>)}</tr>
            </thead>
            <tbody>
              {rows.length === 0 ? <tr><td colSpan={9} className="text-center py-10 text-white/40">No data available</td></tr> : rows.map((r) => {
                const s = String(r.status ?? "PENDING").toUpperCase();
                const color = s === "WON" ? "bg-green-500/20 text-green-300" : s === "LOST" ? "bg-red-500/20 text-red-300" : s === "PUSH" ? "bg-gray-500/20 text-gray-300" : "bg-yellow-500/20 text-yellow-300";
                return (
                  <tr key={r.id} className="border-t border-[#222]">
                    <td className="px-3 py-2">{r.created_at ? new Date(r.created_at).toLocaleDateString() : "—"}</td>
                    <td className="px-3 py-2">{r.player_name ?? "—"}</td><td className="px-3 py-2">{r.market ?? "—"}</td><td className="px-3 py-2">{r.line ?? "—"}</td><td className="px-3 py-2">{r.odds ?? "—"}</td><td className="px-3 py-2">{r.stake ?? "—"}</td>
                    <td className="px-3 py-2"><span className={`px-2 py-1 rounded text-[10px] font-black ${color}`}>{s}</span></td>
                    {tab === "active" ? <td className="px-3 py-2">{s === "PENDING" ? <div className="flex gap-1"><button onClick={() => gradeBet(r.id, "WON")} className="text-[10px] px-2 py-1 border border-[#333] rounded">GRADE</button></div> : "—"}</td> : <><td className="px-3 py-2">{r.result ?? s}</td><td className="px-3 py-2">{Number(r.pnl ?? 0).toFixed(2)}</td></>}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {open ? (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="w-full max-w-md bg-[#111] border border-[#222] rounded-xl p-4 space-y-3">
            <div className="text-lg font-black">Log Bet</div>
            <select value={form.sport} onChange={(e) => setForm({ ...form, sport: e.target.value as SportKey })} className="w-full bg-[#0a0a0a] border border-[#222] rounded p-2">{DISPLAY_SPORTS.map((k) => <option key={k} value={k}>{SPORTS_CONFIG[k].label}</option>)}</select>
            <input className="w-full bg-[#0a0a0a] border border-[#222] rounded p-2" placeholder="Player" value={form.player} onChange={(e) => setForm({ ...form, player: e.target.value })} />
            <input className="w-full bg-[#0a0a0a] border border-[#222] rounded p-2" placeholder="Market" value={form.market} onChange={(e) => setForm({ ...form, market: e.target.value })} />
            <input className="w-full bg-[#0a0a0a] border border-[#222] rounded p-2" placeholder="Line" value={form.line} onChange={(e) => setForm({ ...form, line: e.target.value })} />
            <input className="w-full bg-[#0a0a0a] border border-[#222] rounded p-2" placeholder="Odds (American)" value={form.odds} onChange={(e) => setForm({ ...form, odds: e.target.value })} />
            <input className="w-full bg-[#0a0a0a] border border-[#222] rounded p-2" placeholder="Stake" value={form.stake} onChange={(e) => setForm({ ...form, stake: e.target.value })} />
            <div className="flex justify-end gap-2"><button onClick={() => setOpen(false)} className="px-3 py-1 border border-[#333] rounded text-xs">Cancel</button><button onClick={logBet} className="px-3 py-1 bg-cyan-500 text-black rounded text-xs font-black">Save</button></div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
