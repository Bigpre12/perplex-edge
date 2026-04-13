export const SPORTS_CONFIG = {
    basketball_nba: { label: "NBA", icon: "🏀", season: true, espn: "nba", espn_path: "basketball/nba" },
    americanfootball_nfl: { label: "NFL", icon: "🏈", season: true, espn: "nfl", espn_path: "football/nfl" },
    baseball_mlb: { label: "MLB", icon: "⚾", season: true, espn: "mlb", espn_path: "baseball/mlb" },
    icehockey_nhl: { label: "NHL", icon: "🏒", season: true, espn: "nhl", espn_path: "hockey/nhl" },
    americanfootball_ncaaf: { label: "NCAAF", icon: "🏈", season: true, espn: "college-football", espn_path: "football/college-football" },
    basketball_ncaab: { label: "NCAAB", icon: "🏀", season: true, espn: "mens-college-basketball", espn_path: "basketball/mens-college-basketball" },
    basketball_wnba: { label: "WNBA", icon: "🏀", season: true, espn: "wnba", espn_path: "basketball/wnba" },
    soccer_epl: { label: "EPL", icon: "⚽", season: true, espn: "eng.1", espn_path: "soccer/eng.1" },
    soccer_uefa_champs_league: { label: "UCL", icon: "⚽", season: true, espn: "uefa.champions", espn_path: "soccer/uefa.champions" },
    mma_mixed_martial_arts: { label: "UFC", icon: "🥊", season: true, espn: "ufc", espn_path: "mma/ufc" },
    soccer_usa_mls: { label: "MLS", icon: "⚽", season: true, espn: "usa.1", espn_path: "soccer/usa.1" },
    tennis_atp: { label: "Tennis", icon: "🎾", season: true, espn: "atp", espn_path: "tennis/atp" },
    tennis_wta: { label: "Tennis (W)", icon: "🎾", season: true, espn: "wta", espn_path: "tennis/wta" },
    golf_pga: { label: "PGA", icon: "⛳", season: true, espn: "pga", espn_path: "golf/pga" },
    boxing_boxing: { label: "Boxing", icon: "🥊", season: true, espn: "boxing", espn_path: "boxing" },
    all: { label: "All Sports", icon: "🌍", season: true, espn: null, espn_path: "basketball/nba" },
} as const;

export type SportKey = keyof typeof SPORTS_CONFIG;
export const ALL_SPORTS = Object.keys(SPORTS_CONFIG) as SportKey[];
export const ACTIVE_SPORTS = ALL_SPORTS.filter(k => k !== 'all' && SPORTS_CONFIG[k].season);
export const DISPLAY_SPORTS = ALL_SPORTS.filter(k => k !== 'all');
