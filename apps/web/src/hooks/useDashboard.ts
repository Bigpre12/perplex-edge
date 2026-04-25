"use client";

import { useMemo } from "react";
import { useBackendData } from "@/hooks/useBackendData";
import { normalizeSportKey } from "@/constants/sports";

const toList = (value: unknown): any[] => {
  if (Array.isArray(value)) return value;
  if (!value || typeof value !== "object") return [];
  const v = value as Record<string, unknown>;
  const nested = v.data ?? v.results ?? v.items ?? v.props ?? v.alerts ?? [];
  return Array.isArray(nested) ? nested : [];
};

export function useDashboard(sport = "basketball_nba") {
  const normalizedSport = normalizeSportKey(sport);
  const health = useBackendData<any>("/api/health", { pollMs: 15_000 });
  const brain = useBackendData<any>("/api/brain/status", { pollMs: 15_000 });
  const props = useBackendData<any>("/api/props", { params: { sport: normalizedSport }, pollMs: 15_000 });
  const whale = useBackendData<any>("/api/whale", { params: { sport: normalizedSport }, pollMs: 15_000 });
  const evTop = useBackendData<any>("/api/ev/top", { params: { sport: normalizedSport, limit: 10 }, pollMs: 15_000 });

  const isLoading = health.isLoading || brain.isLoading || props.isLoading || whale.isLoading || evTop.isLoading;
  const isError = health.isError || brain.isError || props.isError || whale.isError || evTop.isError;
  const error = health.error || brain.error || props.error || whale.error || evTop.error;

  const data = useMemo(
    () => ({
      health: health.data,
      brain: brain.data,
      props: toList(props.data),
      whales: toList(whale.data),
      evTop: toList(evTop.data),
    }),
    [health.data, brain.data, props.data, whale.data, evTop.data],
  );

  const lastUpdated = [health.lastUpdated, brain.lastUpdated, props.lastUpdated, whale.lastUpdated, evTop.lastUpdated]
    .filter(Boolean)
    .sort()
    .at(-1) || null;

  return {
    data,
    isLoading,
    isError,
    error,
    lastUpdated,
    refetch: async () => {
      await Promise.all([health.refetch(), brain.refetch(), props.refetch(), whale.refetch(), evTop.refetch()]);
    },
  };
}
