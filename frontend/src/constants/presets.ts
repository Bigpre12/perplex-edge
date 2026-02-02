/**
 * Quick Start Presets - Pre-tuned filter configurations per sport
 * 
 * These presets help new users see picks instantly without touching sliders.
 * Each preset is optimized for different betting styles and risk tolerance.
 */

// =============================================================================
// Sport-Specific Quick Start Presets
// =============================================================================

export interface QuickStartPreset {
  id: string;
  label: string;
  description: string;
  icon: string;
  // Filter values
  minConfidence: number;
  minEv: number;
  riskLevels: string[];
  // Optional sport-specific settings
  excludeStats?: string[];
  hideCoinFlips?: boolean;
  hideStaleLines?: boolean;
}

// Default presets that work across all sports
export const QUICK_START_PRESETS: QuickStartPreset[] = [
  {
    id: 'conservative',
    label: 'Safe Bets',
    description: 'High confidence picks with solid edge. Lower volume, higher win rate.',
    icon: '🛡️',
    minConfidence: 0.60,
    minEv: 0.05,
    riskLevels: ['CONFIDENT', 'STRONG'],
    hideCoinFlips: true,
    hideStaleLines: true,
  },
  {
    id: 'balanced',
    label: 'Balanced',
    description: 'Good mix of confidence and EV. Our recommended starting point.',
    icon: '⚖️',
    minConfidence: 0.55,
    minEv: 0.03,
    riskLevels: ['STANDARD', 'CONFIDENT', 'STRONG'],
    hideCoinFlips: true,
    hideStaleLines: true,
  },
  {
    id: 'value',
    label: 'Value Hunter',
    description: 'Focus on high EV opportunities. More variance, higher upside.',
    icon: '💎',
    minConfidence: 0.52,
    minEv: 0.05,
    riskLevels: ['STANDARD', 'CONFIDENT', 'STRONG', 'MAX'],
    hideCoinFlips: true,
    hideStaleLines: false,
  },
  {
    id: 'all',
    label: 'Show All',
    description: 'See everything - no filters applied.',
    icon: '👁️',
    minConfidence: 0,
    minEv: 0,
    riskLevels: ['SMALL', 'STANDARD', 'CONFIDENT', 'STRONG', 'MAX'],
    hideCoinFlips: false,
    hideStaleLines: false,
  },
];

// =============================================================================
// Default Filter Values (used for Reset functionality)
// =============================================================================

export const DEFAULT_PLAYER_PROPS_FILTERS = {
  statType: '',
  minConfidence: 0.55,
  minEv: 0.03,
  riskLevels: ['STANDARD', 'CONFIDENT', 'STRONG'],
  excludedStatTypes: new Set(['player_steals', 'player_blocks']),
  excludedPlayers: new Set<string>(),
  onlyGreenTier: false,
  hideCoinFlips: true,
  hideStaleLines: true,
};

export const DEFAULT_100PCT_FILTERS = {
  window: 'last_5',
  limit: 50,
  minHitRate: 0.70,
};

export const DEFAULT_PARLAY_FILTERS = {
  legCount: 3,
  minGrade: 'B',
  include100Pct: false,
  maxResults: 5,
  blockCorrelated: true,
  maxCorrelationRisk: 'MEDIUM',
};

// =============================================================================
// EV and Stat Explainers (micro-copy)
// =============================================================================

export const METRIC_EXPLAINERS = {
  ev: {
    short: 'Expected profit per bet',
    long: 'EV (Expected Value) is your long-term edge per bet. +5% EV means you expect to profit $5 for every $100 wagered over time.',
    example: '+5% EV = $5 profit per $100 bet (long-term)',
  },
  hitRate: {
    short: 'How often this line has hit historically',
    long: 'Hit Rate shows how often this player has gone over/under this line in recent games. 100% means they\'ve hit every time.',
    example: '80% L5 = Hit 4 of last 5 games',
  },
  confidence: {
    short: 'Model\'s certainty in the prediction',
    long: 'Confidence is the model\'s probability estimate. Higher confidence means the model is more certain about the outcome.',
    example: '65% = Model predicts 65% chance of hitting',
  },
  kelly: {
    short: 'Optimal bet sizing based on edge',
    long: 'Kelly Criterion calculates the mathematically optimal bet size based on your edge and bankroll. Higher Kelly = bigger suggested stake.',
    example: 'CONFIDENT = 1-2 units suggested',
  },
  clv: {
    short: 'Closing Line Value - did you beat the close?',
    long: 'CLV measures if you got a better line than the final closing line. Positive CLV indicates you captured value before the market moved.',
    example: '+5 cents CLV = Beat the closing line',
  },
};

// =============================================================================
// Feature Flags (for Lite vs Pro versioning)
// =============================================================================

export const FEATURE_FLAGS = {
  // Core features
  ENABLE_PLAYER_PROPS: true,
  ENABLE_GAME_LINES: true,
  ENABLE_100PCT_HITS: true,
  ENABLE_PARLAY_BUILDER: true,
  ENABLE_MY_BETS: true,
  
  // Premium features
  ENABLE_LIVE_EV: true,
  ENABLE_ANALYTICS: true,
  ENABLE_BACKTEST: true,
  ENABLE_ALT_LINES: true,
  ENABLE_WATCHLISTS: true,
  
  // Sports (can be toggled for different license tiers)
  ENABLE_NBA: true,
  ENABLE_NFL: true,
  ENABLE_MLB: true,
  ENABLE_NHL: true,
  ENABLE_NCAAB: true,
  ENABLE_NCAAF: true,
  ENABLE_ATP: true,
  ENABLE_WTA: true,
  
  // Pro-only features
  ENABLE_EXPORT: true,
  ENABLE_MODEL_PERFORMANCE: true,
  ENABLE_ADVANCED_FILTERS: true,
};

// Helper to check if a feature is enabled
export function isFeatureEnabled(flag: keyof typeof FEATURE_FLAGS): boolean {
  return FEATURE_FLAGS[flag] ?? false;
}
