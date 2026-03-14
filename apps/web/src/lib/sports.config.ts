export const SPORTS_CONFIG = {
    basketball_nba: { label: "NBA", icon: "🏀", season: true, espn: "nba" },
    basketball_wnba: { label: "WNBA", icon: "🏀", season: true, espn: "wnba" },
    basketball_ncaab: { label: "NCAAB", icon: "🏀", season: true, espn: "mens-college-basketball" },
    americanfootball_nfl: { label: "NFL", icon: "🏈", season: false, espn: "nfl" },
    americanfootball_ncaaf: { label: "NCAAF", icon: "🏈", season: false, espn: "college-football" },
    baseball_mlb: { label: "MLB", icon: "⚾", season: false, espn: "mlb" },
    icehockey_nhl: { label: "NHL", icon: "🏒", season: true, espn: "nhl" },
    soccer_epl: { label: "EPL", icon: "⚽", season: true, espn: "eng.1" },
    soccer_uefa_champs_league: { label: "UCL", icon: "⚽", season: true, espn: "uefa.champions" },
    mma_mixed_martial_arts: { label: "UFC", icon: "🥊", season: true, espn: "ufc" },
    tennis_atp: { label: "Tennis", icon: "🎾", season: true, espn: "tennis" },
    golf_pga_tour: { label: "PGA", icon: "⛳", season: true, espn: "golf" },
    boxing_boxing: { label: "Boxing", icon: "🥊", season: true, espn: "boxing" },
    all: { label: "All Sports", icon: "🌍", season: true, espn: null },
} as const;

export type SportKey = keyof typeof SPORTS_CONFIG;
export const ALL_SPORTS = Object.keys(SPORTS_CONFIG) as SportKey[];
export const ACTIVE_SPORTS = ALL_SPORTS.filter(k => k !== 'all' && SPORTS_CONFIG[k].season);
export const DISPLAY_SPORTS = ALL_SPORTS.filter(k => k !== 'all');
