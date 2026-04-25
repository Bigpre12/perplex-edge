"use client";

type Props = {
  lastUpdated?: string | null;
  staleMs?: number;
  expiredMs?: number;
  label?: string;
};

export default function DataFreshnessBanner({
  lastUpdated,
  staleMs = 60_000,
  expiredMs = 180_000,
  label = "Data freshness",
}: Props) {
  if (!lastUpdated) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-white/70">
        {label}: waiting for first sync
      </div>
    );
  }

  const ageMs = Math.max(0, Date.now() - new Date(lastUpdated).getTime());
  const seconds = Math.floor(ageMs / 1000);
  const tone =
    ageMs >= expiredMs
      ? "border-red-500/30 bg-red-500/10 text-red-300"
      : ageMs >= staleMs
        ? "border-amber-500/30 bg-amber-500/10 text-amber-300"
        : "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
  const state = ageMs >= expiredMs ? "stale" : ageMs >= staleMs ? "aging" : "fresh";

  return (
    <div className={`rounded-xl border px-3 py-2 text-xs font-semibold ${tone}`}>
      {label}: {state} ({seconds}s ago)
    </div>
  );
}
