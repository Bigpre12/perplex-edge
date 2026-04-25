LUCRIX PLATFORM — COMPLETE END-TO-END FIX
Commit message: "fix: complete platform data wiring, odds key, all pages, engines, ws reconnect"

You are fixing every broken piece of this platform in one pass. Execute every section completely. Do not skip anything. Do not stop early.

════════════════════════════════════════════════════════════════
BACKEND FIXES
════════════════════════════════════════════════════════════════

── FIX 1: apps/api/src/core/config.py ──────────────────────────
Find the Odds API key loading block and replace entirely with:

raw_list = os.getenv("ODDS_API_KEYS", "")
primary = os.getenv("ODDS_API_KEY", os.getenv("THE_ODDS_API_KEY", ""))
backup = os.getenv("ODDS_API_KEY_BACKUP", "")
if not primary and raw_list and "," not in raw_list.strip():
    primary = raw_list.strip()
    raw_list = ""
all_keys: list[str] = []
if primary.strip():
    all_keys.append(primary.strip())
for k in raw_list.split(","):
    k = k.strip()
    if k and k not in all_keys:
        all_keys.append(k)
if backup.strip() and backup.strip() not in all_keys:
    all_keys.append(backup.strip())
self.ODDS_API_KEYS: list[str] = all_keys
self.ODDS_API_KEY: str = all_keys[0] if all_keys else ""
self.ODDS_API_KEY_PRIMARY: str = self.ODDS_API_KEY
self.ODDS_API_KEY_BACKUP: str = backup.strip()
if not self.ODDS_API_KEY:
    import logging
    logging.getLogger(__name__).warning("ODDS_API_KEY not resolved — check ODDS_API_KEY, THE_ODDS_API_KEY, or ODDS_API_KEYS env vars")

── FIX 2: User Settings Router ─────────────────────────────────
Find the router handling GET /settings (user_settings router). Replace the handler with:

DEFAULT_USER_SETTINGS = {
    "theme": "dark", "default_sport": "basketball_nba",
    "min_ev_threshold": 2.0, "notifications_enabled": True,
    "auto_sync": True, "tier": "free"
}

@router.get("/settings")
async def get_user_settings(user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    try:
        row = await db.fetchrow("SELECT settings FROM user_settings WHERE user_id = $1", user_id)
        if not row:
            return JSONResponse(content={"ok": True, "settings": DEFAULT_USER_SETTINGS, "is_default": True})
        return JSONResponse(content={"ok": True, "settings": {**DEFAULT_USER_SETTINGS, **row["settings"]}})
    except Exception as e:
        logger.error(f"Settings fetch failed: {e}")
        return JSONResponse(status_code=200, content={"ok": True, "settings": DEFAULT_USER_SETTINGS, "is_default": True})

@router.put("/settings")
async def put_user_settings(body: dict, user_id: str = Depends(get_current_user_id), db=Depends(get_db)):
    try:
        await db.execute(
            "INSERT INTO user_settings (user_id, settings) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET settings = $2, updated_at = now()",
            user_id, json.dumps(body)
        )
        return {"ok": True}
    except Exception as e:
        return JSONResponse(status_code=200, content={"ok": False, "error": str(e)})

Also add this Supabase migration (run in SQL editor):
CREATE TABLE IF NOT EXISTS user_settings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text UNIQUE NOT NULL,
  settings jsonb NOT NULL DEFAULT '{}',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_read" ON user_settings FOR SELECT USING (user_id = auth.uid()::text);
CREATE POLICY "own_write" ON user_settings FOR ALL USING (user_id = auth.uid()::text);

── FIX 3: Brain Endpoints ───────────────────────────────────────
Ensure these 3 endpoints exist in the brain router. Add any that are missing:

GET /api/brain/status → JSONResponse({ "status": brain_service.status or "warming", "last_sync": brain_service.last_sync_iso, "decisions_count": brain_service.decisions_count, "model_version": "groq-llama3" })

GET /api/brain/decisions?sport=&limit=25 → query decisions table, return list of { player_name, market_key, line, confidence, recommendation, reasoning, edge_score, created_at }. If table empty return [].

GET /api/brain/metrics → return { accuracy_7d, accuracy_30d, roi_7d, avg_confidence, total_decisions } computed from decisions table. If no data return all zeros with no error.

In main.py lifespan after DB init, add brain warmup task:
async def _warm_brain():
    await asyncio.sleep(45)
    try:
        from services.brain_service import brain_service
        await brain_service.run_inference_cycle(sport="basketball_nba")
    except Exception as e:
        logger.warning(f"Brain warmup: {e}")
asyncio.create_task(_warm_brain())

── FIX 4: Monte Carlo Endpoint ─────────────────────────────────
Ensure POST /api/simulation/run exists. If it doesn't, create it:

@router.post("/run")
async def run_simulation(body: SimRequest):
    import random, math
    def american_to_prob(o):
        return 100/(o+100) if o > 0 else abs(o)/(abs(o)+100)
    legs = body.legs
    n = body.n_sims or 10000
    probs = [l.get("probability") or american_to_prob(l.get("over_odds", -110)) for l in legs]
    # No-vig adjust
    wins = 0
    dist = []
    for _ in range(n):
        payout = 1.0
        all_hit = True
        for p in probs:
            hit = random.random() < p
            if not hit:
                all_hit = False
                break
            payout *= (1 / p - 1)
        if all_hit:
            wins += 1
            dist.append(payout)
        else:
            dist.append(0.0)
    win_prob = wins / n
    avg_payout = sum(dist) / n
    ev = win_prob * avg_payout - (1 - win_prob)
    kelly = max(0, (win_prob * avg_payout - (1 - win_prob)) / max(avg_payout, 0.01))
    return { "win_prob": win_prob, "ev": ev, "kelly_fraction": min(kelly, 0.25), "distribution": dist[:500], "legs_count": len(legs) }

── FIX 5: CLV Summary Endpoint ─────────────────────────────────
Ensure GET /api/clv/summary?sport= never throws. Wrap in try/except:
If no odds_snapshots data exists, return:
{ "avg_clv_edge": 0.0, "win_rate_vs_clv": 0.0, "total_events": 0, "events": [], "status": "pending_first_sync" }
with HTTP 200.

── FIX 6: WebSocket Keepalive ───────────────────────────────────
In the live WebSocket endpoint, add ping every 25 seconds:
async def live_ws_handler(websocket):
    await websocket.accept()
    try:
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=25.0)
                await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping", "ts": time.time()})
    except Exception:
        pass

── FIX 7: Props Response ────────────────────────────────────────
In the props router response, ensure every item includes:
"has_odds": bool(item.get("over_odds") or item.get("bookmaker_line")),
"probability": american_to_prob(item.get("over_odds", -110))

where american_to_prob(o) = 100/(o+100) if o>0 else abs(o)/(abs(o)+100)

── FIX 8: Hit Rate Endpoints ────────────────────────────────────
Ensure these exist in the hit_rate router:

GET /api/hit-rate/summary?sport= → { platform_accuracy, avg_roi, graded_picks, accuracy_trend }
GET /api/hit-rate/leaderboard?sport=&limit=25 → [{ player_name, hit_rate, roi, total_picks, streak, last_result }]

Both accept sport="all" for aggregate. Both return safe defaults (zeros, empty array) on DB error.

Also add:
POST /api/hit-rate/sync → trigger result grading job, return { ok: true, graded: N }

════════════════════════════════════════════════════════════════
FRONTEND SHARED INFRASTRUCTURE
════════════════════════════════════════════════════════════════

── CREATE: apps/web/src/lib/apiBase.ts ──────────────────────────
export const API_BASE = typeof window === "undefined"
  ? (process.env.NEXT_PUBLIC_API_URL || "https://perplex-edge-backend-copy-production.up.railway.app")
  : "/backend";

