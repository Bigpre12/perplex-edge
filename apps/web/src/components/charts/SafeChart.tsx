"use client";

import { useEffect, useState, type ReactNode } from "react";

type SafeChartProps = {
  children: ReactNode;
  minHeight?: number;
};

/**
 * Avoid Recharts measuring width/height -1 when the parent is animating (e.g. framer-motion)
 * or not yet laid out.
 */
export function SafeChart({ children, minHeight = 200 }: SafeChartProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div
        className="animate-pulse rounded-md bg-white/5"
        style={{ height: minHeight, minWidth: 1, width: "100%" }}
        aria-hidden
      />
    );
  }

  return (
    <div style={{ minWidth: 1, minHeight, width: "100%", height: "100%" }}>{children}</div>
  );
}
