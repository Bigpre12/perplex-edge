export const SPORTSBOOKS = {
    draftkings: { label: "DraftKings", color: "#53d337" },
    fanduel: { label: "FanDuel", color: "#1493ff" },
    betmgm: { label: "BetMGM", color: "#c8a84b" },
    caesars: { label: "Caesars", color: "#0d3366" },
    pointsbet: { label: "PointsBet", color: "#e41e26" },
    bet365: { label: "Bet365", color: "#027b5b" },
    betrivers: { label: "BetRivers", color: "#003087" },
    espnbet: { label: "ESPN Bet", color: "#cc0000" },
    hardrock: { label: "Hard Rock", color: "#b8860b" },
    fliff: { label: "Fliff", color: "#7b2fff" },
} as const;

export type SportsbookKey = keyof typeof SPORTSBOOKS;
export const ALL_BOOKS = Object.keys(SPORTSBOOKS) as SportsbookKey[];
