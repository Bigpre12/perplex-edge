"use client";

import { useAuth } from "./useAuth";
import { Tier, checkTierAccess } from "@/lib/tier";

interface TierGateOptions {
  requiredTier: Tier;
}

/**
 * useTierGate - Wraps a query result and checks if the user has access.
 * Returns { data, isLocked, isLoading }.
 */
export function useTierGate<T>(
  queryResult: { data: T | undefined; isLoading: boolean; error: any },
  options: TierGateOptions
) {
  const { tier, loading: authLoading } = useAuth();
  
  const isLocked = !authLoading && !checkTierAccess(tier, options.requiredTier);
  const isLoading = authLoading || queryResult.isLoading;

  // If the API explicitly returns a 403, we also mark it as locked
  const isApiLocked = queryResult.error?.message?.includes("403") || queryResult.error?.status === 403;

  return {
    data: (isLocked || isApiLocked) ? undefined : queryResult.data,
    isLocked: isLocked || isApiLocked,
    isLoading,
    error: queryResult.error,
  };
}
