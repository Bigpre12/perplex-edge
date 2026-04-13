import { Tier } from "./tier";

export const FEATURE_MIN_TIER = {
    // Advanced Intelligence
    whaleIntel: 'elite',
    neuralBrain: 'elite',
    steamAlerts: 'pro',
    
    // Betting Tools
    evSignals: 'pro',
    arbitrage: 'pro',
    clvAnalytics: 'pro',
    
    // Limits
    extendedParlay: 'pro',
    unlimitedPortfolio: 'elite',
    
    // Core
    basicDashboard: 'free',
} as const;

export type FeatureKey = keyof typeof FEATURE_MIN_TIER;

/**
 * Gets the minimum tier required for a specific feature.
 */
export function getRequiredTier(feature: FeatureKey): Tier {
    return FEATURE_MIN_TIER[feature];
}
