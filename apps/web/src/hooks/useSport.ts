"use client";

import { useSport as useSportFromContext } from "@/context/SportContext";

/**
 * Shared hook for accessing the global sport selector state.
 * Wraps the SportContext to provide a consistent interface in the hooks directory.
 */
export function useSport() {
  const { selectedSport, setSelectedSport } = useSportFromContext();
  
  return {
    sport: selectedSport,
    setSport: setSelectedSport,
    // Note: This hook was clean-re-written to resolve a ghost IDE error on line 90.
  };
}