export const WS_BASE = (process.env.NEXT_PUBLIC_WS_URL || API_BASE)
  .replace("https://", "wss://").replace("http://", "ws://").replace(/\/+$/, "");

── CREATE: apps/web/src/hooks/useBackendData.ts ─────────────────
"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import { API_BASE } from "@/lib/apiBase";

export interface BackendDataState<T> {
  data: T | null; isLoading: boolean; isError: boolean;
  error: string | null; refetch: () => void; lastUpdated: Date | null;
}

export function useBackendData<T>(
  endpoint: string,
  opts?: { interval?: number; enabled?: boolean; params?: Record<string, string | number | undefined>; method?: "GET"|"POST"; body?: unknown; }
): BackendDataState<T> {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const abort = useRef<AbortController | null>(null);

  const fetchData = useCallback(async () => {
    if (opts?.enabled === false) { setIsLoading(false); return; }
    abort.current?.abort();
    abort.current = new AbortController();
    try {
      setIsError(false);
      const params = new URLSearchParams();
      if (opts?.params) Object.entries(opts.params).forEach(([k,v]) => { if (v !== undefined) params.set(k, String(v)); });
      const qs = params.toString();
      const url = `${API_BASE}${endpoint}${qs ? "?"+qs : ""}`;
      const res = await fetch(url, {
        method: opts?.method || "GET",
        headers: { "Content-Type": "application/json" },
        body: opts?.body ? JSON.stringify(opts.body) : undefined,
        signal: abort.current.signal,
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json); setLastUpdated(new Date()); setIsError(false); setError(null);
    } catch (e: unknown) {
      if ((e as Error).name === "AbortError") return;
      setIsError(true); setError((e as Error).message);
    } finally { setIsLoading(false); }
  }, [endpoint, JSON.stringify(opts?.params), opts?.enabled, opts?.method]);

  useEffect(() => {
    fetchData();
    if (opts?.interval) { const id = setInterval(fetchData, opts.interval); return () => clearInterval(id); }
  }, [fetchData]);

  return { data, isLoading, isError, error, refetch: fetchData, lastUpdated };
}

── CREATE: apps/web/src/components/shared/DataFreshnessBanner.tsx
"use client";
export function DataFreshnessBanner({ lastUpdated, staleMs = 300000, label = "DATA" }: { lastUpdated: Date | null; staleMs?: number; label?: string }) {
  if (!lastUpdated) return null;
  const age = Date.now() - lastUpdated.getTime();
  const str = age < 60000 ? `${Math.floor(age/1000)}s ago` : `${Math.floor(age/60000)}m ago`;
  const c = age < staleMs ? "text-green-400" : age < staleMs*2 ? "text-amber-400" : "text-red-400";
  const d = age < staleMs ? "bg-green-400" : age < staleMs*2 ? "bg-amber-400" : "bg-red-400";
  return (
    <div className={`flex items-center gap-2 text-xs ${c} mb-3`}>
      <span className={`w-2 h-2 rounded-full ${d} animate-pulse`} />
      {label} · updated {str}
    </div>
  );
}

── CREATE: apps/web/src/components/shared/LoadingSkeleton.tsx ───
export function LoadingSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="h-12 bg-gray-800 rounded-lg animate-pulse" style={{ opacity: 1 - i * 0.15 }} />
      ))}
    </div>
  );
}

── CREATE: apps/web/src/components/shared/ErrorRetry.tsx ────────
export function ErrorRetry({ onRetry, message }: { onRetry: () => void; message: string }) {
  return (
    <div className="text-center py-10">
      <p className="text-red-400 text-sm mb-3">{message}</p>
      <button onClick={onRetry} className="px-4 py-2 bg-gray-800 text-white rounded text-sm hover:bg-gray-700">↻ Retry</button>
    </div>
  );
}

════════════════════════════════════════════════════════════════
REWRITE ALL HOOKS

── apps/web/src/hooks/useSettings.ts (COMPLETE) ─────────────────
"use client";
import { useState, useCallback } from "react";
import { useBackendData } from "./useBackendData";
import { API_BASE } from "@/lib/apiBase";
export interface UserSettings { theme:string; default_sport:string; min_ev_threshold:number; notifications_enabled:boolean; auto_sync:boolean; tier:string; is_default?:boolean; }
export function useSettings() {
  const [isSaving,setIsSaving]=useState(false);
  const {data,isLoading,isError,refetch,lastUpdated}=useBackendData<{settings:UserSettings}>("/api/settings");
  const saveSettings=useCallback(async(s:Partial<UserSettings>)=>{
    setIsSaving(true);
    try{ await fetch(`${API_BASE}/api/settings`,{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(s)}); await refetch(); }
    finally{ setIsSaving(false); }
  },[refetch]);
  return { settings:data?.settings??null, isDefault:data?.settings?.is_default??false, isLoading, isError, isSaving, refetch, lastUpdated, saveSettings };
}

════════════════════════════════════════════════════════════════
REWRITE ALL UI PAGES — COMPLETE
Replace each file entirely.
════════════════════════════════════════════════════════════════

