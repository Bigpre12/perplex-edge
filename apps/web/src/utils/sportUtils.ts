/**
 * Utility for sports seasonality and filtering.
 * Based on February 2026 current date.
 */

export interface Sport {
    id: string;
    name: string;
    icon: string;
    inSeason: boolean;
}

export const SPORTS: Sport[] = [
    { id: 'basketball_nba', name: 'NBA', icon: 'sports_basketball', inSeason: true },
    { id: 'basketball_wnba', name: 'WNBA', icon: 'sports_basketball', inSeason: true },
    { id: 'icehockey_nhl', name: 'NHL', icon: 'sports_hockey', inSeason: true },
    { id: 'americanfootball_nfl', name: 'NFL', icon: 'sports_football', inSeason: false },
    { id: 'baseball_mlb', name: 'MLB', icon: 'sports_baseball', inSeason: false },
    { id: 'tennis_atp', name: 'Tennis (ATP/WTA)', icon: 'sports_tennis', inSeason: true },
    { id: 'boxing_boxing', name: 'Boxing', icon: 'sports_mma', inSeason: true },
    { id: 'mma_mixed_martial_arts', name: 'MMA', icon: 'sports_martial_arts', inSeason: true },
    { id: 'soccer_epl', name: 'Soccer (EPL)', icon: 'sports_soccer', inSeason: true },
];

export const getInSeasonSports = () => SPORTS.filter(s => s.inSeason);

export const isSportActive = (sportId: string) => {
    const sport = SPORTS.find(s => s.id === sportId || s.name === sportId);
    return sport ? sport.inSeason : true; // Default to true for unknown sports
};
