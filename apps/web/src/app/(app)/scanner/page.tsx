"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { SPORTS_CONFIG, DISPLAY_SPORTS, SportKey } from "@/lib/sports.config";
import { useAuth } from "@/hooks/useAuth";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import DataFreshnessBanner from "@/components/shared/DataFreshnessBanner";
import { useScannerFeed } from "@/hooks/useScannerFeed";

const PILL_LABELS = ["NBA", "NFL", "MLB", "NHL", "NCAAF", "NCAAB", "WNBA", "EPL", "UCL", "UFC", "MLS"];
const PILL_SPORTS = DISPLAY_SPORTS.filter((k) => PILL_LABELS.includes(SPORTS_CONFIG[k].label)).sort(
  (a: SportKey, b: SportKey) => PILL_LABELS.indexOf(SPORTS_CONFIG[a].label) - PILL_LABELS.indexOf(SPORTS_CONFIG[b].label)
);

export default function ScannerPage() {
  const router = useRouter();
  const { token, loading: authLoading } = useAuth();
  const [sport, setSport] = useState<SportKey>("basketball_nba");
  const { rows, isLoading: loading, isError, refetch, lastUpdated } = useScannerFeed(sport);
  const error = isError ? "Unable to connect to backend. Data will populate once API is online." : null;

  useEffect(() => {
    if (!authLoading && !token) router.replace("/login");
  }, [authLoading, token, router]);

  const stats = useMemo(() => {
    const edgesFound = rows.length;
    const avgEv = rows.length ? rows.reduce((s, r) => s + r.edgePct, 0) / rows.length : 0;
    const sharpAlerts = rows.filter((r) => r.signal === "SHARP").length;
    return { edgesFound, avgEv, sharpAlerts };
  }, [rows]);
  const allZeroEdges = rows.length > 0 && rows.every((r) => Math.abs(r.edgePct) < 0.01);

  if (authLoading || !token) return <div className="min-h-[50vh] flex items-center justify-center"><LoadingSkeleton rows={5} /></div>;

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white p-6 space-y-6">
      <div>
        <h1 className="text-4xl font-black uppercase tracking-tight">Market <span className="text-cyan-400">Scanner</span></h1>
        <p className="text-white/50 text-sm">Real-time edge detection across all markets</p>
        <div className="mt-3"><DataFreshnessBanner lastUpdated={lastUpdated} label="Scanner source" /></div>
      </div>

      {error ? <div className="border border-red-500/30 bg-red-500/10 p-3 rounded-xl text-sm">{error} <button onClick={() => refetch()} className="ml-2 underline">Retry</button></div> : null}
      {!error && allZeroEdges ? (
        <div className="border border-amber-500/30 bg-amber-500/10 p-3 rounded-xl text-sm text-amber-200">
          Odds loaded but edges are still flat. Compute cycle may still be warming.
        </div>
      ) : null}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {[
          ["EDGES FOUND", String(stats.edgesFound)],
          ["AVG EV", `${stats.avgEv.toFixed(2)}%`],
          ["SHARP ALERTS", String(stats.sharpAlerts)],
          ["LAST SCAN", new Date().toLocaleTimeString()],
        ].map(([k, v]) => (
          <div key={k} className="bg-[#111] border border-[#222] rounded-xl p-4">
            <div className="text-[10px] uppercase font-black text-white/50">{k}</div>
            <div className="text-xl font-black">{v}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        {PILL_SPORTS.map((k) => (
          <button key={k} onClick={() => setSport(k)} className={`px-3 py-1 rounded-full border text-xs font-black uppercase ${sport === k ? "bg-cyan-500 text-black border-cyan-500" : "bg-[#111] border-[#222] text-white/70"}`}>
            {SPORTS_CONFIG[k].label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingSkeleton rows={5} />
      ) : (
        <div className="border border-[#222] rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-[#111] text-white/50 text-[10px] uppercase">
              <tr>{["PLAYER","MARKET","LINE","BOOK ODDS","FAIR VALUE","EDGE %","SIGNAL","ACTION"].map((h)=><th key={h} className="px-3 py-2 text-left">{h}</th>)}</tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr><td colSpan={8} className="text-center py-10 text-white/40">No data available</td></tr>
              ) : rows.map((r) => (
                <tr key={r.id} className="border-t border-[#222]">
                  <td className="px-3 py-2">{r.player}</td><td className="px-3 py-2">{r.market}</td><td className="px-3 py-2">{r.line}</td>
                  <td className="px-3 py-2">{r.bookOdds}</td><td className="px-3 py-2">{r.fairValue}</td><td className="px-3 py-2">{r.edgePct.toFixed(2)}%</td>
                  <td className="px-3 py-2"><span className={`px-2 py-1 rounded text-[10px] font-black ${r.signal==="SHARP"?"bg-cyan-500/20 text-cyan-300":r.signal==="CLV"?"bg-green-500/20 text-green-300":r.signal==="EV+"?"bg-blue-500/20 text-blue-300":"bg-red-500/20 text-red-300"}`}>{r.signal}</span></td>
                  <td className="px-3 py-2"><button className="px-2 py-1 text-[10px] font-black border border-[#333] rounded">+ ADD TO SLIP</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
