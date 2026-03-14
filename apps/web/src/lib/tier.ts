export const TIER_LEVELS = {
    free: 0,
    pro: 1,
    elite: 2,
} as const;

export type Tier = keyof typeof TIER_LEVELS;

/**
 * checkTierAccess - Checks if a user's tier meets the minimum requirements.
 */
export function checkTierAccess(
    userTier: Tier = 'free',
    required: Tier
): boolean {
    return (TIER_LEVELS[userTier] ?? 0) >= TIER_LEVELS[required];
}

// Tier-specific functional limits
export function getSimCount(tier: Tier): number {
    return tier === 'elite' ? 10_000 : 100;
}

export function getRefreshInterval(tier: Tier): number {
    return tier === 'elite' ? 30_000 : tier === 'pro' ? 60_000 : 300_000;
}

export function getMaxParlayLegs(tier: Tier): number {
    return tier === 'free' ? 2 : 12;
}

export function getOracleLimit(tier: Tier): number {
    return tier === 'elite' ? Infinity : tier === 'pro' ? 10 : 0;
}

export function getBookCount(tier: Tier): number {
    return tier === 'free' ? 2 : 10;
}

export function getSportCount(tier: Tier): number {
    return tier === 'free' ? 2 : 14;
}

export function getPropLimit(tier: Tier): number {
    return tier === 'free' ? 5 : 50;
}
