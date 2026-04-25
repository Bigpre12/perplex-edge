export const SPORT_KEY_MAP: Record<string, string> = {
  all: "basketball_nba",
  nba: "basketball_nba",
  basketball_nba: "basketball_nba",
  nfl: "americanfootball_nfl",
  americanfootball_nfl: "americanfootball_nfl",
  mlb: "baseball_mlb",
  baseball_mlb: "baseball_mlb",
  nhl: "icehockey_nhl",
  icehockey_nhl: "icehockey_nhl",
  ncaaf: "americanfootball_ncaaf",
  americanfootball_ncaaf: "americanfootball_ncaaf",
  ncaab: "basketball_ncaab",
  basketball_ncaab: "basketball_ncaab",
  wnba: "basketball_wnba",
  basketball_wnba: "basketball_wnba",
  ufc: "mma_mixed_martial_arts",
  mma_mixed_martial_arts: "mma_mixed_martial_arts",
  mls: "soccer_usa_mls",
  soccer_usa_mls: "soccer_usa_mls",
  epl: "soccer_epl",
  soccer_epl: "soccer_epl",
};

export function normalizeSportKey(raw?: string | null): string {
  if (!raw) return "basketball_nba";
  return SPORT_KEY_MAP[raw] || raw;
}
