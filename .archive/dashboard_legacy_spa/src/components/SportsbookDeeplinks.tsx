import React, { useState } from "react";
import { Copy, Share2, Check } from 'lucide-react';

interface DeepLink {
    sportsbook: string;
    logo: string;
    color: string;
    web_url: string;
    app_url: string;
    label: string;
}

interface Props {
    id?: number;
    playerName: string;
    statType: string;
    line: number;
    side?: string;
    odds?: number;
    fullData?: any;
}

const SPORTSBOOK_DISPLAY: Record<string, { name: string; short: string; color: string }> = {
    fanduel: { name: "FanDuel", short: "FD", color: "#1975d2" },
    draftkings: { name: "DraftKings", short: "DK", color: "#53d337" },
    betmgm: { name: "BetMGM", short: "MGM", color: "#d4af37" },
    caesars: { name: "Caesars", short: "CZR", color: "#003087" },
    betrivers: { name: "BetRivers", short: "BR", color: "#f7b500" },
    pointsbet: { name: "PointsBet", short: "PB", color: "#e4002b" },
};

export const SportsbookDeeplinks: React.FC<Props> = ({
    id, playerName, statType, line, side = "over", odds, fullData
}) => {
    const [clicked, setClicked] = useState<string | null>(null);
    const [sharing, setSharing] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleClick = (link: any) => {
        setClicked(link.key);
        const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent);
        const url = isMobile ? link.app_url : link.web_url;
        window.open(url, "_blank", "noopener,noreferrer");
        setTimeout(() => setClicked(null), 1500);
    };

    const handleShare = async () => {
        setSharing(true);
        try {
            const shareData = fullData || {
                playerName, statType, line, side, odds, id
            };

            const res = await fetch("http://localhost:8000/share/create", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(shareData)
            });
            const data = await res.json();

            if (data.share_id) {
                const shareUrl = `${window.location.origin}/share/${data.share_id}`;
                await navigator.clipboard.writeText(shareUrl);
                setCopied(true);
                setTimeout(() => setCopied(false), 3000);
            }
        } catch (err) {
            console.error("Failed to create share link:", err);
        } finally {
            setSharing(false);
        }
    };

    return (
        <div className="flex flex-col gap-4 p-4 glass-panel border border-white/10 rounded-xl">
            <div className="flex items-center justify-between">
                <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Select Books</span>
                <span className="text-[9px] font-bold text-primary px-1.5 py-0.5 bg-primary/10 rounded tracking-tighter uppercase">Viral Tail Enabled</span>
            </div>

            <div className="grid grid-cols-3 gap-2">
                {Object.entries(SPORTSBOOK_DISPLAY).map(([key, display]) => {
                    const isClicked = clicked === key;
                    const playerEncoded = encodeURIComponent(playerName);

                    // Direct Deeplink URL construction logic
                    const web_url = `https://sportsbook.${key === "fanduel" ? "fanduel.com" : key === "draftkings" ? "draftkings.com" : key + ".com"}/search?q=${playerEncoded}`;
                    const app_url = `${key}://search?q=${playerEncoded}`;

                    return (
                        <button
                            key={key}
                            onClick={() => handleClick({ key, web_url, app_url })}
                            className={`flex flex-col items-center gap-1 p-3 rounded-lg border transition-all ${isClicked
                                ? 'bg-primary/20 border-primary/50 text-primary shadow-[0_0_15px_rgba(13,242,51,0.2)]'
                                : 'bg-white/5 border-white/5 text-slate-400 hover:bg-white/10 hover:border-white/20'
                                }`}
                        >
                            <span className="text-[9px] font-black opacity-50">{display.short}</span>
                            <span className="text-xs font-bold">{display.name}</span>
                            {isClicked && <Check size={10} className="text-primary animate-pulse mt-0.5" />}
                        </button>
                    );
                })}
            </div>

            <div className="pt-2 border-t border-white/5">
                <button
                    onClick={handleShare}
                    disabled={sharing}
                    className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-black text-[11px] uppercase tracking-[0.1em] transition-all ${copied
                        ? 'bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.3)]'
                        : 'bg-primary text-background-dark hover:scale-[1.02] active:scale-[0.98]'
                        }`}
                >
                    {sharing ? (
                        <div className="size-4 border-2 border-background-dark/30 border-t-background-dark rounded-full animate-spin"></div>
                    ) : copied ? (
                        <>
                            <Copy size={14} /> Link Copied to Clipboard
                        </>
                    ) : (
                        <>
                            <Share2 size={14} /> Create Viral Tail Link
                        </>
                    )}
                </button>
                <p className="text-[9px] text-slate-500 text-center mt-3 font-medium">Rebuilds entire betslip on any book for followers.</p>
            </div>
        </div>
    );
};


export default SportsbookDeeplinks;
