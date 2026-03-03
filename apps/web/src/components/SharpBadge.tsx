"use client";

interface Props {
    lineMovement?: number;   // e.g. -1.5 means line dropped 1.5 pts
    isSteam?: boolean;
    sharpBook?: string;      // e.g. "Pinnacle"
    publicPct?: number;      // 0-100
}

export function SharpBadge({ lineMovement, isSteam, sharpBook, publicPct }: Props) {
    if (!isSteam && !lineMovement) return null;

    return (
        <div className="flex items-center gap-2 flex-wrap mb-2">
            {isSteam && (
                <span className="flex items-center gap-1.5 bg-yellow-400 text-black text-[10px] font-black px-2 py-0.5 rounded shadow-[0_0_12px_rgba(250,204,21,0.4)] animate-pulse">
                    <span className="text-xs">⚡</span> SHARP
                </span>
            )}

            {lineMovement !== undefined && lineMovement !== 0 && (
                <span className={`text-[10px] px-2 py-0.5 rounded font-bold border ${lineMovement < 0
                        ? "bg-emerald-500/15 border-emerald-500/30 text-emerald-400"
                        : "bg-rose-500/15 border-rose-500/30 text-rose-400"
                    }`}>
                    Line {lineMovement > 0 ? "+" : ""}{lineMovement}
                </span>
            )}

            {sharpBook && (
                <span className="text-[10px] text-gray-300 bg-gray-800 px-2 py-0.5 rounded border border-gray-700 font-medium">
                    📍 {sharpBook}
                </span>
            )}

            {publicPct !== undefined && (
                <div className="flex items-center gap-1.5 ml-1">
                    <div className="w-10 h-1 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
                        <div className="h-full bg-blue-500" style={{ width: `${publicPct}%` }} />
                    </div>
                    <span className="text-[10px] text-gray-500 font-medium">
                        {publicPct}% public
                    </span>
                </div>
            )}
        </div>
    );
}
