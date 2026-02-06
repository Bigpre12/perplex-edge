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
 * Sport IDs follow a logical grouping pattern:
 * - 30s: Basketball (NBA=30, NCAAB=32, WNBA=34)
 * - 31: NFL, 40: MLB, 41: NCAAF
 * - 42-43: Tennis (ATP, WTA)
 * - 53: NHL
 * - 60: Golf (PGA)
 * - 70s: Soccer (EPL=70, UCL=71, MLS=72)
 * - 80: UFC/MMA
 */
export const SPORT_CONFIG: Record<number, SportConfig> = {
  // Basketball
  30: { name: 'NBA', icon: '🏀', color: 'bg-orange-900/30 text-orange-400', borderColor: 'border-orange-700' },
  32: { name: 'NCAAB', icon: '🏀', color: 'bg-blue-900/30 text-blue-400', borderColor: 'border-blue-700' },
  34: { name: 'WNBA', icon: '🏀', color: 'bg-orange-900/30 text-orange-300', borderColor: 'border-orange-600' },
  // Football
  31: { name: 'NFL', icon: '🏈', color: 'bg-green-900/30 text-green-400', borderColor: 'border-green-700' },
  41: { name: 'NCAAF', icon: '🏈', color: 'bg-purple-900/30 text-purple-400', borderColor: 'border-purple-700' },
  // Baseball
  40: { name: 'MLB', icon: '⚾', color: 'bg-red-900/30 text-red-400', borderColor: 'border-red-700' },
  // Hockey
  53: { name: 'NHL', icon: '🏒', color: 'bg-cyan-900/30 text-cyan-400', borderColor: 'border-cyan-700' },
  // Tennis
  42: { name: 'ATP', icon: '🎾', color: 'bg-yellow-900/30 text-yellow-400', borderColor: 'border-yellow-700' },
  43: { name: 'WTA', icon: '🎾', color: 'bg-pink-900/30 text-pink-400', borderColor: 'border-pink-700' },
  // Golf
  60: { name: 'PGA', icon: '⛳', color: 'bg-green-900/30 text-green-300', borderColor: 'border-green-600' },
  // Soccer
  70: { name: 'EPL', icon: '⚽', color: 'bg-indigo-900/30 text-indigo-400', borderColor: 'border-indigo-700' },
  71: { name: 'UCL', icon: '⚽', color: 'bg-blue-900/30 text-blue-300', borderColor: 'border-blue-600' },
  72: { name: 'MLS', icon: '⚽', color: 'bg-red-900/30 text-red-300', borderColor: 'border-red-600' },
  73: { name: 'UEL', icon: '⚽', color: 'bg-orange-900/30 text-orange-400', borderColor: 'border-orange-700' },
  74: { name: 'UECL', icon: '⚽', color: 'bg-green-900/30 text-green-400', borderColor: 'border-green-700' },
  // MMA/UFC
  80: { name: 'UFC', icon: '🥊', color: 'bg-red-900/30 text-red-500', borderColor: 'border-red-800' },
};

/**
 * Get all sport IDs.
 */
export const ALL_SPORT_IDS = Object.keys(SPORT_CONFIG).map(Number);

/**
 * Sport key to display name mapping (for API responses that use string keys).
 */
export const SPORT_KEY_TO_NAME: Record<string, string> = {
  // Basketball
  basketball_nba: 'NBA',
  basketball_ncaab: 'NCAAB',
  basketball_wnba: 'WNBA',
  // Football
  americanfootball_nfl: 'NFL',
  americanfootball_ncaaf: 'NCAAF',
  // Baseball
  baseball_mlb: 'MLB',
  // Hockey
  icehockey_nhl: 'NHL',
  // Tennis
  tennis_atp: 'ATP',
  tennis_wta: 'WTA',
  // Golf
  golf_pga_tour: 'PGA',
  // Soccer
  soccer_epl: 'EPL',
  soccer_uefa_champs_league: 'UCL',
  soccer_uefa_europa: 'UEL',
  soccer_uefa_conference: 'UECL',
  soccer_usa_mls: 'MLS',
  // MMA
  mma_mixed_martial_arts: 'UFC',
};

/**
 * Sport type groupings (for stat type filtering).
 */
export type SportType = 'basketball' | 'football' | 'baseball' | 'hockey' | 'tennis' | 'golf' | 'soccer' | 'mma';

export const SPORT_ID_TO_TYPE: Record<number, SportType> = {
  30: 'basketball',
  32: 'basketball',
  34: 'basketball',
  31: 'football',
  41: 'football',
  40: 'baseball',
  53: 'hockey',
  42: 'tennis',
  43: 'tennis',
  60: 'golf',
  70: 'soccer',
  71: 'soccer',
  72: 'soccer',
  73: 'soccer',
  74: 'soccer',
  80: 'mma',
};

/**
 * Enabled sports for the multi-sport slate (ordered by priority).
 */
export const ENABLED_SPORTS = [
  { id: 30, key: 'NBA', type: 'basketball' as SportType },
  { id: 32, key: 'NCAAB', type: 'basketball' as SportType },
  { id: 31, key: 'NFL', type: 'football' as SportType },
  { id: 41, key: 'NCAAF', type: 'football' as SportType },
  { id: 40, key: 'MLB', type: 'baseball' as SportType },
  { id: 53, key: 'NHL', type: 'hockey' as SportType },
  { id: 42, key: 'ATP', type: 'tennis' as SportType },
  { id: 43, key: 'WTA', type: 'tennis' as SportType },
  { id: 34, key: 'WNBA', type: 'basketball' as SportType },
  { id: 60, key: 'PGA', type: 'golf' as SportType },
  { id: 70, key: 'EPL', type: 'soccer' as SportType },
  { id: 71, key: 'UCL', type: 'soccer' as SportType },
  { id: 72, key: 'MLS', type: 'soccer' as SportType },
  { id: 73, key: 'UEL', type: 'soccer' as SportType },
  { id: 74, key: 'UECL', type: 'soccer' as SportType },
  { id: 80, key: 'UFC', type: 'mma' as SportType },
];

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
