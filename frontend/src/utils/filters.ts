/**
 * Filter utilities for consistent filter state detection across components.
 * 
 * Provides helpers to determine if filters are active and manage filter state.
 */

// =============================================================================
// Types
// =============================================================================

export interface PropFilterState {
  minEv?: number;
  minConfidence?: number;
  riskLevels?: string[];
  excludedStatTypes?: Set<string> | string[];
  excludedPlayers?: Set<string> | string[];
  sportsbook?: string | null;
  side?: 'over' | 'under' | null;
  searchQuery?: string;
}

export interface PropFilterDefaults {
  minEv: number;
  minConfidence: number;
  riskLevels: string[];
  excludedStatTypes: string[];
  excludedPlayers: string[];
  sportsbook: null;
  side: null;
  searchQuery: string;
}

// Default filter values (matching PlayerPropsTab defaults)
export const DEFAULT_PROP_FILTERS: PropFilterDefaults = {
  minEv: 0,
  minConfidence: 0,
  riskLevels: [],  // Empty = all risk levels
  excludedStatTypes: [],
  excludedPlayers: [],
  sportsbook: null,
  side: null,
  searchQuery: '',
};

// =============================================================================
// Filter Detection
// =============================================================================

/**
 * Check if any prop filters are active (different from defaults).
 */
export function hasActiveFilters(
  filters: PropFilterState,
  defaults: Partial<PropFilterDefaults> = DEFAULT_PROP_FILTERS
): boolean {
  const d = { ...DEFAULT_PROP_FILTERS, ...defaults };
  
  // Check EV filter
  if (filters.minEv !== undefined && filters.minEv !== d.minEv) {
    return true;
  }
  
  // Check confidence filter
  if (filters.minConfidence !== undefined && filters.minConfidence !== d.minConfidence) {
    return true;
  }
  
  // Check risk levels
  if (filters.riskLevels && filters.riskLevels.length > 0) {
    return true;
  }
  
  // Check excluded stat types
  const excludedStats = filters.excludedStatTypes;
  if (excludedStats) {
    const size = excludedStats instanceof Set ? excludedStats.size : excludedStats.length;
    if (size > 0) {
      return true;
    }
  }
  
  // Check excluded players
  const excludedPlayers = filters.excludedPlayers;
  if (excludedPlayers) {
    const size = excludedPlayers instanceof Set ? excludedPlayers.size : excludedPlayers.length;
    if (size > 0) {
      return true;
    }
  }
  
  // Check sportsbook filter
  if (filters.sportsbook !== undefined && filters.sportsbook !== d.sportsbook) {
    return true;
  }
  
  // Check side filter
  if (filters.side !== undefined && filters.side !== d.side) {
    return true;
  }
  
  // Check search query
  if (filters.searchQuery && filters.searchQuery.trim() !== '') {
    return true;
  }
  
  return false;
}

/**
 * Get a human-readable summary of active filters.
 */
export function getFilterSummary(filters: PropFilterState): string[] {
  const active: string[] = [];
  
  if (filters.minEv !== undefined && filters.minEv > 0) {
    active.push(`EV ≥ ${(filters.minEv * 100).toFixed(0)}%`);
  }
  
  if (filters.minConfidence !== undefined && filters.minConfidence > 0) {
    active.push(`Conf ≥ ${(filters.minConfidence * 100).toFixed(0)}%`);
  }
  
  if (filters.riskLevels && filters.riskLevels.length > 0) {
    active.push(`Risk: ${filters.riskLevels.join(', ')}`);
  }
  
  const excludedStats = filters.excludedStatTypes;
  if (excludedStats) {
    const size = excludedStats instanceof Set ? excludedStats.size : excludedStats.length;
    if (size > 0) {
      active.push(`${size} stat type(s) hidden`);
    }
  }
  
  const excludedPlayers = filters.excludedPlayers;
  if (excludedPlayers) {
    const size = excludedPlayers instanceof Set ? excludedPlayers.size : excludedPlayers.length;
    if (size > 0) {
      active.push(`${size} player(s) hidden`);
    }
  }
  
  if (filters.sportsbook) {
    active.push(`Book: ${filters.sportsbook}`);
  }
  
  if (filters.side) {
    active.push(`Side: ${filters.side}`);
  }
  
  if (filters.searchQuery && filters.searchQuery.trim()) {
    active.push(`Search: "${filters.searchQuery}"`);
  }
  
  return active;
}

/**
 * Count the number of active filters.
 */
export function countActiveFilters(filters: PropFilterState): number {
  return getFilterSummary(filters).length;
}

// =============================================================================
// Stats Filter State (for StatsDashboard)
// =============================================================================

export interface StatsFilterState {
  marketType?: string | null;
  side?: 'over' | 'under' | null;
  minGames?: number;
  dateRange?: '7d' | '30d' | 'all';
}

export const DEFAULT_STATS_FILTERS: StatsFilterState = {
  marketType: null,
  side: null,
  minGames: 0,
  dateRange: '30d',
};

export function hasActiveStatsFilters(
  filters: StatsFilterState,
  defaults: StatsFilterState = DEFAULT_STATS_FILTERS
): boolean {
  if (filters.marketType && filters.marketType !== defaults.marketType) {
    return true;
  }
  if (filters.side && filters.side !== defaults.side) {
    return true;
  }
  if (filters.minGames !== undefined && filters.minGames !== defaults.minGames) {
    return true;
  }
  if (filters.dateRange && filters.dateRange !== defaults.dateRange) {
    return true;
  }
  return false;
}

// =============================================================================
// Parlay Filter State
// =============================================================================

export interface ParlayFilterState {
  minEv?: number;
  minConfidence?: number;
  maxLegs?: number;
  sameGame?: boolean;
}

export const DEFAULT_PARLAY_FILTERS: ParlayFilterState = {
  minEv: 0,
  minConfidence: 0.55,
  maxLegs: 10,
  sameGame: false,
};

export function hasActiveParlayFilters(
  filters: ParlayFilterState,
  defaults: ParlayFilterState = DEFAULT_PARLAY_FILTERS
): boolean {
  if (filters.minEv !== undefined && filters.minEv !== defaults.minEv) {
    return true;
  }
  if (filters.minConfidence !== undefined && filters.minConfidence !== defaults.minConfidence) {
    return true;
  }
  if (filters.maxLegs !== undefined && filters.maxLegs !== defaults.maxLegs) {
    return true;
  }
  if (filters.sameGame !== undefined && filters.sameGame !== defaults.sameGame) {
    return true;
  }
  return false;
}

// =============================================================================
// Generic Filter Comparison
// =============================================================================

/**
 * Deep compare two filter objects to check if they differ.
 */
export function filtersChanged<T extends Record<string, unknown>>(
  current: T,
  defaults: T
): boolean {
  for (const key of Object.keys(defaults)) {
    const currentVal = current[key];
    const defaultVal = defaults[key];
    
    // Handle Set comparison
    if (currentVal instanceof Set && defaultVal instanceof Set) {
      if (currentVal.size !== defaultVal.size) return true;
      for (const item of currentVal) {
        if (!defaultVal.has(item)) return true;
      }
      continue;
    }
    
    // Handle array comparison
    if (Array.isArray(currentVal) && Array.isArray(defaultVal)) {
      if (currentVal.length !== defaultVal.length) return true;
      if (!currentVal.every((v, i) => v === defaultVal[i])) return true;
      continue;
    }
    
    // Simple comparison
    if (currentVal !== defaultVal) return true;
  }
  
  return false;
}
