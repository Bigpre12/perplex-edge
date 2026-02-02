/**
 * Feature Flags Context
 * 
 * Provides feature flag management for Lite vs Pro versioning.
 * Flags can be configured via environment variables or runtime config.
 */

import { createContext, useContext, ReactNode } from 'react';

// =============================================================================
// Feature Flag Types
// =============================================================================

export interface FeatureFlags {
  // Core features
  playerProps: boolean;
  gameLines: boolean;
  hundredPercentHits: boolean;
  parlayBuilder: boolean;
  myBets: boolean;
  
  // Premium features
  liveEV: boolean;
  analytics: boolean;
  backtest: boolean;
  altLines: boolean;
  watchlists: boolean;
  modelPerformance: boolean;
  
  // Sports (can be toggled for different license tiers)
  nba: boolean;
  nfl: boolean;
  mlb: boolean;
  nhl: boolean;
  ncaab: boolean;
  ncaaf: boolean;
  atp: boolean;
  wta: boolean;
  
  // Pro-only features
  exportData: boolean;
  advancedFilters: boolean;
  autoGenerate: boolean;
  sharedCards: boolean;
}

// =============================================================================
// Default Flags (Full/Pro version - all enabled)
// =============================================================================

const DEFAULT_FLAGS: FeatureFlags = {
  // Core features - always enabled
  playerProps: true,
  gameLines: true,
  hundredPercentHits: true,
  parlayBuilder: true,
  myBets: true,
  
  // Premium features - enabled in Pro
  liveEV: true,
  analytics: true,
  backtest: true,
  altLines: true,
  watchlists: true,
  modelPerformance: true,
  
  // All sports enabled in Pro
  nba: true,
  nfl: true,
  mlb: true,
  nhl: true,
  ncaab: true,
  ncaaf: true,
  atp: true,
  wta: true,
  
  // Pro-only features
  exportData: true,
  advancedFilters: true,
  autoGenerate: true,
  sharedCards: true,
};

// =============================================================================
// Lite Version Flags (restricted features)
// =============================================================================

export const LITE_FLAGS: FeatureFlags = {
  // Core features - enabled
  playerProps: true,
  gameLines: true,
  hundredPercentHits: true,
  parlayBuilder: true,
  myBets: false, // Lite doesn't have bet tracking
  
  // Premium features - disabled in Lite
  liveEV: false,
  analytics: false,
  backtest: false,
  altLines: false,
  watchlists: false,
  modelPerformance: false,
  
  // Limited sports in Lite (NBA and NFL only)
  nba: true,
  nfl: true,
  mlb: false,
  nhl: false,
  ncaab: false,
  ncaaf: false,
  atp: false,
  wta: false,
  
  // Pro-only features - disabled
  exportData: false,
  advancedFilters: false,
  autoGenerate: false,
  sharedCards: false,
};

// =============================================================================
// Load Flags from Environment
// =============================================================================

function loadFlagsFromEnv(): Partial<FeatureFlags> {
  const flags: Partial<FeatureFlags> = {};
  
  // Check for tier-based preset
  const tier = import.meta.env.VITE_FEATURE_TIER;
  if (tier === 'lite') {
    return LITE_FLAGS;
  }
  
  // Individual feature overrides
  if (import.meta.env.VITE_ENABLE_LIVE_EV !== undefined) {
    flags.liveEV = import.meta.env.VITE_ENABLE_LIVE_EV === 'true';
  }
  if (import.meta.env.VITE_ENABLE_ANALYTICS !== undefined) {
    flags.analytics = import.meta.env.VITE_ENABLE_ANALYTICS === 'true';
  }
  if (import.meta.env.VITE_ENABLE_BACKTEST !== undefined) {
    flags.backtest = import.meta.env.VITE_ENABLE_BACKTEST === 'true';
  }
  if (import.meta.env.VITE_ENABLE_MY_BETS !== undefined) {
    flags.myBets = import.meta.env.VITE_ENABLE_MY_BETS === 'true';
  }
  
  // Sport flags
  if (import.meta.env.VITE_ENABLE_MLB !== undefined) {
    flags.mlb = import.meta.env.VITE_ENABLE_MLB === 'true';
  }
  if (import.meta.env.VITE_ENABLE_NHL !== undefined) {
    flags.nhl = import.meta.env.VITE_ENABLE_NHL === 'true';
  }
  if (import.meta.env.VITE_ENABLE_NCAAB !== undefined) {
    flags.ncaab = import.meta.env.VITE_ENABLE_NCAAB === 'true';
  }
  if (import.meta.env.VITE_ENABLE_TENNIS !== undefined) {
    flags.atp = import.meta.env.VITE_ENABLE_TENNIS === 'true';
    flags.wta = import.meta.env.VITE_ENABLE_TENNIS === 'true';
  }
  
  return flags;
}

// =============================================================================
// Context
// =============================================================================

const FeatureFlagsContext = createContext<FeatureFlags>(DEFAULT_FLAGS);

export function FeatureFlagsProvider({ children }: { children: ReactNode }) {
  // Merge default flags with environment overrides
  const envFlags = loadFlagsFromEnv();
  const flags: FeatureFlags = { ...DEFAULT_FLAGS, ...envFlags };
  
  return (
    <FeatureFlagsContext.Provider value={flags}>
      {children}
    </FeatureFlagsContext.Provider>
  );
}

// =============================================================================
// Hooks
// =============================================================================

export function useFeatureFlags(): FeatureFlags {
  return useContext(FeatureFlagsContext);
}

export function useFeatureFlag(flag: keyof FeatureFlags): boolean {
  const flags = useContext(FeatureFlagsContext);
  return flags[flag];
}

// Check if a sport is enabled
export function useSportEnabled(sportId: number): boolean {
  const flags = useContext(FeatureFlagsContext);
  
  const sportFlags: Record<number, keyof FeatureFlags> = {
    30: 'nba',
    31: 'nfl',
    32: 'ncaab',
    40: 'mlb',
    41: 'ncaaf',
    42: 'atp',
    43: 'wta',
    44: 'nhl',
  };
  
  const flagKey = sportFlags[sportId];
  return flagKey ? flags[flagKey] : false;
}
