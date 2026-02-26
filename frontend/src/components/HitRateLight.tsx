import React from "react";

interface Props {
    hitRate: number;           // 0–1 float  e.g. 0.72
    sampleSize?: number;       // number of games
    label?: string;            // e.g. "L5" or "L10" or "vs OPP"
    size?: "sm" | "md" | "lg";
}

function getTrafficLight(rate: number): {
    color: string;
    bg: string;
    glow: string;
    label: string;
    emoji: string;
} {
    if (rate >= 0.70) return { color: "#00e676", bg: "rgba(0,230,118,0.15)", glow: "0 0 8px rgba(0,230,118,0.6)", label: "STRONG", emoji: "🟢" };
    if (rate >= 0.55) return { color: "#ffeb3b", bg: "rgba(255,235,59,0.12)", glow: "0 0 8px rgba(255,235,59,0.5)", label: "LEAN", emoji: "🟡" };
    if (rate >= 0.40) return { color: "#ff9800", bg: "rgba(255,152,0,0.12)", glow: "0 0 8px rgba(255,152,0,0.5)", label: "WEAK", emoji: "🟠" };
    return { color: "#f44336", bg: "rgba(244,67,54,0.12)", glow: "0 0 8px rgba(244,67,54,0.5)", label: "AVOID", emoji: "🔴" };
}

export const HitRateLight: React.FC<Props> = ({
    hitRate, sampleSize, label = "Hit Rate", size = "md"
}) => {
    const light = getTrafficLight(hitRate);
    const pct = Math.round(hitRate * 100);

    const sizes = {
        sm: { dot: 10, font: 11, pctFont: 12 },
        md: { dot: 14, font: 12, pctFont: 14 },
        lg: { dot: 18, font: 13, pctFont: 18 },
    }[size];

    return (
        <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "6px",
            padding: "4px 8px",
            background: light.bg,
            borderRadius: "6px",
            border: `1px solid ${light.color}44`,
        }}>
            {/* Traffic dot */}
            <div style={{
                width: sizes.dot,
                height: sizes.dot,
                borderRadius: "50%",
                background: light.color,
                boxShadow: light.glow,
                flexShrink: 0,
            }} />
            {/* Percentage */}
            <span style={{
                fontSize: sizes.pctFont,
                fontWeight: "700",
                color: light.color,
                fontVariantNumeric: "tabular-nums",
            }}>
                {pct}%
            </span>
            {/* Label */}
            <div style={{ display: "flex", flexDirection: "column", gap: "1px" }}>
                <span style={{ fontSize: sizes.font - 1, color: light.color, fontWeight: "600", letterSpacing: "0.06em" }}>
                    {light.label}
                </span>
                <span style={{ fontSize: sizes.font - 2, color: "#666" }}>
                    {label}{sampleSize ? ` (${sampleSize}G)` : ""}
                </span>
            </div>
        </div>
    );
};

/**
 * Full traffic light stack — shows L5, L10, L20, vs-opponent in a row.
 * Usage: <HitRateStack splits={player.splits} />
 */
interface HitRateStackProps {
    splits: {
        l5?: number;
        l10?: number;
        l20?: number;
        vs_opp?: number;
        season?: number;
    };
    size?: "sm" | "md" | "lg";
}

export const HitRateStack: React.FC<HitRateStackProps> = ({ splits, size = "sm" }) => {
    const windows = [
        { key: "l5", label: "L5", rate: splits.l5, n: 5 },
        { key: "l10", label: "L10", rate: splits.l10, n: 10 },
        { key: "l20", label: "L20", rate: splits.l20, n: 20 },
        { key: "vs_opp", label: "vs OPP", rate: splits.vs_opp, n: undefined },
    ];

    return (
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {windows.map(w => w.rate !== undefined && (
                <HitRateLight
                    key={w.key}
                    hitRate={w.rate}
                    sampleSize={w.n}
                    label={w.label}
                    size={size}
                />
            ))}
        </div>
    );
};
