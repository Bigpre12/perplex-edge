/**
 * Centralized sport configuration constants.
 * 
 * Used across components that need sport metadata (name, icon, colors).
 */

export interface SportConfig {
  name: string;
  icon: string;
  color: string;
  borderColor?: string;
}

/**
 * Sport ID to configuration mapping.
 * 
 * Sport IDs match the database:
 * - 30: NBA
 * - 31: NFL
 * - 32: NCAAB
 * - 40: MLB
 * - 41: NCAAF
 * - 42: Tennis ATP
 * - 43: Tennis WTA
 */
export const SPORT_CONFIG: Record<number, SportConfig> = {
  30: { name: 'NBA', icon: '🏀', color: 'bg-orange-900/30 text-orange-400', borderColor: 'border-orange-700' },
  31: { name: 'NFL', icon: '🏈', color: 'bg-green-900/30 text-green-400', borderColor: 'border-green-700' },
  32: { name: 'NCAAB', icon: '🏀', color: 'bg-blue-900/30 text-blue-400', borderColor: 'border-blue-700' },
  40: { name: 'MLB', icon: '⚾', color: 'bg-red-900/30 text-red-400', borderColor: 'border-red-700' },
  41: { name: 'NCAAF', icon: '🏈', color: 'bg-purple-900/30 text-purple-400', borderColor: 'border-purple-700' },
  42: { name: 'ATP', icon: '🎾', color: 'bg-yellow-900/30 text-yellow-400', borderColor: 'border-yellow-700' },
  43: { name: 'WTA', icon: '🎾', color: 'bg-pink-900/30 text-pink-400', borderColor: 'border-pink-700' },
};

/**
 * Get all sport IDs.
 */
export const ALL_SPORT_IDS = Object.keys(SPORT_CONFIG).map(Number);

/**
 * Sport key to display name mapping (for API responses that use string keys).
 */
export const SPORT_KEY_TO_NAME: Record<string, string> = {
  basketball_nba: 'NBA',
  basketball_ncaab: 'NCAAB',
  americanfootball_nfl: 'NFL',
  americanfootball_ncaaf: 'NCAAF',
  baseball_mlb: 'MLB',
  icehockey_nhl: 'NHL',
  tennis_atp: 'ATP',
  tennis_wta: 'WTA',
};

/**
 * Get sport config by ID with fallback.
 */
export function getSportConfig(sportId: number): SportConfig {
  return SPORT_CONFIG[sportId] || {
    name: `Sport ${sportId}`,
    icon: '🏆',
    color: 'bg-gray-900/30 text-gray-400',
    borderColor: 'border-gray-700',
  };
}

/**
 * Get sport name by key with fallback.
 */
export function getSportNameByKey(key: string): string {
  return SPORT_KEY_TO_NAME[key] || key.toUpperCase();
}
