"use client";

import React, { useRef, useEffect } from "react";
import { clsx } from "clsx";

interface ProgressProps {
  value: number;
  className?: string;
  color?: "success" | "warning" | "danger" | "purple";
  showGlow?: boolean;
}

export function Progress({ value, className, color = "success", showGlow = true }: ProgressProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.style.width = `${value}%`;
    }
  }, [value]);

  const colorClasses = {
    success: "bg-brand-success",
    warning: "bg-brand-warning",
    danger: "bg-brand-danger",
    purple: "bg-brand-purple",
  };

  const glowClasses = {
    success: "shadow-glow shadow-brand-success/40",
    warning: "shadow-glow shadow-brand-warning/40",
    danger: "shadow-glow shadow-brand-danger/40",
    purple: "shadow-glow shadow-brand-purple/40",
  };

  return (
    <div 
      ref={ref}
      className={clsx("h-full transition-all duration-1000", colorClasses[color], showGlow && glowClasses[color], className)} 
    />
  );
}
