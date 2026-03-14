export const TIERS = {
    free: {
        props: 5,           // max props visible
        sports: ["basketball_nba"],  // 1 sport only
        oracle: 3,          // 3 Oracle messages/day

        // Essential Features
        picks: false,
        sharpMoney: false,
        lineMovement: false,
        edges: false,
        parlay: false,
        export: false,
        discord: false,

        // Granular Flags (aligned with permissions.ts)
        view_ev_badges: false,
        view_hit_rates: false,
        view_best_odds: false,
        bankroll_tracker: false,
        arb_finder: false,
        steam_alerts: false,
        clv_tracker: false,
        whale_detector: false,
        middling_calc: false,
        sharp_book_compare: false,
        kalshi_elite: false,
    },
    pro: {
        props: 50,
        sports: ["basketball_nba", "americanfootball_nfl", "baseball_mlb", "icehockey_nhl", "mma_mixed_martial_arts"],
        oracle: 20,

        picks: true,
        sharpMoney: false,
        lineMovement: true,
        edges: true,
        parlay: true,
        export: true,
        discord: true,

        view_ev_badges: true,
        view_hit_rates: true,
        view_best_odds: true,
        bankroll_tracker: true,
        arb_finder: true,
        steam_alerts: false,
        clv_tracker: false,
        whale_detector: false,
        middling_calc: true,
        sharp_book_compare: true,
        kalshi_elite: false,
    },
    elite: {
        props: 999,
        sports: ["all"],
        oracle: 999,

        picks: true,
        sharpMoney: true,
        lineMovement: true,
        edges: true,
        parlay: true,
        export: true,
        discord: true,

        view_ev_badges: true,
        view_hit_rates: true,
        view_best_odds: true,
        bankroll_tracker: true,
        arb_finder: true,
        steam_alerts: true,
        clv_tracker: true,
        whale_detector: true,
        middling_calc: true,
        sharp_book_compare: true,
        kalshi_elite: true,
    },
    owner: {
        props: 999,
        sports: ["all"],
        oracle: 999,

        picks: true,
        sharpMoney: true,
        lineMovement: true,
        edges: true,
        parlay: true,
        export: true,
        discord: true,

        view_ev_badges: true,
        view_hit_rates: true,
        view_best_odds: true,
        bankroll_tracker: true,
        arb_finder: true,
        steam_alerts: true,
        clv_tracker: true,
        whale_detector: true,
        middling_calc: true,
        sharp_book_compare: true,
        kalshi_elite: true,
    },
};

export type Tier = keyof typeof TIERS;
export const getTierConfig = (tier: Tier | string) => {
    const t = (tier?.toLowerCase() || 'free') as Tier;
    return TIERS[t] ?? TIERS.free;
};
