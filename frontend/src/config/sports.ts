/**
 * Shared sport and stat-type configuration.
 *
 * This module provides type-safe sport keys, stat types, and the mapping
 * of which stat types are valid for each sport.
 *
 * Keep this file in sync with backend/app/config/sports.py
 */

// =============================================================================
// Sport Key Type
// =============================================================================

/**
 * Union type of all supported sport keys.
 * Values match The Odds API sport key format.
 */
export type SportKey =
  // Basketball
  | 'basketball_nba'
  | 'basketball_ncaab'
  | 'basketball_wnba'
  // Football
  | 'americanfootball_nfl'
  | 'americanfootball_ncaaf'
  // Baseball
  | 'baseball_mlb'
  // Hockey
  | 'icehockey_nhl'
  // Tennis
  | 'tennis_atp'
  | 'tennis_wta'
  // Golf
  | 'golf_pga_tour'
  // Soccer
  | 'soccer_epl'
  | 'soccer_uefa_champs_league'
  | 'soccer_usa_mls'
  // MMA
  | 'mma_mixed_martial_arts';

// =============================================================================
// Stat Type Union
// =============================================================================

/**
 * Union type of all supported stat types across all sports.
 * Values are the internal stat type identifiers used in the database.
 */
export type StatType =
  // Basketball Stats
  | 'PTS'
  | 'REB'
  | 'AST'
  | '3PM'
  | 'PRA'
  | 'PR'
  | 'PA'
  | 'RA'
  | 'STL'
  | 'BLK'
  | 'TO'
  | 'DD'
  | 'TD'
  // Football Stats
  | 'PASS_YDS'
  | 'PASS_TDS'
  | 'PASS_ATT'
  | 'PASS_COMP'
  | 'INT'
  | 'RUSH_YDS'
  | 'RUSH_ATT'
  | 'RUSH_TDS'
  | 'REC_YDS'
  | 'REC'
  | 'REC_TDS'
  | 'RUSH_REC_YDS'
  | 'ANYTIME_TD'
  // Baseball Stats
  | 'H'
  | 'R'
  | 'RBI'
  | 'TB'
  | 'HRR'
  | 'K'
  | 'OUTS'
  | 'HR'
  // Hockey Stats
  | 'GOALS'
  | 'AST_H'
  | 'PTS_H'
  | 'SOG'
  | 'BLK_SHOTS'
  | 'SAVES'
  | 'PPP'
  | 'PIM'
  // Tennis Stats
  | 'ACES'
  | 'DF'
  | 'GAMES'
  | 'SETS'
  | 'TOTAL_GAMES'
  // Golf Stats
  | 'FINISH_POS'
  | 'MAKE_CUT'
  | 'TOP_5'
  | 'TOP_10'
  | 'TOP_20'
  | 'FRL'
  | 'MATCHUP'
  | 'BIRDIES'
  | 'BOGEYS'
  | 'STROKES'
  // Soccer Stats
  | 'ANYTIME_GOAL'
  | 'SHOTS'
  | 'SOT'
  | 'FOULS'
  | 'CARDS'
  | 'TACKLES'
  | 'PASSES'
  // MMA/UFC Stats
  | 'WINNER'
  | 'METHOD'
  | 'TOTAL_ROUNDS'
  | 'SIG_STRIKES'
  | 'TAKEDOWNS'
  | 'GOES_DISTANCE'
  | 'FIGHT_TIME';

// =============================================================================
// Stat Type Display Labels
// =============================================================================

/**
 * Human-readable labels for stat types.
 */
