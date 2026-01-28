import { useState, useEffect, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';

interface UseAutoRefreshOptions {
  /** Refresh interval in milliseconds */
  interval?: number;
  /** Initial enabled state */
  enabled?: boolean;
}

interface UseAutoRefreshReturn {
  /** Whether auto-refresh is enabled */
  isEnabled: boolean;
  /** Toggle auto-refresh on/off */
  toggle: () => void;
  /** Enable auto-refresh */
  enable: () => void;
  /** Disable auto-refresh */
  disable: () => void;
  /** Timestamp of last refresh */
  lastUpdated: Date | null;
  /** Trigger a manual refresh */
  refresh: () => void;
  /** Time until next refresh (in seconds) */
  nextRefreshIn: number;
}

export function useAutoRefresh(options: UseAutoRefreshOptions = {}): UseAutoRefreshReturn {
  const { interval = 5 * 60 * 1000, enabled: initialEnabled = true } = options;

  const queryClient = useQueryClient();
  const [isEnabled, setIsEnabled] = useState(initialEnabled);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [nextRefreshIn, setNextRefreshIn] = useState(interval / 1000);

  // Manual refresh function
  const refresh = useCallback(() => {
    // Invalidate all queries to trigger refetch
    queryClient.invalidateQueries();
    setLastUpdated(new Date());
    setNextRefreshIn(interval / 1000);
  }, [queryClient, interval]);

  // Toggle function
  const toggle = useCallback(() => {
    setIsEnabled((prev) => !prev);
  }, []);

  const enable = useCallback(() => setIsEnabled(true), []);
  const disable = useCallback(() => setIsEnabled(false), []);

  // Auto-refresh effect
  useEffect(() => {
    if (!isEnabled) return;

    // Initial update timestamp
    if (!lastUpdated) {
      setLastUpdated(new Date());
    }

    // Countdown timer
    const countdownInterval = setInterval(() => {
      setNextRefreshIn((prev) => {
        if (prev <= 1) {
          // Time to refresh
          refresh();
          return interval / 1000;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      clearInterval(countdownInterval);
    };
  }, [isEnabled, interval, lastUpdated, refresh]);

  return {
    isEnabled,
    toggle,
    enable,
    disable,
    lastUpdated,
    refresh,
    nextRefreshIn,
  };
}

/**
 * Format seconds into a human-readable string
 */
export function formatTimeRemaining(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  if (remainingSeconds === 0) {
    return `${minutes}m`;
  }
  return `${minutes}m ${remainingSeconds}s`;
}

/**
 * Format a date into a relative time string
 */
export function formatLastUpdated(date: Date | null): string {
  if (!date) return 'Never';
  
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  
  if (diffSeconds < 5) return 'Just now';
  if (diffSeconds < 60) return `${diffSeconds}s ago`;
  
  const diffMinutes = Math.floor(diffSeconds / 60);
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  
  const diffHours = Math.floor(diffMinutes / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  
  return date.toLocaleDateString();
}

export default useAutoRefresh;
