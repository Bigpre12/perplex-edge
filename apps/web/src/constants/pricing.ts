// src/constants/pricing.ts

export const PRICING = {
    FREE: {
        label: "FREE",
        monthly: 0,
        annual: 0,
        description: "Basic access",
        features: [
            "Live player props (NBA, NFL, MLB, NHL, NCAAB)",
            "Best available odds across books",
            "Basic prop search & filtering",
            "Today's slate overview",
            "Live game scores",
        ],
    },
    PRO: {
        label: "PRO",
        monthly: 19.99,
        annual: 16.99, // ~200/yr / 12
        description: "Full props",
        features: [
            "Everything in Free",
            "EV+ badges on every prop",
            "Hit rate tracker",
            "Parlay builder with EV scoring",
            "Matchup & situational filters",
            "Real-time Discord alerts",
            "Live WebSocket odds feed",
            "Bankroll management tracker",
            "All sports unlocked (WNBA, MMA, Tennis, Boxing, Soccer)",
            "Multi-book best line comparison",
        ],
    },
    ELITE: {
        label: "ELITE",
        monthly: 39.99,
        annual: 33.99, // ~400/yr / 12
        description: "Everything",
        features: [
            "Everything in Pro",
            "Arbitrage finder",
            "Sharp money & steam alerts",
            "Whale detector (large bet signals)",
            "CLV tracker",
            "Line movement history & reverse line alerts",
            "Middling calculator",
            "Sharp vs square book comparison",
            "Lucrix Oracle AI (live slate awareness)",
            "Priority support",
        ],
    },
} as const;

export type Tier = keyof typeof PRICING;
