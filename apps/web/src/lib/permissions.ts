import { TIERS, Tier as TierConfig } from "./tiers";

// Legacy Tier mapping for backward compatibility if components use "pro" or "elite" strings
export type Tier = "free" | "pro" | "elite" | "premium" | "owner";

const TIER_MAPPING: Record<Tier, TierConfig> = {
    free: "free",
    pro: "pro",
    elite: "elite",
    premium: "pro", // backward compatibility
    owner: "owner"
};

/**
 * @deprecated Use useGate() hook or lib/tiers directly.
 * This file is now a compatibility layer over lib/tiers.ts.
 */
export const PERMISSIONS = {
    // Props
    view_props: "free",
    view_all_sports: "pro",
    view_ev_badges: "pro",
    view_hit_rates: "pro",
    view_best_odds: "pro",

    // Tools
    parlay_builder: "pro",
    bankroll_tracker: "pro",
    matchup_filters: "pro",
    discord_alerts: "pro",
    live_feed: "pro",

    // Sharp/Elite
    arb_finder: "elite",
    steam_alerts: "elite",
    whale_detector: "elite",
    clv_tracker: "elite",
    line_movement: "pro",
    middling_calc: "pro",
    sharp_book_compare: "elite",
    oracle_ai: "pro",
} as const;

export type FeatureKey = keyof typeof PERMISSIONS;

export function canAccess(userTier: Tier, feature: FeatureKey): boolean {
    const isDev = typeof window !== 'undefined' && 
                 (window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1' || 
                  window.location.hostname.startsWith('192.168.') || 
                  window.location.hostname.startsWith('172.'));
    if (isDev) return true;

    const targetTier = TIER_MAPPING[userTier] || "free";
    const config = TIERS[targetTier];

    // Attempt to map feature to tiers keys
    const tierKeyMap: Record<string, keyof typeof config> = {
        view_ev_badges: "edges",
        parlay_builder: "parlay",
        whale_detector: "sharpMoney",
        discord_alerts: "discord",
        line_movement: "lineMovement"
    };

    const key = tierKeyMap[feature] || (feature as any);
    return !!(config as any)[key];
}

export function getRequiredTier(feature: FeatureKey): Tier {
    return PERMISSIONS[feature] as Tier;
}
