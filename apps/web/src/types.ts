/**
 * Shared TypeScript types for the Lucrix frontend.
 * Use these instead of `any` in hooks and components.
 */

/** A player prop pick from the API */
export interface LiveProp {
    id: string | number;
    player_name: string;
    position?: string;
    team?: string;
    stat_type: string;
    line: number;
    line_value?: number;
    side: 'over' | 'under' | 'moneyline';
    odds: number;
    sportsbook?: string;
    sport_key?: string;
    sport_id?: number;
    ev_percentage?: number;
    display_edge?: number;
    edge?: number;
    confidence_score?: number;
    model_probability?: number;
    implied_probability?: number;
    kelly_units?: number;
    sharp_money_indicator?: boolean;
    sharp_money?: boolean;
    steam_score?: number;
    status?: string;
    created_at?: string;
    updated_at?: string;
    /** Nested player object (from some endpoints) */
    player?: {
        name: string;
        position: string;
    };
    /** Nested market object (from some endpoints) */
    market?: {
        stat_type: string;
    };
    /** Game context */
    game?: {
        home: string;
        away: string;
    };
    matchup?: {
        opponent: string;
    };
}

/** Brain decision from /api/brain/decisions */
export interface BrainDecision {
    action: string;
    reasoning: string;
    details: {
        player_name: string;
        stat_type: string;
        line_value: number;
        side: string;
        edge: number;
        confidence: number;
    };
    confidence_tier?: 'high' | 'mid' | 'low';
}

/** System health from /api/brain/health */
export interface SystemHealth {
    status: string;
    ai_evaluation: {
        action: string;
        target: string;
        reason: string;
        is_critical: boolean;
    };
    system_metrics_evaluated: {
        cpu_usage: number;
        error_rate: number;
    };
}

/** Market intelligence item */
export interface MarketIntelItem {
    title: string;
    content: string;
    type: 'news' | 'injury' | 'sharp';
    timestamp: string;
}

/** Trend item from /api/trends/hit-rates */
export interface TrendItem {
    id: string | number;
    player_name: string;
    stat_type: string;
    hit_rate: number;
    games_played: number;
    avg_value?: number;
    line?: number;
    sport_key?: string;
}

/** Parlay leg */
export interface ParlayLeg {
    id: string;
    player_name: string;
    stat_type: string;
    line: number;
    side: string;
    odds: number;
    team?: string;
    ev?: number;
}