── apps/web/src/app/(app)/ev/page.tsx ───────────────────────────
"use client";
import { useState } from "react";
import { useEV } from "@/hooks/useEV";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function EVPage() {
  const {sport}=useSport(); const [minEv,setMinEv]=useState(0);
  const {data,isLoading,isError,error,refetch,lastUpdated}=useEV(sport,minEv);
  const rows=(data??[]).filter(r=>r.ev_pct>=minEv).sort((a,b)=>b.ev_pct-a.ev_pct);
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <div><h1 className="text-2xl font-bold text-white">EV+ SIGNALS</h1><p className="text-xs text-gray-400">Positive Expectation Engine</p></div>
        <div className="flex items-center gap-4">
          abel className="text-xs text-gray-400">Min EV%
            <select value={minEv} onChange={e=>setMinEv(Number(e.target.value))} className="ml-2 bg-gray-800 text-white text-xs rounded px-2 py-1">
              {[0,1,2,3,5,7,10].map(v=><option key={v} value={v}>{v}%</option>)}
            </select>
          </label>
          <div className="text-xs text-gray-400"><span className="text-white font-bold text-lg">{rows.length}</span> EDGES</div>
        </div>
      </div>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={120000} label="EV DATA"/>
      {isLoading&&<LoadingSkeleton rows={8}/>}
      {isError&&<ErrorRetry onRetry={refetch} message={error??"Failed to load EV signals"}/>}
      {!isLoading&&!isError&&rows.length===0&&(
        <div className="text-center py-16 text-gray-500">
          <p className="text-lg">No EV signals at {minEv}%+ threshold</p>
          <p className="text-sm mt-2">Engine computing — lower threshold or retry in 30s</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded text-sm">Retry Now</button>
        </div>
      )}
      {rows.length>0&&(
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="text-gray-400 text-xs border-b border-gray-800">
              <th className="text-left py-3 px-4">PLAYER</th><th className="text-left py-3 px-4">MARKET</th>
              <th className="text-right py-3 px-4">LINE</th><th className="text-right py-3 px-4">EV%</th>
              <th className="text-left py-3 px-4">BOOK</th><th className="text-left py-3 px-4">SIGNAL</th><th className="text-left py-3 px-4">REC</th>
            </tr></thead>
            <tbody>
              {rows.map((r,i)=>{
                const c=r.ev_pct>=5?"text-green-400":r.ev_pct>=2?"text-amber-400":"text-gray-400";
                return(<tr key={i} className="border-b border-gray-900 hover:bg-gray-900">
                  <td className="py-3 px-4 text-white font-medium">{r.player_name}</td>
                  <td className="py-3 px-4 text-gray-300">{r.market_key}</td>
                  <td className="py-3 px-4 text-right text-gray-300">{r.line}</td>
                  <td className={`py-3 px-4 text-right font-bold ${c}`}>{r.ev_pct>0?"+":""}{r.ev_pct.toFixed(1)}%</td>
                  <td className="py-3 px-4 text-gray-400 text-xs">{r.bookmaker}</td>
                  <td className={`py-3 px-4 text-xs ${c}`}>{r.ev_pct>=5?"● HIGH":r.ev_pct>=2?"● MID":"● LOW"}</td>
                  <td className="py-3 px-4"><span className={`px-2 py-1 rounded text-xs font-bold ${r.recommendation==="OVER"?"bg-green-900 text-green-300":r.recommendation==="UNDER"?"bg-red-900 text-red-300":"bg-gray-800 text-gray-400"}`}>{r.recommendation}</span></td>
                </tr>);
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/clv/page.tsx ──────────────────────────
"use client";
import { useState } from "react";
import { useCLV } from "@/hooks/useCLV";
import { useSimLegs, useMonteCarlo } from "@/hooks/useMonteCarlo";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function CLVPage() {
  const {sport}=useSport(); const [tab,setTab]=useState<"clv"|"monte">("clv");
  const {data:clv,isLoading,isError,error,refetch,lastUpdated}=useCLV(sport);
  const {data:legs,isLoading:ll}=useSimLegs(sport);
  const {result,isRunning,error:simErr,runSimulation}=useMonteCarlo();
  const [sel,setSel]=useState<number[]>([]);
  const toggle=(i:number)=>setSel(p=>p.includes(i)?p.filter(x=>x!==i):p.length<8?[...p,i]:p);
  return(
    <div className="p-6">
      <div className="mb-6"><h1 className="text-2xl font-bold text-white">NEURAL ANALYTICS</h1><p className="text-xs text-gray-400 uppercase tracking-widest mt-1">CLV & Monte Carlo Simulation</p></div>
      <div className="flex gap-2 mb-6">
        {(["clv","monte"] as const).map(t=>(
          <button key={t} onClick={()=>setTab(t)} className={`px-5 py-2 rounded text-sm font-medium transition-colors ${tab===t?"bg-white text-black":"bg-gray-800 text-gray-300 hover:bg-gray-700"}`}>
            {t==="clv"?"ACTIVE CLV":"MONTE CARLO"}
          </button>
        ))}
      </div>
      {tab==="clv"&&(<>
        <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={300000} label="CLV DATA"/>
        {isLoading&&<LoadingSkeleton rows={4}/>}
        {isError&&<ErrorRetry onRetry={refetch} message={error??""}/>}
        {!isLoading&&clv&&(<>
          <div className="grid grid-cols-3 gap-4 mb-6">
            {[{label:"AVG CLV EDGE",value:`+${clv.avg_clv_edge.toFixed(2)}%`},{label:"WIN RATE VS CLV",value:`${clv.win_rate_vs_clv.toFixed(1)}%`},{label:"TOTAL EVENTS",value:String(clv.total_events)}].map(s=>(
              <div key={s.label} className="bg-gray-900 rounded-lg p-5"><div className="text-xs text-gray-400 mb-2">{s.label}</div><div className="text-3xl font-light text-white">{s.value}</div></div>
            ))}
          </div>
          {clv.total_events===0?(
            <div className="text-center py-10 text-gray-500"><p>CLV tracking begins after the first odds sync</p><p className="text-xs mt-1">Open and close lines are recorded automatically each game</p></div>
          ):(
            <table className="w-full text-sm">
              <thead><tr className="text-gray-400 text-xs border-b border-gray-800">
                <th className="text-left py-3 px-4">PLAYER</th><th className="text-left py-3 px-4">MARKET</th>
                <th className="text-right py-3 px-4">OPEN</th><th className="text-right py-3 px-4">CLOSE</th>
                <th className="text-right py-3 px-4">CLV EDGE</th><th className="text-left py-3 px-4">RESULT</th>
              </tr></thead>
              <tbody>{clv.events.map((ev,i)=>(
                <tr key={i} className="border-b border-gray-900 hover:bg-gray-900">
                  <td className="py-3 px-4 text-white">{ev.player_name}</td>
                  <td className="py-3 px-4 text-gray-300">{ev.market_key}</td>
                  <td className="py-3 px-4 text-right text-gray-400">{ev.open_line}</td>
                  <td className="py-3 px-4 text-right text-gray-400">{ev.close_line}</td>
                  <td className={`py-3 px-4 text-right font-bold ${ev.clv_edge>=0?"text-green-400":"text-red-400"}`}>{ev.clv_edge>=0?"+":""}{ev.clv_edge.toFixed(2)}%</td>
                  <td className="py-3 px-4"><span className={`px-2 py-1 rounded text-xs font-bold ${ev.result==="WIN"?"bg-green-900 text-green-300":ev.result==="LOSS"?"bg-red-900 text-red-300":ev.result==="PUSH"?"bg-gray-700 text-gray-300":"bg-blue-900 text-blue-300"}`}>{ev.result}</span></td>
                </tr>
              ))}</tbody>
            </table>
          )}
        </>)}
      </>)}
      {tab==="monte"&&(
        <div className="grid grid-cols-2 gap-6">
          <div className="bg-gray-900 rounded-xl p-5">
            <h2 className="text-sm font-bold text-white mb-1">SELECT LEGS</h2>
            <p className="text-xs text-gray-500 mb-4">Choose up to 8 props</p>
            {ll?<LoadingSkeleton rows={6}/>:(legs??[]).length===0?<p className="text-gray-500 text-sm">No props available — odds sync in progress</p>:(
              <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                {(legs??[]).map((leg,i)=>(
                  abel key={i} className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${sel.includes(i)?"bg-blue-900/40 border border-blue-700":"bg-gray-800 hover:bg-gray-700"}`}>
                    <input type="checkbox" checked={sel.includes(i)} onChange={()=>toggle(i)} className="accent-blue-500"/>
                    <div className="flex-1 min-w-0"><div className="text-white text-sm truncate">{leg.player_name}</div><div className="text-gray-400 text-xs">{leg.market_key} · O{leg.line}</div></div>
                    <div className="text-xs text-gray-400 shrink-0">{leg.over_odds>0?"+":""}{leg.over_odds}</div>
                  </label>
                ))}
              </div>
            )}
            <div className="mt-4 text-xs text-gray-500">{sel.length}/8 legs selected</div>
          </div>
          <div className="bg-gray-900 rounded-xl p-5 flex flex-col">
            <h2 className="text-sm font-bold text-white mb-1">NEURAL PARLAY SIMULATOR</h2>
            <p className="text-xs text-gray-500 mb-5">10,000+ iteration Monte Carlo engine</p>
            <button onClick={()=>{ if(!legs||sel.length===0)return; runSimulation(sel.map(i=>legs[i])); }}
              disabled={isRunning||sel.length===0}
              className="w-full py-3 rounded-lg font-bold text-sm bg-purple-600 hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white mb-6 transition-all">
              {isRunning?"⟳ RUNNING SIMULATION...":"✦ RUN NEURAL SIMULATION"}
            </button>
            {simErr&&
            {simErr&&<p className="text-red-400 text-xs mb-4">{simErr}</p>}
            {result&&(
              <div className="space-y-4 flex-1">
                <div className="grid grid-cols-3 gap-3">
                  {[{label:"WIN PROB",value:`${(result.win_prob*100).toFixed(1)}%`,color:result.win_prob>0.5?"text-green-400":"text-amber-400"},
                    {label:"EXP VALUE",value:`${result.ev>=0?"+":""}${(result.ev*100).toFixed(1)}%`,color:result.ev>=0?"text-green-400":"text-red-400"},
                    {label:"KELLY %",value:`${(result.kelly_fraction*100).toFixed(1)}%`,color:"text-blue-400"}
                  ].map(s=>(
                    <div key={s.label} className="bg-gray-800 rounded-lg p-3 text-center">
                      <div className="text-xs text-gray-400 mb-1">{s.label}</div>
                      <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
                    </div>
                  ))}
                </div>
                {result.distribution.length>0&&(
                  <div>
                    <div className="text-xs text-gray-400 mb-2">OUTCOME DISTRIBUTION</div>
                    <div className="flex items-end gap-0.5 h-16">
                      {(()=>{
                        const N=20,vals=result.distribution;
                        const mx=Math.max(...vals),mn=Math.min(...vals),rng=mx-mn||1;
                        const counts=Array(N).fill(0);
                        vals.forEach(v=>{const idx=Math.min(Math.floor(((v-mn)/rng)*N),N-1);counts[idx]++;});
                        const pk=Math.max(...counts);
                        return counts.map((c,i)=>(
                          <div key={i} style={{height:`${(c/pk)*100}%`}} className={`flex-1 rounded-sm ${i>N*0.6?"bg-green-600":i>N*0.4?"bg-amber-600":"bg-red-700"}`}/>
                        ));
                      })()}
                    </div>
                  </div>
                )}
                <p className="text-xs text-gray-500">{result.legs_count} legs · Kelly stake: {(result.kelly_fraction*100).toFixed(1)}% of bankroll</p>
              </div>
            )}
            {!result&&!isRunning&&<div className="flex-1 flex items-center justify-center text-gray-600 text-sm">Select legs and run simulation</div>}
          </div>
        </div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/brain/page.tsx ────────────────────────
"use client";
import { useBrainStatus, useBrainDecisions, useBrainMetrics } from "@/hooks/useBrainData";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
export default function BrainPage() {
  const {sport}=useSport();
  const {data:st,lastUpdated:su}=useBrainStatus();
  const {data:dec,isLoading:dl,refetch}=useBrainDecisions(sport);
  const {data:met}=useBrainMetrics();
  const sc=st?.status==="active"?"text-green-400":st?.status==="warming"?"text-amber-400":"text-red-400";
  const sd=st?.status==="active"?"bg-green-400":st?.status==="warming"?"bg-amber-400":"bg-red-400";
  return(
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-white">NEURAL ENGINE</h1><p className="text-xs text-gray-400 uppercase tracking-widest mt-1">AI-Powered Decision Layer</p></div>
        <div className={`flex items-center gap-2 text-sm font-bold ${sc}`}><span className={`w-2.5 h-2.5 rounded-full animate-pulse ${sd}`}/>{st?.status?.toUpperCase()??"CONNECTING"}</div>
      </div>
      <DataFreshnessBanner lastUpdated={su} staleMs={60000} label="BRAIN"/>
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[{label:"ACCURACY 7D",value:met?`${met.accuracy_7d.toFixed(1)}%`:"—"},{label:"ROI 7D",value:met?`${met.roi_7d>=0?"+":""}${met.roi_7d.toFixed(1)}%`:"—"},{label:"AVG CONFIDENCE",value:met?`${met.avg_confidence.toFixed(0)}%`:"—"},{label:"DECISIONS",value:st?String(st.decisions_count):"—"}].map(m=>(
          <div key={m.label} className="bg-gray-900 rounded-xl p-4"><div className="text-xs text-gray-400 mb-2">{m.label}</div><div className="text-2xl font-bold text-white">{m.value}</div></div>
        ))}
      </div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider">Decisions — {sport}</h2>
        <button onClick={refetch} className="text-xs text-gray-400 hover:text-white px-3 py-1 bg-gray-800 rounded">↻ Refresh</button>
      </div>
      {dl&&<LoadingSkeleton rows={6}/>}
      {!dl&&(dec??[]).length===0&&(
        <div className="text-center py-14 text-gray-500">
          <div className="text-4xl mb-4">◎</div>
          <p className="text-base">Engine active — decisions populate after first full ingest cycle</p>
          <p className="text-sm mt-2">Last sync: {st?.last_sync?new Date(st.last_sync).toLocaleTimeString():"—"}</p>
        </div>
      )}
      {(dec??[]).length>0&&(
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {dec!.map((d,i)=>(
            <div key={i} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <div className="flex items-start justify-between mb-3">
                <div><div className="text-white font-medium">{d.player_name}</div><div className="text-gray-400 text-xs mt-0.5">{d.market_key} · O/U {d.line}</div></div>
                <span className={`px-2 py-1 rounded text-xs font-bold ${d.recommendation==="OVER"?"bg-green-900 text-green-300":d.recommendation==="UNDER"?"bg-red-900 text-red-300":d.recommendation==="FADE"?"bg-orange-900 text-orange-300":"bg-gray-800 text-gray-400"}`}>{d.recommendation}</span>
              </div>
              <div className="mb-3">
                <div className="flex justify-between text-xs mb-1"><span className="text-gray-400">Confidence</span><span className="text-white font-medium">{d.confidence.toFixed(0)}%</span></div>
                <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden"><div style={{width:`${d.confidence}%`}} className={`h-full rounded-full ${d.confidence>=70?"bg-green-500":d.confidence>=50?"bg-amber-500":"bg-red-500"}`}/></div>
              </div>
              {d.reasoning&&<p className="text-xs text-gray-500 line-clamp-2">{d.reasoning}</p>}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-800">
                <span className="text-xs text-gray-500">Edge Score</span>
                <span className="text-xs text-blue-400 font-bold">{d.edge_score.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/sharp/page.tsx ────────────────────────
"use client";
import { useSharpMoney } from "@/hooks/useSharpMoney";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function SharpPage() {
  const {sport}=useSport();
  const {data,isLoading,isError,error,refetch,lastUpdated}=useSharpMoney(sport);
  return(
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-1">SHARP MONEY</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Institutional Flow Tracker</p>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={120000} label="SHARP DATA"/>
      {isLoading&&<LoadingSkeleton rows={8}/>}
      {isError&&<ErrorRetry onRetry={refetch} message={error??""}/>}
      {!isLoading&&!isError&&(data??[]).length===0&&(
        <div className="text-center py-14 text-gray-500">
          <p>No sharp signals detected yet</p><p className="text-xs mt-2">Requires live multi-book odds — computing now</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-gray-800 text-white rounded text-sm">Retry</button>
        </div>
      )}
      {(data??[]).length>0&&(
        <table className="w-full text-sm">
          <thead><tr className="text-gray-400 text-xs border-b border-gray-800">
            <th className="text-left py-3 px-4">PLAYER</th><th className="text-left py-3 px-4">MARKET</th>
            <th className="text-right py-3 px-4">LINE</th><th className="text-right py-3 px-4">SHARP%</th>
            <th className="text-right py-3 px-4">PUBLIC%</th><th className="text-right py-3 px-4">MOVE</th><th className="text-left py-3 px-4">SIGNAL</th>
          </tr></thead>
          <tbody>{(data??[]).sort((a,b)=>b.sharp_pct-a.sharp_pct).map((r,i)=>(
            <tr key={i} className="border-b border-gray-900 hover:bg-gray-900">
              <td className="py-3 px-4 text-white font-medium">{r.player_name}</td>
              <td className="py-3 px-4 text-gray-300">{r.market_key}</td>
              <td className="py-3 px-4 text-right text-gray-300">{r.line}</td>
              <td className="py-3 px-4 text-right text-blue-400 font-bold">{r.sharp_pct.toFixed(0)}%</td>
              <td className="py-3 px-4 text-right text-gray-400">{r.public_pct.toFixed(0)}%</td>
              <td className={`py-3 px-4 text-right font-bold ${r.line_move>0?"text-green-400":r.line_move<0?"text-red-400":"text-gray-400"}`}>{r.line_move>0?"▲":r.line_move<0?"▼":"–"} {Math.abs(r.line_move).toFixed(1)}</td>
              <td className="py-3 px-4"><span className={`px-2 py-1 rounded text-xs font-bold ${r.signal_strength==="HIGH"?"bg-blue-900 text-blue-300":r.signal_strength==="MEDIUM"?"bg-amber-900 text-amber-300":"bg-gray-800 text-gray-400"}`}>{r.signal_strength}</span></td>
            </tr>
          ))}</tbody>
        </table>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/arbitrage/page.tsx ────────────────────
"use client";
import { useArbitrage } from "@/hooks/useArbitrage";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function ArbPage() {
  const {sport}=useSport();
  const {data,isLoading,isError,error,refetch,lastUpdated}=useArbitrage(sport);
  return(
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-1">ARBITRAGE SCANNER</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Risk-Free Market Extraction</p>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={60000} label="ARB DATA"/>
      {isLoading&&<LoadingSkeleton rows={6}/>}
      {isError&&<ErrorRetry onRetry={refetch} message={error??""}/>}
      {!isLoading&&!isError&&(data??[]).length===0&&(
        <div className="text-center py-14 text-gray-500">
          <p>No arbitrage opportunities found</p><p className="text-xs mt-2">Requires simultaneous odds from 2+ books — compute triggered</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-gray-800 text-white rounded text-sm">Retry</button>
        </div>
      )}
      {(data??[]).length>0&&(
        <div className="grid gap-4">{(data??[]).sort((a,b)=>b.arb_pct-a.arb_pct).map((arb,i)=>(
          <div key={i} className="bg-gray-900 rounded-xl p-5 border border-green-900">
            <div
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="text-white font-semibold">{arb.player_name}</div>
                <div className="text-gray-400 text-xs mt-0.5">{arb.market_key} · Line {arb.line}</div>
              </div>
              <div className="text-right">
                <div className="text-green-400 font-bold text-xl">{arb.arb_pct.toFixed(2)}%</div>
                <div className="text-green-600 text-xs">${arb.profit_per_100.toFixed(2)} per $100</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {[{book:arb.book_a,odds:arb.odds_a,label:"BOOK A"},{book:arb.book_b,odds:arb.odds_b,label:"BOOK B"}].map((side,j)=>(
                <div key={j} className="bg-gray-800 rounded-lg p-3">
                  <div className="text-xs text-gray-400">{side.label} · {side.book}</div>
                  <div className="text-white font-bold mt-1">{side.odds>0?"+":""}{side.odds}</div>
                </div>
              ))}
            </div>
          </div>
        ))}</div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/whale/page.tsx ────────────────────────
"use client";
import { useWhale } from "@/hooks/useWhale";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function WhalePage() {
  const {sport}=useSport();
  const {data,isLoading,isError,error,refetch,lastUpdated}=useWhale(sport);
  return(
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-1">WHALE INTEL</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Institutional Smart Money Flow</p>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={120000} label="WHALE DATA"/>
      {isLoading&&<LoadingSkeleton rows={6}/>}
      {isError&&<ErrorRetry onRetry={refetch} message={error??""}/>}
      {!isLoading&&!isError&&(data??[]).length===0&&(
        <div className="text-center py-14 text-gray-500">
          <p>No whale signals in current window</p>
          <p className="text-xs mt-2">Whale detection activates after odds sync</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-gray-800 text-white rounded text-sm">Retry</button>
        </div>
      )}
      {(data??[]).length>0&&(
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(data??[]).sort((a,b)=>b.units-a.units).map((w,i)=>(
            <div key={i} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <div className="flex justify-between items-start mb-3">
                <div><div className="text-white font-medium">{w.player_name}</div><div className="text-gray-400 text-xs">{w.market_key} · O/U {w.line}</div></div>
                <span className={`text-xs font-bold px-2 py-1 rounded ${w.move_type==="STEAM"?"bg-red-900 text-red-300":w.move_type==="WHALE"?"bg-purple-900 text-purple-300":"bg-blue-900 text-blue-300"}`}>{w.move_type}</span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center">
                {[{label:"DIRECTION",value:w.direction,c:w.direction==="OVER"?"text-green-400":"text-red-400"},{label:"UNITS",value:`${w.units.toFixed(1)}u`,c:"text-white"},{label:"LINE",value:String(w.bookmaker_line||w.line),c:"text-white"}].map(s=>(
                  <div key={s.label} className="bg-gray-800 rounded p-2"><div className="text-xs text-gray-400">{s.label}</div><div className={`font-bold text-sm ${s.c}`}>{s.value}</div></div>
                ))}
              </div>
              <div className="mt-3 flex justify-between text-xs text-gray-500">
                <span>Sharp {w.sharp_pct.toFixed(0)}% / Public {w.public_pct.toFixed(0)}%</span>
                <span>{new Date(w.detected_at).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/kalshi/page.tsx ───────────────────────
"use client";
import { useKalshi } from "@/hooks/useKalshi";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function KalshiPage() {
  const {data,isLoading,isError,error,refetch,lastUpdated}=useKalshi();
  return(
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-1">KALSHI MARKETS</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Prediction Market Edge</p>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={120000} label="KALSHI"/>
      {isLoading&&<LoadingSkeleton rows={8}/>}
      {isError&&(
        <div className="space-y-3">
          <ErrorRetry onRetry={refetch} message={error??"Kalshi API unavailable"}/>
          <p className="text-center text-xs text-gray-500">Kalshi integration requires KALSHI_API_KEY in Railway env vars</p>
        </div>
      )}
      {!isLoading&&!isError&&(data??[]).length===0&&(
        <div className="text-center py-14 text-gray-500">
          <p>No Kalshi markets available</p>
          <p className="text-xs mt-2">Check KALSHI_API_KEY is set in Railway and backend is online</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-gray-800 text-white rounded text-sm">Retry</button>
        </div>
      )}
      {(data??[]).length>0&&(
        <div className="grid gap-3">
          {(data??[]).sort((a,b)=>b.volume-a.volume).map((m,i)=>(
            <div key={i} className="bg-gray-900 rounded-xl p-4 flex items-center justify-between">
              <div className="flex-1 min-w-0 mr-4">
                <div className="text-white font-medium truncate">{m.title}</div>
                <div className="text-gray-400 text-xs mt-0.5">{m.ticker} · {m.category} · closes {new Date(m.closes_at).toLocaleDateString()}</div>
              </div>
              <div className="grid grid-cols-3 gap-4 text-center shrink-0">
                <div><div className="text-xs text-gray-400">YES</div><div className="text-green-400 font-bold">{(m.yes_price*100).toFixed(0)}¢</div></div>
                <div><div className="text-xs text-gray-400">NO</div><div className="text-red-400 font-bold">{(m.no_price*100).toFixed(0)}¢</div></div>
                <div><div className="text-xs text-gray-400">VOL</div><div className="text-white font-bold">${(m.volume/1000).toFixed(0)}k</div></div>
              </div>
              {m.edge_vs_sportsbook!==undefined&&(
                <div className={`ml-4 text-sm font-bold ${m.edge_vs_sportsbook>0?"text-green-400":"text-gray-400"}`}>
                  {m.edge_vs_sportsbook>0?"+":""}{(m.edge_vs_sportsbook*100).toFixed(1)}% EDGE
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/live/page.tsx ─────────────────────────
"use client";
import { useLiveGames } from "@/hooks/useLiveGames";
import { useSport } from "@/hooks/useSport";
export default function LivePage() {
  const {sport}=useSport();
  const {games,wsStatus}=useLiveGames(sport);
  const live=games.filter(g=>g.status==="live");
  const scheduled=games.filter(g=>g.status==="scheduled");
  return(
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-white">LIVE GAMES</h1><p className="text-xs text-gray-400 uppercase tracking-widest mt-1">Real-Time Score Feed</p></div>
        <div className={`flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-full ${wsStatus==="online"?"bg-green-900/40 text-green-400":wsStatus==="connecting"?"bg-amber-900/40 text-amber-400":"bg-red-900/40 text-red-400"}`}>
          <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${wsStatus==="online"?"bg-green-400":wsStatus==="connecting"?"bg-amber-400":"bg-red-400"}`}/>
          {wsStatus==="online"?"LIVE STREAM":wsStatus==="connecting"?"CONNECTING...":"POLLING FALLBACK"}
        </div>
      </div>
      {games.length===0&&(
        <div className="text-center py-16 text-gray-500">
          <div className="text-4xl mb-4">📡</div>
          <p className="text-base">No {sport} games currently live</p>
          <p className="text-sm mt-2">Stream connects automatically when games start</p>
        </div>
      )}
      {live.length>0&&(
        <div className="mb-8">
          <h2 className="text-xs font-bold text-green-400 uppercase tracking-widest mb-3">● LIVE NOW</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {live.map((g,i)=>(
              <div key={i} className="bg-gray-900 rounded-xl p-5 border border-green-900">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-green-400 font-bold animate-pulse">● LIVE · {g.period} {g.clock}</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="text-center flex-1"><div className="text-white font-bold text-lg">{g.away_team}</div><div className="text-gray-400 text-xs mt-1">AWAY</div></div>
                  <div className="text-center px-6">
                    <div className="text-4xl font-bold text-white">{g.away_score}<span className="text-gray-600 mx-2">–</span>{g.home_score}</div>
                  </div>
                  <div className="text-center flex-1"><div className="text-white font-bold text-lg">{g.home_team}</div><div className="text-gray-400 text-xs mt-1">HOME</div></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      {scheduled.length>0&&(
        <div>
          <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">UPCOMING</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {scheduled.map((g,i)=>(
              <div key={i} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
                <div className="flex items-center justify-between">
                  <div className="text-white font-medium">{g.away_team} @ {g.home_team}</div>
                  <div className="text-gray-400 text-xs">{g.period}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/line-movement/page.tsx ────────────────
"use client";
import { useLineMovement } from "@/hooks/useLineMovement";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function LineMovementPage() {
  const {sport}=useSport();
  const {data,isLoading,isError,error,refetch,lastUpdated}=useLineMovement(sport);
  return(
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-1">LINE MOVEMENT</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Market Flux Detection</p>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={90000} label="LINE DATA"/>
      {isLoading&&<LoadingSkeleton rows={8}/>}
      {isError&&<ErrorRetry onRetry={refetch} message={error??""}/>}
      {!isLoading&&!isError&&(data??[]).length===0&&(
        <div className="text-center py-14 text-gray-500">
          <p>No active market flux detected
          <p>No active market flux detected</p>
          <p className="text-xs mt-2">Line movement requires at least 2 odds snapshots per market — syncing now</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-gray-800 text-white rounded text-sm">Retry</button>
        </div>
      )}
      {(data??[]).length>0&&(
        <table className="w-full text-sm">
          <thead><tr className="text-gray-400 text-xs border-b border-gray-800">
            <th className="text-left py-3 px-4">PLAYER</th><th className="text-left py-3 px-4">MARKET</th>
            <th className="text-right py-3 px-4">OPEN</th><th className="text-right py-3 px-4">CURRENT</th>
            <th className="text-right py-3 px-4">DELTA</th><th className="text-right py-3 px-4">MOVE%</th>
            <th className="text-left py-3 px-4">DIRECTION</th><th className="text-left py-3 px-4">BOOK</th>
          </tr></thead>
          <tbody>{(data??[]).sort((a,b)=>Math.abs(b.move_pct)-Math.abs(a.move_pct)).map((r,i)=>(
            <tr key={i} className="border-b border-gray-900 hover:bg-gray-900">
              <td className="py-3 px-4 text-white font-medium">{r.player_name}</td>
              <td className="py-3 px-4 text-gray-300">{r.market_key}</td>
              <td className="py-3 px-4 text-right text-gray-400">{r.open_line}</td>
              <td className="py-3 px-4 text-right text-white font-medium">{r.current_line}</td>
              <td className={`py-3 px-4 text-right font-bold ${r.line_delta>0?"text-green-400":r.line_delta<0?"text-red-400":"text-gray-400"}`}>{r.line_delta>0?"+":""}{r.line_delta.toFixed(1)}</td>
              <td className={`py-3 px-4 text-right font-bold ${r.move_pct>0?"text-green-400":r.move_pct<0?"text-red-400":"text-gray-400"}`}>{r.move_pct>0?"+":""}{r.move_pct.toFixed(1)}%</td>
              <td className="py-3 px-4"><span className={`px-2 py-1 rounded text-xs font-bold ${r.move_direction==="UP"?"bg-green-900 text-green-300":r.move_direction==="DOWN"?"bg-red-900 text-red-300":"bg-gray-800 text-gray-400"}`}>{r.move_direction==="UP"?"▲ UP":r.move_direction==="DOWN"?"▼ DOWN":"— FLAT"}</span></td>
              <td className="py-3 px-4 text-gray-400 text-xs">{r.bookmaker}</td>
            </tr>
          ))}</tbody>
        </table>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/signals/page.tsx ──────────────────────
"use client";
import { useSignals } from "@/hooks/useSignals";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function SignalsPage() {
  const {sport}=useSport();
  const {data,isLoading,isError,error,refetch,lastUpdated}=useSignals(sport);
  return(
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-1">MARKET SIGNALS</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Anomaly Detection Engine</p>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={90000} label="SIGNALS"/>
      {isLoading&&<LoadingSkeleton rows={6}/>}
      {isError&&<ErrorRetry onRetry={refetch} message={error??""}/>}
      {!isLoading&&!isError&&(data??[]).length===0&&(
        <div className="text-center py-14 text-gray-500">
          <p>No market anomalies detected</p>
          <p className="text-xs mt-2">Signal engine requires fresh odds — check sync status</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-gray-800 text-white rounded text-sm">Retry</button>
        </div>
      )}
      {(data??[]).length>0&&(
        <div className="grid gap-3">
          {(data??[]).sort((a,b)=>b.confidence-a.confidence).map((s,i)=>(
            <div key={i} className="bg-gray-900 rounded-xl p-4 flex items-start justify-between">
              <div className="flex-1 min-w-0 mr-4">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${s.direction==="BULLISH"?"bg-green-900 text-green-300":s.direction==="BEARISH"?"bg-red-900 text-red-300":"bg-gray-700 text-gray-300"}`}>{s.direction}</span>
                  <span className="text-xs text-gray-400">{s.signal_type}</span>
                </div>
                <div className="text-white font-medium">{s.player_name} — {s.market_key}</div>
                <div className="text-gray-400 text-xs mt-1">{s.description}</div>
              </div>
              <div className="text-right shrink-0">
                <div className="text-white font-bold">{s.value.toFixed(2)}</div>
                <div className="text-xs text-gray-400 mt-1">Conf {(s.confidence*100).toFixed(0)}%</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/pick-intel/page.tsx ───────────────────
"use client";
import { useState } from "react";
import { usePickIntel } from "@/hooks/usePickIntel";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function PickIntelPage() {
  const {sport}=useSport();
  const [minEv,setMinEv]=useState(2); const [minConf,setMinConf]=useState(0);
  const {data,isLoading,isError,error,refetch,lastUpdated}=usePickIntel(sport,50);
  const rows=(data??[]).filter(p=>p.ev_pct>=minEv&&p.brain_confidence>=minConf).sort((a,b)=>b.brain_confidence-a.brain_confidence);
  return(
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-1">PICK INTEL</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Brain-Ranked Props · Decision Cards</p>
      <div className="flex gap-4 mb-4">
        abel className="text-xs text-gray-400">Min EV%
          <input type="number" value={minEv} onChange={e=>setMinEv(Number(e.target.value))} className="ml-2 w-16 bg-gray-800 text-white text-xs rounded px-2 py-1"/>
        </label>
        abel className="text-xs text-gray-400">Min Confidence
          <input type="number" min="0" max="100" value={minConf} onChange={e=>setMinConf(Number(e.target.value))} className="ml-2 w-16 bg-gray-800 text-white text-xs rounded px-2 py-1"/>
        </label>
      </div>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={120000} label="PICK INTEL"/>
      {isLoading&&<LoadingSkeleton rows={8}/>}
      {isError&&<ErrorRetry onRetry={refetch} message={error??""}/>}
      {!isLoading&&!isError&&rows.length===0&&(
        <div className="text-center py-14 text-gray-500">
          <p>No picks match these filters</p>
          <p className="text-xs mt-2">Try lowering Min EV% or Min Confidence, or wait for next brain cycle</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-gray-800 text-white rounded text-sm">Retry</button>
        </div>
      )}
      {rows.length>0&&(
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {rows.map((p,i)=>(
            <div key={i} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <div className="flex items-start justify-between mb-3">
                <div><div className="text-white font-medium">{p.player_name}</div><div className="text-gray-400 text-xs mt-0.5">{p.market_key} · O/U {p.line} · {p.bookmaker}</div></div>
                <span className={`px-2 py-1 rounded text-xs font-bold ${p.recommendation==="OVER"?"bg-green-900 text-green-300":p.recommendation==="UNDER"?"bg-red-900 text-red-300":"bg-gray-800 text-gray-400"}`}>{p.recommendation}</span>
              </div>
              <div className="grid grid-cols-3 gap-2 mb-3">
                {[{l:"EV%",v:`${p.ev_pct>=0?"+":""}${p.ev_pct.toFixed(1)}%`,c:p.ev_pct>=2?"text-green-400":"text-gray-400"},{l:"BRAIN CONF",v:`${p.brain_confidence.toFixed(0)}%`,c:"text-blue-400"},{l:"RISK",v:p.risk_tier,c:p.risk_tier==="HIGH"?"text-green-400":p.risk_tier==="MEDIUM"?"text-amber-400":"text-red-400"}].map(s=>(
                  <div key={s.l} className="bg-gray-800 rounded p-2 text-center"><div className="text-xs text-gray-400">{s.l}</div><div className={`font-bold text-sm ${s.c}`}>{s.v}</div></div>
                ))}
              </div>
              <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden mb-2"><div style={{width:`${p.brain_confidence}%`}} className={`h-full rounded-full ${p.brain_confidence>=70?"bg-blue-500":p.brain_confidence>=50?"bg-amber-500":"bg-red-500"}`}/></div>
              {p.reasoning&&<p className="text-xs text-gray-500 line-clamp-2">{p.reasoning}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/hit-rate/page.tsx ─────────────────────
"use client";
import { useState } from "react";
import { useHitRate } from "@/hooks/useHitRate";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/apiBase";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
export default function HitRatePage() {
  const {sport}=useSport();
  const {summary,leaderboard}=useHitRate(sport);
  const [syncing,setSyncing]=useState(false);
  const triggerSync=async()=>{ setSyncing(true); try{ await fetch(`${API_BASE}/api/hit-rate/sync`,{method:"POST"}); await summary.refetch(); await leaderboard.refetch(); }finally{ setSyncing(false); }};
  return(
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div><h1 className="text-2xl font-bold text-white">HIT RATE</h1><p className="text-xs text-gray-400 uppercase tracking-widest mt-1">Model Accuracy Tracker</p></div>
        <button onClick={triggerSync} disabled={syncing} className="flex items-center gap-2 px-4 py-2 bg-gray-800 text-white rounded text-sm hover:bg-gray-700 disabled:opacity-50">
          <span className={syncing?"animate-spin":""}>{syncing?"⟳":"↻"}</span> {syncing?"Syncing...":"Trigger Result Sync"}
        </button>
      </div>
      <DataFreshnessBanner lastUpdated={summary.lastUpdated} staleMs={300000} label="HIT RATE"/>
      {summary.isLoading&&<LoadingSkeleton rows={2}/>}
      {!summary.isLoading&&summary.data&&(
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[{label:"PLATFORM ACCURACY",value:`${summary.data.platform_accuracy.toFixed(1)}%`},{label:"AVERAGE ROI",value:`${summary.data.avg_roi>=0?"+":""}${summary.data.avg_roi.toFixed(1)}%`},{label:"GRADED PICKS",value:summary.data.graded_picks.toLocaleString()},{label:"ACCURACY TREND",value:summary.data.accuracy_trend.toLocaleString()}].map(s=>(
            <div key={s.label} className="bg-gray-900 rounded-xl p-5"><div className="text-xs text-gray-400 mb-2">{s.label}</div><div className="text-3xl font-bold text-white">{s.value}</div></div>
          ))}
        </div>
      )}
      <h2 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Player Leaderboard</h2>
      {le
      {leaderboard.isLoading&&<LoadingSkeleton rows={5}/>}
      {!leaderboard.isLoading&&(leaderboard.data??[]).length===0&&(
        <div className="text-center py-10 text-gray-500">
          <p>No graded picks yet — results populate as games complete</p>
        </div>
      )}
      {(leaderboard.data??[]).length>0&&(
        <table className="w-full text-sm">
          <thead><tr className="text-gray-400 text-xs border-b border-gray-800">
            <th className="text-left py-3 px-4">PLAYER</th>
            <th className="text-right py-3 px-4">HIT RATE</th>
            <th className="text-right py-3 px-4">ROI</th>
            <th className="text-right py-3 px-4">TOTAL PICKS</th>
            <th className="text-right py-3 px-4">STREAK</th>
            <th className="text-left py-3 px-4">LAST</th>
          </tr></thead>
          <tbody>{(leaderboard.data??[]).sort((a,b)=>b.hit_rate-a.hit_rate).map((p,i)=>(
            <tr key={i} className="border-b border-gray-900 hover:bg-gray-900">
              <td className="py-3 px-4 text-white font-medium">{p.player_name}</td>
              <td className={`py-3 px-4 text-right font-bold ${p.hit_rate>=60?"text-green-400":p.hit_rate>=50?"text-amber-400":"text-red-400"}`}>{p.hit_rate.toFixed(1)}%</td>
              <td className={`py-3 px-4 text-right font-bold ${p.roi>=0?"text-green-400":"text-red-400"}`}>{p.roi>=0?"+":""}{p.roi.toFixed(1)}%</td>
              <td className="py-3 px-4 text-right text-gray-300">{p.total_picks}</td>
              <td className="py-3 px-4 text-right text-white">{p.streak>0?`W${p.streak}`:p.streak<0?`L${Math.abs(p.streak)}`:"—"}</td>
              <td className="py-3 px-4"><span className={`px-2 py-1 rounded text-xs font-bold ${p.last_result==="WIN"?"bg-green-900 text-green-300":p.last_result==="LOSS"?"bg-red-900 text-red-300":"bg-gray-800 text-gray-400"}`}>{p.last_result??"—"}</span></td>
            </tr>
          ))}</tbody>
        </table>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/props-history/page.tsx ────────────────
"use client";
import { usePropsHistory } from "@/hooks/usePropsHistory";
import { useSport } from "@/hooks/useSport";
import { DataFreshnessBanner } from "@/components/shared/DataFreshnessBanner";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
export default function PropsHistoryPage() {
  const {sport}=useSport();
  const {data,isLoading,isError,error,refetch,lastUpdated}=usePropsHistory(sport);
  return(
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-1">SETTLEMENT LOG</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Historical Verification & Model Grader</p>
      <DataFreshnessBanner lastUpdated={lastUpdated} staleMs={600000} label="HISTORY"/>
      {isLoading&&<LoadingSkeleton rows={8}/>}
      {isError&&<ErrorRetry onRetry={refetch} message={error??""}/>}
      {!isLoading&&!isError&&(data??[]).length===0&&(
        <div className="text-center py-14 text-gray-500">
          <p className="text-lg font-medium">No graded picks yet</p>
          <p className="text-sm mt-2">History builds as picks are logged and results come in</p>
          <button onClick={refetch} className="mt-4 px-4 py-2 bg-gray-800 text-white rounded text-sm">Retry</button>
        </div>
      )}
      {(data??[]).length>0&&(
        <table className="w-full text-sm">
          <thead><tr className="text-gray-400 text-xs border-b border-gray-800">
            <th className="text-left py-3 px-4">PLAYER / EVENT</th>
            <th className="text-right py-3 px-4">LINE</th>
            <th className="text-right py-3 px-4">ACTUAL</th>
            <th className="text-left py-3 px-4">RESULT</th>
            <th className="text-right py-3 px-4">TREND</th>
            <th className="text-right py-3 px-4">CONFIDENCE</th>
          </tr></thead>
          <tbody>{(data??[]).sort((a,b)=>new Date(b.graded_at).getTime()-new Date(a.graded_at).getTime()).map((p,i)=>(
            <tr key={i} className="border-b border-gray-900 hover:bg-gray-900">
              <td className="py-3 px-4"><div className="text-white font-medium">{p.player_name}</div><div className="text-gray-400 text-xs">{p.market_key}</div></td>
              <td className="py-3 px-4 text-right text-gray-300">{p.line}</td>
              <td className="py-3 px-4 text-right text-white font-medium">{p.actual_value}</td>
              <td className="py-3 px-4"><span className={`px-2 py-1 rounded text-xs font-bold ${p.result==="WIN"?"bg-green-900 text-green-300":p.result==="LOSS"?"bg-red-900 text-red-300":"bg-gray-700 text-gray-300"}`}>{p.result}</span></td>
              <td className={`py-3 px-4 text-right font-bold ${p.trend>0?"text-green-400":p.trend<0?"text-red-400":"text-gray-400"}`}>{p.trend>0?"+":""}{p.trend.toFixed(1)}</td>
              <td className="py-3 px-4 text-right text-gray-300">{p.confidence.toFixed(0)}%</td>
            </tr>
          ))}</tbody>
        </table>
      )}
    </div>
  );
}

── apps/web/src/app/(app)/settings/page.tsx ─────────────────────
"use client";
import { useSettings } from "@/hooks/useSettings";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
export default function SettingsPage() {
  const {settings,isLoading,isSaving,saveSettings,isDefault}=useSettings();
  if(isLoading) return <div className="p-6"><LoadingSkeleton rows={6}/></div>;
  if(!settings) return <div className="p-6 text-center text-gray-500"><p>Unable to load settings</p><p className="text-xs mt-2">Backend may be starting up — refresh in a moment</p></div>;
  return(
    <div className="p-6 max-w-2xl">
      <h1 className="text-2xl font-bold text-white mb-1">SETTINGS</h1>
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-6">Platform Configuration</p>
      {isDefault&&<div className="mb-4 px-4 py-3 bg-amber-900/30 border border-amber-700 rounded-lg text-amber-400 text-xs">Showing default settings — your preferences will save when you make changes</div>}
      <div className="space-y-6">
        <div className="bg-gray-900 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">DISPLAY</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div><div className="text-white text-sm">Theme</div><div className="text-gray-400 text-xs">Interface appearance</div></div>
              <select value={settings.theme} onChange={e=>saveSettings({theme:e.target.value})} className="bg-gray-800 text-white text-sm rounded px-3 py-2">
                <option value="dark">Dark</option><option value="light">Light</option>
              </select>
            </div>
            <div className="flex items-center justify-between">
              <div><div className="text-white text-sm">Default Sport</div><div className="text-gray-400 text-xs">Sport shown on load</div></div>
              <select value={settings.default_sport} onChange={e=>saveSettings({default_sport:e.target.value})} className="bg-gray-800 text-white text-sm rounded px-3 py-2">
                {[["basketball_nba","NBA"],["americanfootball_nfl","NFL"],["baseball_mlb","MLB"],["icehockey_nhl","NHL"]].map(([v,l])=><option key={v} value={v}>{l}</option>)}
              </select>
            </div>
          </div>
        </div>
        <div className="bg-gray-900 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">ENGINE</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div><div className="text-white text-sm">Min EV Threshold</div><div className="text-gray-400 text-xs">Hide signals below this EV%</div></div>
              <input type="number" min="0" max="20" step="0.5" value={settings.min_ev_threshold} onChange={e=>saveSettings({min_ev_threshold:Number(e.target.value)})} className="bg-gray-800 text-white text-sm rounded px-3 py-2 w-20 text-center"/>
            </div>
            <div className="flex items-center justify-between">
              <div><div className="text-white text-sm">Auto Sync</div><div className="text-gray-400 text-xs">Automatically fetch latest odds</div></div>
              <button onClick={()=>saveSettings({auto_sync:!settings.auto_sync})} className={`relative w-11 h-6 rounded-full transition-colors ${settings.auto_sync?"bg-green-500":"bg-gray-700"}`}>
                <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${settings.auto_sync?"translate-x-5":"translate-x-0.5"}`}/>
              </button>
            </div>
            <div className="flex items-center justify-between">
              <div><div className="text-white text-sm">Notifications</div><div className="text-gray-400 text-xs">Sharp money & steam alerts</div></div>
              <button onClick={()=>saveSettings({notifications_enabled:!settings.notifications_enabled})} className={`relative w-11 h-6 rounded-full transition-colors ${settings.notifications_enabled?"bg-green-500":"bg-gray-700"}`}>
                <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform ${settings.notifications_enabled?"translate-x-5":"translate-x-0.5"}`}/>
              </button>
            </div>
          </div>
        </div>
        <div className="bg-gray-900 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">ACCOUNT</h2>
          <div className="flex items-center justify-between">
            <div><div className="text-white text-sm">Tier</div><div className="text-gray-400 text-xs">Current subscription level</div></div>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-900 text-blue-300 uppercase">{settings.tier}</span>
          </div>
        </div>
      </div>
      {isSaving&&<div className="fixed bottom-4 right-4 bg-gray-800 text-white text-xs px-4 py-2 rounded-full shadow-lg">Saving...</div>}
    </div>
  );
}

════════════════════════════════════════════════════════════════
FINAL DEPLOYMENT CHECKLIST — DO THIS AFTER ALL CODE CHANGES
════════════════════════════════════════════════════════════════

1. RAILWAY — perplex-edge-backend Copy service → Variables:
   ADD: ODDS_API_KEY = [copy exact value from ODDS_API_KEYS variable]
   VERIFY: AI_API_KEY = [set to your Groq API key in Railway]
   VERIFY: REDIS_URL = redis://default:PASSWORD@redis.railway.internal:6379
   Then click Deploy.

2. RAILWAY — celery-beat service → Variables:
   ADD: ODDS_API_KEY = [same value as above]
   VERIFY: AI_API_KEY = [set to your Groq API key in Railway]
   Then click Deploy.

3. VERCEL — perplex-edge project → Environment Variables:
   VERIFY: NEXT_PUBLIC_API_URL = https://perplex-edge-backend-copy-production.up.railway.app
   ADD if missing: NEXT_PUBLIC_WS_URL = wss://perplex-edge-backend-copy-production.up.railway.app
   Redeploy frontend after any env var change.

4. SUPABASE — SQL Editor → run the user_settings table migration from Fix 2 above.

5. After deploy, verify platform health:
   - Dashboard → ODDS badge should update from "7 DAYS AGO" to "JUST NOW" within 5 min
   - EV+ → should show computed signals
   - Brain → decisions should appear after first ingest cycle (~2 min)
   - CLV → will populate after 2nd odds snapshot (open + close)
   - Settings → should load without error banner
   - Live → WebSocket status should show ONLINE
   - All pages → DataFreshnessBanner should show green "LIVE · updated Xs ago"

6. COMMIT MESSAGE:
   "fix: complete platform data wiring, odds key, all pages, engines, ws reconnect"
════════════════════
