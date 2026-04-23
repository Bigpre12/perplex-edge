"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useReconnectingWs } from "./useReconnectingWs";

interface WSFallbackOptions<T> {
  wsEndpoint: string;
  queryKey: any[];
  queryFn: () => Promise<T>;
  enabled?: boolean;
  refetchInterval?: number;
}

/**
 * useWSFallback - Connects to WebSocket, falls back to REST polling if WS is down.
 */
export function useWSFallback<T>(options: WSFallbackOptions<T>) {
  const [localData, setLocalData] = useState<T | null>(null);
  
  const { data: wsData, status: wsStatus } = useReconnectingWs(
    options.wsEndpoint,
    (newData) => setLocalData(newData)
  );

  const isWSOpen = wsStatus === "open";

  const { data: restData, isLoading, isError } = useQuery({
    queryKey: options.queryKey,
    queryFn: options.queryFn,
    enabled: options.enabled !== false && !isWSOpen, // Only poll if WS is not open
    refetchInterval: options.refetchInterval || 15_000, // Default 15s fallback
    retry: 2,
    retryDelay: (a) => Math.min(2000 * 2 ** a, 12_000),
  });

  // Use WS data if available, otherwise fallback to REST data
  const data = isWSOpen ? (wsData || localData) : restData;

  return {
    data,
    isLoading: !data && isLoading,
    isError,
    isWSOpen,
  };
}
