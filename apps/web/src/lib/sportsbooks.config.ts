export const SPORTSBOOKS = {
    draftkings: { label: "DraftKings", color: "#53d337", logo: "/logos/dk.svg" },
    fanduel: { label: "FanDuel", color: "#1493ff", logo: "/logos/fd.svg" },
    betmgm: { label: "BetMGM", color: "#c8a84b", logo: "/logos/mgm.svg" },
    caesars: { label: "Caesars", color: "#0d3366", logo: "/logos/czr.svg" },
    bet365: { label: "Bet365", color: "#027b5b", logo: "/logos/b365.svg" },
    betrivers: { label: "BetRivers", color: "#003087", logo: "/logos/br.svg" },
    espnbet: { label: "ESPN Bet", color: "#cc0000", logo: "/logos/espn.svg" },
    pinnacle: { label: "Pinnacle", color: "#ee9c1e", logo: "/logos/pinn.svg" },
    bovada: { label: "Bovada", color: "#cc0000", logo: "/logos/bov.svg" },
    fliff: { label: "Fliff", color: "#7b2fff", logo: "/logos/fl.svg" },
} as const;

export type SportsbookKey = keyof typeof SPORTSBOOKS;
export const ALL_BOOKS = Object.keys(SPORTSBOOKS) as SportsbookKey[];
