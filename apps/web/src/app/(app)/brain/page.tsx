"use client";

import { BrainCircuit } from "lucide-react";
import { useSport } from "@/hooks/useSport";
import { useBrainData } from "@/hooks/useBrainData";
import { LoadingSkeleton } from "@/components/shared/LoadingSkeleton";
import { ErrorRetry } from "@/components/shared/ErrorRetry";
import DataFreshnessBanner from "@/components/shared/DataFreshnessBanner";
import SportSelector from "@/components/shared/SportSelector";
import { EmptyState } from "@/components/shared/EmptyState";

export default function BrainPage() {
  const { sport } = useSport();
  const { decisions, health, metrics, loading, isError, error, refetch, lastUpdated } = useBrainData(sport as any);

  return (
    <div className="pb-24 space-y-6 pt-6 px-4 text-white">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black uppercase italic flex items-center gap-2">
            <BrainCircuit className="text-brand-purple" /> Neural Engine
          </h1>
          <p className="text-xs text-textMuted">Live decisions, metrics, and health state.</p>
          <div className="mt-3"><SportSelector /></div>
        </div>
        <DataFreshnessBanner lastUpdated={lastUpdated} label="Brain stream" />
      </div>

      {loading ? <LoadingSkeleton rows={6} /> : null}
      {isError ? <ErrorRetry message={error || "Failed to load brain data"} onRetry={() => refetch()} /> : null}

      {!loading && !isError ? (
        <>
          <div className="rounded-2xl border border-lucrix-border bg-lucrix-surface p-4">
            <div className="text-xs uppercase text-textMuted mb-2">Engine status</div>
            <div className="text-lg font-black">{health?.status || "UNKNOWN"}</div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <MetricCard label="Accuracy 7d" value={Number(metrics?.accuracy_7d || 0).toFixed(1) + "%"} />
            <MetricCard label="Accuracy 30d" value={Number(metrics?.accuracy_30d || 0).toFixed(1) + "%"} />
            <MetricCard label="ROI 7d" value={Number(metrics?.roi_7d || 0).toFixed(1) + "%"} />
            <MetricCard label="Avg confidence" value={Number(metrics?.avg_confidence || 0).toFixed(1) + "%"} />
          </div>
          {(decisions || []).length === 0 ? (
            <EmptyState
              title="No data available. Waiting for market sync."
              description="Neural decisions will appear once the market ingestion cycle completes."
              onRetry={() => refetch()}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(decisions || []).map((d: any, i: number) => (
                <div key={d?.id || i} className="rounded-2xl border border-lucrix-border bg-lucrix-surface p-4">
                  <div className="text-sm font-black">{d?.details?.player_name || d?.player || "Unknown Player"}</div>
                  <div className="text-xs text-textMuted mt-1">{d?.details?.stat_type || d?.market || "Market"}</div>
                  <div className="text-xs mt-2">{d?.reasoning || "No reasoning provided."}</div>
                  <div className="mt-3 text-[11px] text-brand-cyan">
                    Rec: {d?.action || d?.recommendation || d?.details?.side || "PASS"}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-lucrix-border bg-lucrix-surface p-3">
      <div className="text-[10px] uppercase text-textMuted">{label}</div>
      <div className="text-sm font-black">{value}</div>
    </div>
  );
}
