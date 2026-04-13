"use client";
import { useQuery } from "@tanstack/react-query";
import api, { unwrap } from "@/lib/api";

export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: api.metrics,
    refetchInterval: 30000,
  });
}

export function usePropsScored(sport = "basketball_nba") {
  return useQuery({
    queryKey: ["propsScored", sport],
    queryFn: async () => unwrap(await api.propsScored(sport, 50)),
  });
}

export function useEvTop(sport = "basketball_nba") {
  return useQuery({
    queryKey: ["evTop", sport],
    queryFn: async () => unwrap(await api.ev.top(sport, 10)),
  });
}

export function useInjuries(sport = "basketball_nba") {
  return useQuery({
    queryKey: ["injuries", sport],
    queryFn: async () => unwrap(await api.injuries(sport)),
  });
}

export function useNews(sport = "basketball_nba") {
  return useQuery({
    queryKey: ["news", sport],
    queryFn: async () => unwrap(await api.news(sport)),
  });
}

export function useLineMovement(sport = "basketball_nba") {
  return useQuery({
    queryKey: ["lineMovement", sport],
    queryFn: async () => unwrap(await api.lineMovement(sport)),
  });
}

export function useFreshness(sport = "basketball_nba") {
  return useQuery({
    queryKey: ["freshness", sport],
    queryFn: async () => await api.signals.freshness(sport),
    refetchInterval: 15000,
  });
}
