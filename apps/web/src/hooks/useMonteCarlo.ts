"use client";

import { useState } from "react";

export function useMonteCarlo() {
  const [result, setResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const runSimulation = async (legs: any[], trials = 10000) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch("/backend/api/parlays/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ legs, n_sims: trials }),
      });
      if (!response.ok) throw new Error(`Simulation failed (${response.status})`);
      const json = await response.json();
      setResult(json);
      setLastUpdated(new Date().toISOString());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run simulation");
    } finally {
      setIsLoading(false);
    }
  };

  return { result, isLoading, error, runSimulation, lastUpdated };
}
