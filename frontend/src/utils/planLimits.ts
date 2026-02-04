/**
 * Plan limits utilities for frontend feature gating.
 * 
 * Mirrors backend/app/core/plan_limits.py for consistent enforcement.
 */

import type { UserPlan } from '../context/AuthContext';

// =============================================================================
// Sport IDs (matching backend)
// =============================================================================

export const SPORT_NBA = 30;
export const SPORT_NFL = 31;
export const SPORT_NCAAB = 32;
export const SPORT_WNBA = 34;
export const SPORT_MLB = 40;
export const SPORT_NCAAF = 41;
export const SPORT_ATP = 42;
export const SPORT_WTA = 43;
export const SPORT_NHL = 53;
export const SPORT_PGA = 60;
export const SPORT_EPL = 70;
export const SPORT_UCL = 71;
export const SPORT_MLS = 72;
export const SPORT_UEL = 73;
export const SPORT_UECL = 74;
export const SPORT_UFC = 80;

// Sports available on free tier
export const FREE_SPORTS = [SPORT_NBA, SPORT_NFL];

// All available sports
export const ALL_SPORTS = [
  SPORT_NBA, SPORT_NFL, SPORT_NCAAB, SPORT_WNBA, SPORT_MLB, SPORT_NCAAF,
  SPORT_ATP, SPORT_WTA, SPORT_NHL, SPORT_PGA,
  SPORT_EPL, SPORT_UCL, SPORT_MLS, SPORT_UEL, SPORT_UECL,
  SPORT_UFC,
];

// =============================================================================
// Feature Types
// =============================================================================

export type PlanFeature =
  | 'live_ev'
  | 'alt_lines'
  | 'watchlists'
  | 'backtest'
  | 'analytics'
  | 'model_performance'
  | 'my_edge'
  | 'stats_filters'
  | 'export_data'
  | 'unlimited_props'
  | 'unlimited_parlay_legs';

// =============================================================================
// Plan Limits Configuration
// =============================================================================

interface PlanLimits {
  allowedSports: number[] | 'all';
  dailyPropsLimit: number | null;  // null = unlimited
  parlayMaxLegs: number | null;    // null = unlimited
  features: Record<PlanFeature, boolean>;
}

const PLAN_LIMITS: Record<UserPlan, PlanLimits> = {
  free: {
    allowedSports: FREE_SPORTS,
    dailyPropsLimit: 10,
    parlayMaxLegs: 3,
    features: {
      live_ev: false,
      alt_lines: false,
      watchlists: false,
      backtest: false,
      analytics: false,
      model_performance: false,
      my_edge: false,
      stats_filters: false,
      export_data: false,
      unlimited_props: false,
      unlimited_parlay_legs: false,
    },
  },
  trial: {
    allowedSports: 'all',
    dailyPropsLimit: null,
    parlayMaxLegs: null,
    features: {
      live_ev: true,
      alt_lines: true,
      watchlists: true,
      backtest: true,
      analytics: true,
      model_performance: true,
      my_edge: true,
      stats_filters: true,
      export_data: true,
      unlimited_props: true,
      unlimited_parlay_legs: true,
    },
  },
  pro: {
    allowedSports: 'all',
    dailyPropsLimit: null,
    parlayMaxLegs: null,
    features: {
      live_ev: true,
      alt_lines: true,
      watchlists: true,
      backtest: true,
      analytics: true,
      model_performance: true,
      my_edge: true,
      stats_filters: true,
      export_data: true,
      unlimited_props: true,
      unlimited_parlay_legs: true,
    },
  },
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get plan limits for a user plan.
 */
export function getPlanLimits(plan: UserPlan): PlanLimits {
  return PLAN_LIMITS[plan] || PLAN_LIMITS.free;
}

/**
 * Get list of sport IDs the user can access.
 */
export function getAllowedSports(plan: UserPlan): number[] {
  const limits = getPlanLimits(plan);
  return limits.allowedSports === 'all' ? ALL_SPORTS : limits.allowedSports;
}

/**
 * Check if user can access a specific sport.
 */
export function canAccessSport(plan: UserPlan, sportId: number): boolean {
  const allowed = getAllowedSports(plan);
  return allowed.includes(sportId);
}

/**
 * Check if user can use a specific feature.
 */
export function canUseFeature(plan: UserPlan, feature: PlanFeature): boolean {
  const limits = getPlanLimits(plan);
  return limits.features[feature] || false;
}

/**
 * Get daily props limit for a plan.
 * Returns null for unlimited.
 */
export function getDailyPropsLimit(plan: UserPlan): number | null {
  const limits = getPlanLimits(plan);
  return limits.dailyPropsLimit;
}

/**
 * Get max parlay legs for a plan.
 * Returns null for unlimited.
 */
export function getMaxParlayLegs(plan: UserPlan): number | null {
  const limits = getPlanLimits(plan);
  return limits.parlayMaxLegs;
}

/**
 * Check if a user has reached their daily props limit.
 */
export function hasReachedPropsLimit(plan: UserPlan, propsViewed: number): boolean {
  const limit = getDailyPropsLimit(plan);
  if (limit === null) return false;
  return propsViewed >= limit;
}

/**
 * Check if a parlay exceeds the user's leg limit.
 */
export function exceedsParlayLimit(plan: UserPlan, legs: number): boolean {
  const limit = getMaxParlayLegs(plan);
  if (limit === null) return false;
  return legs > limit;
}

// =============================================================================
// Sport Name Helpers
// =============================================================================

export const SPORT_NAMES: Record<number, string> = {
  [SPORT_NBA]: 'NBA',
  [SPORT_NFL]: 'NFL',
  [SPORT_NCAAB]: 'NCAAB',
  [SPORT_WNBA]: 'WNBA',
  [SPORT_MLB]: 'MLB',
  [SPORT_NCAAF]: 'NCAAF',
  [SPORT_ATP]: 'ATP Tennis',
  [SPORT_WTA]: 'WTA Tennis',
  [SPORT_NHL]: 'NHL',
  [SPORT_PGA]: 'PGA Tour',
  [SPORT_EPL]: 'EPL',
  [SPORT_UCL]: 'Champions League',
  [SPORT_MLS]: 'MLS',
  [SPORT_UEL]: 'Europa League',
  [SPORT_UECL]: 'Conference League',
  [SPORT_UFC]: 'UFC',
};

export function getSportName(sportId: number): string {
  return SPORT_NAMES[sportId] || `Sport ${sportId}`;
}

/**
 * Get locked sports (not available on free plan).
 */
export function getLockedSports(): number[] {
  return ALL_SPORTS.filter(id => !FREE_SPORTS.includes(id));
}

/**
 * Check if a sport is locked for free users.
 */
export function isSportLocked(sportId: number): boolean {
  return !FREE_SPORTS.includes(sportId);
}