export const STAT_TYPE_LABELS: Record<StatType, string> = {
  // Basketball
  PTS: 'Points',
  REB: 'Rebounds',
  AST: 'Assists',
  '3PM': '3-Pointers Made',
  PRA: 'Pts + Reb + Ast',
  PR: 'Pts + Reb',
  PA: 'Pts + Ast',
  RA: 'Reb + Ast',
  STL: 'Steals',
  BLK: 'Blocks',
  TO: 'Turnovers',
  DD: 'Double-Double',
  TD: 'Triple-Double',
  // Football
  PASS_YDS: 'Passing Yards',
  PASS_TDS: 'Passing TDs',
  PASS_ATT: 'Pass Attempts',
  PASS_COMP: 'Completions',
  INT: 'Interceptions',
  RUSH_YDS: 'Rushing Yards',
  RUSH_ATT: 'Rush Attempts',
  RUSH_TDS: 'Rushing TDs',
  REC_YDS: 'Receiving Yards',
  REC: 'Receptions',
  REC_TDS: 'Receiving TDs',
  RUSH_REC_YDS: 'Rush + Rec Yards',
  ANYTIME_TD: 'Anytime TD',
  // Baseball
  H: 'Hits',
  R: 'Runs',
  RBI: 'RBIs',
  TB: 'Total Bases',
  HRR: 'Hits + Runs + RBIs',
  K: 'Strikeouts (Pitcher)',
  OUTS: 'Outs Recorded',
  HR: 'Home Runs',
  // Hockey
  GOALS: 'Goals',
  AST_H: 'Assists',
  PTS_H: 'Points',
  SOG: 'Shots on Goal',
  BLK_SHOTS: 'Blocked Shots',
  SAVES: 'Saves',
  PPP: 'Power Play Points',
  PIM: 'Penalty Minutes',
  // Tennis
  ACES: 'Aces',
  DF: 'Double Faults',
  GAMES: 'Games Won',
  SETS: 'Sets Won',
  TOTAL_GAMES: 'Total Games',
  // Golf
  FINISH_POS: 'Finish Position',
  MAKE_CUT: 'Make Cut',
  TOP_5: 'Top 5',
  TOP_10: 'Top 10',
  TOP_20: 'Top 20',
  FRL: 'First Round Leader',
  MATCHUP: 'Matchup',
  BIRDIES: 'Birdies or Better',
  BOGEYS: 'Bogeys or Worse',
  STROKES: 'Strokes',
  // Soccer
  ANYTIME_GOAL: 'Anytime Goal',
  SHOTS: 'Shots',
  SOT: 'Shots on Target',
  FOULS: 'Fouls',
  CARDS: 'Cards',
  TACKLES: 'Tackles',
  PASSES: 'Passes',
  // MMA
  WINNER: 'Winner',
  METHOD: 'Method of Victory',
  TOTAL_ROUNDS: 'Total Rounds',
  SIG_STRIKES: 'Significant Strikes',
  TAKEDOWNS: 'Takedowns',
  GOES_DISTANCE: 'Goes Distance',
  FIGHT_TIME: 'Fight Time',
};

// =============================================================================
// Sport ID to Key Mapping
// =============================================================================

/**
 * Maps database sport IDs to sport keys.
 */
export const SPORT_ID_TO_KEY: Record<number, SportKey> = {
  // Basketball
  30: 'basketball_nba',
  32: 'basketball_ncaab',
  34: 'basketball_wnba',
  // Football
  31: 'americanfootball_nfl',
  41: 'americanfootball_ncaaf',
  // Baseball
  40: 'baseball_mlb',
  // Hockey
  44: 'icehockey_nhl', // Legacy mapping
  53: 'icehockey_nhl', // Actual database ID
  // Tennis
  42: 'tennis_atp',
  43: 'tennis_wta',
  // Golf
  60: 'golf_pga_tour',
  // Soccer
  70: 'soccer_epl',
  71: 'soccer_uefa_champs_league',
  72: 'soccer_usa_mls',
  // MMA
  80: 'mma_mixed_martial_arts',
};

// =============================================================================
// Stat Types by Sport
// =============================================================================

/**
 * Defines which stat types are valid for each sport.
 */
