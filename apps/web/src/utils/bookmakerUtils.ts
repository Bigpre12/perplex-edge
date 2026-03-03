/**
 * Texas-Available Sportsbooks & Sharp Reference Utilities
 * Localization for Lucrix Texas Users
 */

export const TEXAS_BOOKS = [
    "fanduel",
    "draftkings",
    "betmgm",
    "caesars",
    "espnbet",
    "hardrock",
    "fliff",
];

export const SHARP_REFERENCE_BOOKS = [
    "pinnacle",
    "betonlineag",
    "mybookieag",
    "bovada",
    "betwhale",
];

/**
 * Returns true if a bookmaker is available for betting in Texas
 */
export const isTexasAvailable = (bookKey: string): boolean => {
    return TEXAS_BOOKS.includes(bookKey.toLowerCase());
};

/**
 * Returns true if a bookmaker is considered a "Sharp" reference line
 */
export const isSharpBook = (bookKey: string): boolean => {
    return SHARP_REFERENCE_BOOKS.includes(bookKey.toLowerCase());
};

/**
 * Formats bookmaker key for display
 */
export const formatBookName = (key: string): string => {
    const names: Record<string, string> = {
        fanduel: "FanDuel",
        draftkings: "DraftKings",
        betmgm: "BetMGM",
        caesars: "Caesars",
        espnbet: "ESPN BET",
        hardrock: "Hard Rock",
        fliff: "Fliff",
        pinnacle: "Pinnacle",
        betonlineag: "BetOnline",
        mybookieag: "MyBookie",
        bovada: "Bovada",
        betwhale: "BetWhale",
        betrivers: "BetRivers",
        unibet: "Unibet",
        pointsbet: "PointsBet",
        superbook: "SuperBook",
        windcreek: "Wind Creek",
    };
    return names[key.toLowerCase()] || key.charAt(0).toUpperCase() + key.slice(1);
};
