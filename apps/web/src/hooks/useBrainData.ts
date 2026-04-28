"use client";
import { SportKey } from "@/lib/sports.config";
import { useBackendData } from "@/hooks/useBackendData";
import { normalizeSportKey } from "@/constants/sports";

export interface BrainDecision {
    action: string
    reasoning: string
    details: {
        player_name: string
        stat_type: string
        line_value: number
        side: string
        edge: number
        confidence: number
    }
    confidence_tier?: string
}

export interface SystemHealth {
    status: string
    ai_evaluation: {
        action: string
        target: string
        reason: string
        is_critical: boolean
    }
    system_metrics_evaluated: {
        cpu_usage: number
        error_rate: number
    }
}

export interface MarketIntelItem {
    title: string
    content: string
    type: 'news' | 'injury' | 'sharp'
    timestamp: string
}

import { useSport } from "@/context/SportContext";

export const useBrainData = (requestedSportKey?: SportKey) => {
  const { selectedSport } = useSport();
  const sportKey = normalizeSportKey(requestedSportKey || selectedSport);
  const decisionsReq = useBackendData<any>("/api/brain/decisions", { params: { sport: sportKey }, pollMs: 30_000 });
  const healthReq = useBackendData<SystemHealth>("/api/brain/status", { pollMs: 30_000 });
  const metricsReq = useBackendData<any>("/api/brain/metrics", { pollMs: 60_000 });
  const intelReq = useBackendData<any>("/api/intel", { params: { sport: sportKey }, pollMs: 60_000 });

  return {
    decisions: (decisionsReq.data?.decisions || decisionsReq.data?.data || []) as BrainDecision[],
    health: (healthReq.data || null) as SystemHealth | null,
    metrics: metricsReq.data || {},
    marketIntel: (intelReq.data?.items || intelReq.data?.data || intelReq.data || []) as MarketIntelItem[],
    loading: decisionsReq.isLoading || healthReq.isLoading,
    isError: decisionsReq.isError && healthReq.isError, // Only hard-fail if both critical endpoints fail
    error: decisionsReq.error || healthReq.error || metricsReq.error || intelReq.error,
    lastUpdated: [decisionsReq.lastUpdated, healthReq.lastUpdated, metricsReq.lastUpdated, intelReq.lastUpdated].filter(Boolean).sort().at(-1) || null,
    refetch: async () => {
      await Promise.all([decisionsReq.refetch(), healthReq.refetch(), metricsReq.refetch(), intelReq.refetch()]);
    },
  };
};
