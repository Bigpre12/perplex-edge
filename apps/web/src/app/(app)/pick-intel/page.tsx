"use client";

import React, { Suspense, useCallback, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useSport } from "@/hooks/useSport";
import { API_BASE } from "@/lib/api";
import { toArray } from "@/lib/utils/data-guards";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import {
  Sparkles,
  Clock,
  TrendingUp,
  Plus,
  X,
  Layers,
  ChevronDown,
} from "lucide-react";
import { clsx } from "clsx";

export interface PickIntelRow {
  id: number;
  player_name: string;
  team: string;
  matchup: string;
  market_label: string;
  market_key: string | null;
  line: number;
  recommended_side: string;
  recommended_odds: number;
  has_odds: boolean;
  best_book: string;
  ev_percentage: number;
  ev_tier: string;
  confidence: number;
  implied_prob: number;
  tags: string[];
  reasoning: string;
  steam_signal: boolean;
  whale_signal: boolean;
  sharp_conflict: boolean;
  is_best_line: boolean;
  game_start_time: string | null;
  sport: string;
  action_score: number;
  game_id: string;
}

function formatAmericanOdds(odds?: number | null): string {
  if (odds == null || Number.isNaN(Number(odds)) || Number(odds) === 0) return "—";
  const n = Number(odds);
  return n > 0 ? `+${n}` : `${n}`;
}

type SortKey = "brain" | "ev" | "confidence";

const MARKETS = ["ALL", "POINTS", "ASSISTS", "REBOUNDS", "THREES"] as const;

export default function PickIntelPage() {
  return (
    <Suspense
      fallback={
        <div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">
          Loading pick intel…
        </div>
      }
    >
      <PickIntelContent />
    </Suspense>
  );
}

