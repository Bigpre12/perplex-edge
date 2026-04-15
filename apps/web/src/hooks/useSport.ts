"use client";

import { useSport as useSportFromContext } from "@/context/SportContext";

/**
 * Shared hook for accessing the global sport selector state.
 * `sport` normalizes 'all' to 'basketball_nba' so API calls always have a valid sport key.
 * `rawSport` gives the unmodified store value for UI display (e.g. TopNav highlight).
 */
export function useSport() {
  const { selectedSport, setSelectedSport } = useSportFromContext();
  const normalized = (!selectedSport || selectedSport === 'all') ? 'basketball_nba' : selectedSport;
  
  return {
    sport: normalized,
    rawSport: selectedSport,
    setSport: setSelectedSport,
  };
}
