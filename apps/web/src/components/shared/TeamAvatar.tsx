"use client";

import React, { useMemo, useState } from "react";
import { clsx } from "clsx";

/** 3+ letter abbreviation from team name (e.g. "Los Angeles Lakers" → "LAL"). */
export function teamAbbreviation(teamName: string, maxLen = 3): string {
  const t = (teamName || "").trim();
  if (!t) return "TM";
  const words = t.split(/\s+/).filter(Boolean);
  if (words.length >= 2) {
    const abbr = words.map((w) => w[0]).join("").toUpperCase();
    return abbr.slice(0, maxLen);
  }
  const alpha = t.replace(/[^a-zA-Z]/g, "");
  return (alpha.slice(0, maxLen) || "TM").toUpperCase();
}

export type TeamAvatarProps = {
  teamName: string;
  logoUrl?: string | null;
  abbr?: string | null;
  className?: string;
};

export function TeamAvatar({ teamName, logoUrl, abbr, className }: TeamAvatarProps) {
  const [imgErr, setImgErr] = useState(false);
  const letters = useMemo(
    () => (abbr && abbr.length > 0 ? abbr.toUpperCase().slice(0, 3) : teamAbbreviation(teamName)),
    [abbr, teamName]
  );

  if (logoUrl && !imgErr) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={logoUrl}
        alt={teamName}
        className={clsx("object-contain", className)}
        onError={() => setImgErr(true)}
      />
    );
  }

  return (
    <div
      className={clsx(
        "flex items-center justify-center font-black italic text-white tracking-tighter bg-lucrix-dark border border-white/10",
        className
      )}
      title={teamName}
    >
      {letters}
    </div>
  );
}
