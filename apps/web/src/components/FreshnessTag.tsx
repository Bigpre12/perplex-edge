"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";

interface Props {
    updatedAt: string | Date | null;
    staleAfterMinutes?: number;
}

export function FreshnessTag({ updatedAt, staleAfterMinutes = 10 }: Props) {
    const [label, setLabel] = useState("");
    const [isStale, setIsStale] = useState(false);

    useEffect(() => {
        if (!updatedAt) return;
        const update = () => {
            const diff = Math.floor((Date.now() - new Date(updatedAt).getTime()) / 1000);
            const stale = diff > staleAfterMinutes * 60;
            setIsStale(stale);
            if (diff < 60) setLabel(`${diff}s ago`);
            else if (diff < 3600) setLabel(`${Math.floor(diff / 60)}m ago`);
            else setLabel(`${Math.floor(diff / 3600)}h ago`);
        };
        update();
        const t = setInterval(update, 15_000);
        return () => clearInterval(t);
    }, [updatedAt, staleAfterMinutes]);

    return (
        <span className={`inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${isStale ? "bg-red-500/10 text-red-400 border border-red-500/20" : "bg-gray-800 text-gray-500"
            }`}>
            <RefreshCw size={9} className={isStale ? "animate-spin" : ""} />
            {label || "Live"}
        </span>
    );
}