export const STAT_TYPES_BY_SPORT: Record<SportKey, StatType[]> = {
  // Basketball
  basketball_nba: [
    'PTS',
    'REB',
    'AST',
    '3PM',
    'PRA',
    'PR',
    'PA',
    'RA',
    'STL',
    'BLK',
    'TO',
    'DD',
    'TD',
  ],
  basketball_ncaab: ['PTS', 'REB', 'AST', '3PM', 'PRA'],
  basketball_wnba: ['PTS', 'REB', 'AST', '3PM', 'PRA', 'STL', 'BLK'],

  // Football
  americanfootball_nfl: [
    'PASS_YDS',
    'PASS_TDS',
    'PASS_ATT',
    'PASS_COMP',
    'INT',
    'RUSH_YDS',
    'RUSH_ATT',
    'RUSH_TDS',
    'REC_YDS',
    'REC',
    'REC_TDS',
    'RUSH_REC_YDS',
    'ANYTIME_TD',
  ],
  americanfootball_ncaaf: [
    'PASS_YDS',
    'PASS_TDS',
    'INT',
    'RUSH_YDS',
    'REC_YDS',
    'REC',
    'ANYTIME_TD',
  ],

  // Baseball
  baseball_mlb: ['H', 'R', 'RBI', 'TB', 'HRR', 'K', 'OUTS', 'HR'],

  // Hockey
  icehockey_nhl: ['GOALS', 'AST_H', 'PTS_H', 'SOG', 'BLK_SHOTS', 'SAVES', 'PPP', 'PIM'],

  // Tennis
  tennis_atp: ['ACES', 'DF', 'GAMES', 'SETS', 'TOTAL_GAMES'],
  tennis_wta: ['ACES', 'DF', 'GAMES', 'SETS', 'TOTAL_GAMES'],

  // Golf
  golf_pga_tour: [
    'FINISH_POS',
    'MAKE_CUT',
    'TOP_5',
    'TOP_10',
    'TOP_20',
    'FRL',
    'MATCHUP',
    'BIRDIES',
    'BOGEYS',
    'STROKES',
  ],

  // Soccer
  soccer_epl: ['GOALS', 'ANYTIME_GOAL', 'SHOTS', 'SOT', 'FOULS', 'CARDS', 'TACKLES', 'PASSES'],
  soccer_uefa_champs_league: ['GOALS', 'ANYTIME_GOAL', 'SHOTS', 'SOT'],
  soccer_usa_mls: ['GOALS', 'ANYTIME_GOAL', 'SHOTS', 'SOT'],

  // MMA
  mma_mixed_martial_arts: [
    'WINNER',
    'METHOD',
    'TOTAL_ROUNDS',
    'SIG_STRIKES',
    'TAKEDOWNS',
    'GOES_DISTANCE',
    'FIGHT_TIME',
  ],
};

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get stat types for a sport key.
 */
export function getStatTypesForSportKey(sportKey: SportKey): StatType[] {
  return STAT_TYPES_BY_SPORT[sportKey] ?? [];
}

/**
 * Get stat types for a sport ID.
 */
export function getStatTypesForSportId(sportId: number): StatType[] {
  const sportKey = SPORT_ID_TO_KEY[sportId];
  if (!sportKey) return [];
  return STAT_TYPES_BY_SPORT[sportKey] ?? [];
}

/**
 * Get stat type options (value + label) for a sport ID.
 * Used for dropdown selects.
 */
export function getStatTypeOptionsForSport(sportId: number): { value: StatType; label: string }[] {
  const statTypes = getStatTypesForSportId(sportId);
  return statTypes.map((statType) => ({
    value: statType,
    label: STAT_TYPE_LABELS[statType] ?? statType,
  }));
}

/**
 * Check if a stat type is valid for a sport.
 */
export function isValidStatForSport(sportKey: SportKey, statType: StatType): boolean {
  const validStats = STAT_TYPES_BY_SPORT[sportKey];
  if (!validStats) return false;
  return validStats.includes(statType);
}

/**
 * Check if a stat type is valid for a sport ID.
 */
export function isValidStatForSportId(sportId: number, statType: StatType): boolean {
  const sportKey = SPORT_ID_TO_KEY[sportId];
  if (!sportKey) return false;
  return isValidStatForSport(sportKey, statType);
}

/**
 * Get sport key from ID with fallback.
 */
export function getSportKeyFromId(sportId: number): SportKey | undefined {
  return SPORT_ID_TO_KEY[sportId];
}

/**
 * Get the label for a stat type.
 */
export function getStatTypeLabel(statType: StatType): string {
  return STAT_TYPE_LABELS[statType] ?? statType;
}