function PickIntelContent() {
  const { sport } = useSport();
  const [minEv, setMinEv] = useState(2);
  const [minConfidence, setMinConfidence] = useState(0);
  const [market, setMarket] = useState<(typeof MARKETS)[number]>("ALL");
  const [limit, setLimit] = useState(50);
  const [sortKey, setSortKey] = useState<SortKey>("brain");
  const [parlay, setParlay] = useState<PickIntelRow[]>([]);

  const queryUrl = useMemo(() => {
    const p = new URLSearchParams();
    p.set("sport", sport);
    p.set("min_ev", String(minEv));
    p.set("min_confidence", String(minConfidence));
    p.set("limit", String(limit));
    if (market !== "ALL") p.set("market", market);
    return `${API_BASE}/api/pick-intel?${p.toString()}`;
  }, [sport, minEv, minConfidence, limit, market]);

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ["pick-intel", sport, minEv, minConfidence, market, limit],
    queryFn: async () => {
      const r = await fetch(queryUrl);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      return toArray<PickIntelRow>(json?.picks ?? json);
    },
    refetchInterval: 60_000,
  });

  const sorted = useMemo(() => {
    const rows = [...(data ?? [])];
    if (sortKey === "ev") {
      rows.sort((a, b) => b.ev_percentage - a.ev_percentage);
    } else if (sortKey === "confidence") {
      rows.sort((a, b) => b.confidence - a.confidence);
    } else {
      rows.sort((a, b) => b.action_score - a.action_score);
    }
    return rows;
  }, [data, sortKey]);

  const toggleParlay = useCallback((row: PickIntelRow) => {
    setParlay((prev) => {
      const exists = prev.some((p) => p.id === row.id);
      if (exists) return prev.filter((p) => p.id !== row.id);
      if (prev.length >= 8) return prev;
      return [...prev, row];
    });
  }, []);

  const inParlay = useCallback(
    (id: number) => parlay.some((p) => p.id === id),
    [parlay]
  );

  if (isLoading) {
    return (
      <div className="space-y-6 pt-6 px-4 pb-32">
        <Skeleton className="h-10 w-56 mb-4" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-72 w-full rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <ErrorBanner message="Pick Intel unavailable." onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div className="pb-40 space-y-8 pt-6 px-4">
      <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-purple/10 p-2 rounded-lg border border-brand-purple/25">
              <Sparkles
                size={24}
                className="text-brand-purple shadow-glow shadow-brand-purple/30"
              />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">
              Pick Intel
            </h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest mb-4 italic">
            Brain-ranked props · decision cards
          </p>
          <SportSelector />
        </div>
        <div className="flex flex-col items-end gap-2">
          <div className="text-[9px] font-black text-textMuted uppercase tracking-widest flex items-center gap-1.5">
            <Clock size={12} className="text-brand-cyan" />
            Auto refresh · 60s
            {isFetching && (
              <span className="text-brand-cyan animate-pulse">· syncing</span>
            )}
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-4 bg-lucrix-surface border border-lucrix-border rounded-2xl p-4">
        <label className="flex flex-col gap-1 min-w-[140px] flex-1">
          <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">
            Min EV %
          </span>
          <input
            type="number"
            step={0.5}
            min={-20}
            max={50}
            value={minEv}
            onChange={(e) => setMinEv(Number(e.target.value) || 0)}
            className="bg-lucrix-dark border border-lucrix-border rounded-lg px-3 py-2 text-sm text-white font-mono"
          />
        </label>
        <label className="flex flex-col gap-1 min-w-[160px] flex-1">
          <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">
            Min confidence (0–1)
          </span>
          <input
            type="number"
            step={0.05}
            min={0}
            max={1}
            value={minConfidence}
            onChange={(e) => setMinConfidence(Number(e.target.value) || 0)}
            className="bg-lucrix-dark border border-lucrix-border rounded-lg px-3 py-2 text-sm text-white font-mono"
          />
        </label>
        <label className="flex flex-col gap-1 min-w-[140px] flex-1">
          <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">
            Market
          </span>
          <div className="relative">
            <select
              value={market}
              onChange={(e) =>
                setMarket(e.target.value as (typeof MARKETS)[number])
              }
              className="w-full appearance-none bg-lucrix-dark border border-lucrix-border rounded-lg px-3 py-2 text-sm text-white font-bold uppercase tracking-wide pr-8"
            >
              {MARKETS.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            <ChevronDown
              size={16}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-textMuted pointer-events-none"
            />
          </div>
        </label>
        <label className="flex flex-col gap-1 min-w-[140px] flex-1">
          <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">
            Sort
          </span>
          <div className="relative">
            <select
              value={sortKey}
              onChange={(e) => setSortKey(e.target.value as SortKey)}
              className="w-full appearance-none bg-lucrix-dark border border-lucrix-border rounded-lg px-3 py-2 text-sm text-white font-bold pr-8"
            >
              <option value="brain">Brain rank</option>
              <option value="ev">EV %</option>
              <option value="confidence">Confidence</option>
            </select>
            <ChevronDown
              size={16}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-textMuted pointer-events-none"
            />
          </div>
        </label>
        <label className="flex flex-col gap-1 min-w-[100px] w-full sm:w-auto">
          <span className="text-[9px] font-black text-textMuted uppercase tracking-widest">
            Limit
          </span>
          <input
            type="number"
            min={1}
            max={100}
            value={limit}
            onChange={(e) =>
              setLimit(Math.min(100, Math.max(1, Number(e.target.value) || 50)))
            }
            className="bg-lucrix-dark border border-lucrix-border rounded-lg px-3 py-2 text-sm text-white font-mono"
          />
        </label>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {sorted.map((row) => (
          <article
            key={row.id}
            className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 hover:border-brand-purple/35 transition-all shadow-card overflow-hidden group"
          >
            <div className="flex justify-between items-start gap-4 mb-4">
              <div>
                <div className="text-lg font-black text-white font-display italic uppercase tracking-tight">
                  {row.player_name}
                </div>
                <div className="text-[10px] font-bold text-textSecondary uppercase tracking-widest mt-1">
                  {row.team} · {row.matchup}
                </div>
              </div>
              <div
                className={clsx(
                  "text-[9px] font-black uppercase tracking-widest px-2 py-1 rounded border shrink-0",
                  row.ev_tier === "Strong edge" &&
                    "bg-brand-success/15 text-brand-success border-brand-success/25",
                  row.ev_tier === "Positive EV" &&
                    "bg-brand-cyan/10 text-brand-cyan border-brand-cyan/25",
                  row.ev_tier === "Marginal" &&
                    "bg-lucrix-elevated text-textMuted border-lucrix-border"
                )}
              >
                {row.ev_tier}
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="text-xs font-black text-white">
                {row.market_label}
              </span>
              <span className="text-textMuted">·</span>
              <span className="text-sm font-mono text-brand-cyan">
                O/U {row.line}
              </span>
              <span className="text-textMuted">·</span>
              <span className="text-sm font-black italic text-white">
                {row.recommended_side} {row.has_odds ? formatAmericanOdds(row.recommended_odds) : "—"}
              </span>
              <span className="text-[10px] text-textMuted uppercase">
                @ {row.best_book}
              </span>
            </div>

            <div className="flex flex-wrap gap-2 mb-4">
              {row.tags.map((t) => (
                <span
                  key={t}
                  className="text-[8px] font-black uppercase tracking-widest px-2 py-0.5 rounded border border-lucrix-border bg-lucrix-dark text-textSecondary"
                >
                  {t}
                </span>
              ))}
            </div>

            <div className="grid grid-cols-3 gap-3 mb-4">
              <div>
                <div className="text-[8px] font-black text-textMuted uppercase mb-0.5">
                  EV %
                </div>
                <div className="text-lg font-black font-display italic text-brand-success">
                  +{row.ev_percentage.toFixed(1)}%
                </div>
              </div>
              <div>
                <div className="text-[8px] font-black text-textMuted uppercase mb-0.5">
                  Confidence
                </div>
                <div className="text-lg font-black font-display italic text-white">
                  {row.confidence === 0 && !row.has_odds ? "N/A" : `${row.confidence.toFixed(0)}%`}
                </div>
              </div>
              <div>
                <div className="text-[8px] font-black text-textMuted uppercase mb-0.5">
                  Implied
                </div>
                <div className="text-lg font-black font-display italic text-textSecondary">
                  {row.implied_prob.toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="bg-lucrix-dark/60 border border-lucrix-border/60 rounded-xl p-4 mb-4">
              <p className="text-[11px] font-bold text-textSecondary italic leading-relaxed">
                {row.reasoning}
              </p>
            </div>

            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-1 text-[9px] font-black text-textMuted uppercase tracking-widest">
                <TrendingUp size={12} className="text-brand-purple" />
                Score {row.action_score.toFixed(2)}
              </div>
              <button
                type="button"
                onClick={() => toggleParlay(row)}
                className={clsx(
                  "flex items-center gap-2 px-3 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-colors border",
                  inParlay(row.id)
                    ? "bg-brand-danger/15 border-brand-danger/40 text-brand-danger"
                    : "bg-brand-purple/15 border-brand-purple/35 text-brand-purple hover:bg-brand-purple/25"
                )}
              >
                {inParlay(row.id) ? (
                  <>
                    <X size={14} /> Remove
                  </>
                ) : (
                  <>
                    <Plus size={14} /> Parlay tray
                  </>
                )}
              </button>
            </div>
          </article>
        ))}
        {sorted.length === 0 && (
          <div className="col-span-full text-center py-24 text-textMuted font-black uppercase italic tracking-widest border border-dashed border-lucrix-border rounded-2xl">
            No picks match these filters.
          </div>
        )}
      </div>

      {parlay.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 z-40 border-t border-lucrix-border bg-lucrix-dark/95 backdrop-blur-md md:left-[240px]">
          <div className="max-w-6xl mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center gap-3 justify-between">
            <div className="flex items-center gap-2 text-white">
              <Layers size={18} className="text-brand-purple" />
              <span className="text-xs font-black uppercase tracking-widest">
                Parlay tray · {parlay.length} leg{parlay.length === 1 ? "" : "s"}
              </span>
            </div>
            <div className="flex flex-wrap gap-2 flex-1 min-w-0">
              {parlay.map((leg) => (
                <button
                  key={leg.id}
                  type="button"
                  onClick={() => toggleParlay(leg)}
                  className="text-[10px] font-bold uppercase tracking-wide px-2 py-1 rounded border border-lucrix-border bg-lucrix-surface text-textSecondary hover:text-white hover:border-brand-danger/40 truncate max-w-[220px]"
                  title={`${leg.player_name} ${leg.recommended_side}`}
                >
                  {leg.player_name.split(" ").pop()} {leg.recommended_side}
                </button>
              ))}
            </div>
            <button
              type="button"
              onClick={() => setParlay([])}
              className="text-[10px] font-black uppercase tracking-widest text-brand-danger border border-brand-danger/30 px-3 py-2 rounded-lg hover:bg-brand-danger/10 shrink-0"
            >
              Clear tray
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
