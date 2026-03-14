"use client";
import { useState } from "react";
import { Share, Twitter, Check, Copy } from "lucide-react";

export function ShareCard({ edge }: { edge: any }) {
    const [open, setOpen] = useState(false);
    const [copied, setCopied] = useState(false);

    if (!edge) return null;

    const shareText = `🔥 Sharp Action Detected on Perplex Edge\n\n${edge.player_name} O ${edge.line} ${edge.prop_type?.replace("player_", "")}\nHit Rate: ${(edge.hit_rate_l10 || edge.hit_rate || 0.5) * 100}%\nEdge: ${edge.edge_score}%\n\nGet the full slate: perplexedge.com`;
    const shareUrl = "https://perplexedge.com";

    const handleCopy = () => {
        navigator.clipboard.writeText(shareText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleTwitter = () => {
        window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`, '_blank');
    };

    return (
        <div className="relative inline-block">
            <button
                onClick={(e) => { e.stopPropagation(); setOpen(!open); }}
                className="p-2 bg-gray-800 hover:bg-gray-700 rounded-full text-gray-400 hover:text-white transition"
            >
                <Share size={16} />
            </button>

            {open && (
                <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-2">
                    <div className="p-3 border-b border-gray-800 bg-black/40">
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Share Play</p>
                    </div>
                    <div className="p-2 space-y-1">
                        <button
                            onClick={(e) => { e.stopPropagation(); handleTwitter(); setOpen(false); }}
                            className="w-full flex items-center gap-3 p-2 hover:bg-blue-500/10 text-gray-300 hover:text-blue-400 rounded-lg transition text-sm text-left"
                        >
                            <Twitter size={16} /> Share to X
                        </button>
                        <button
                            onClick={(e) => { e.stopPropagation(); handleCopy(); }}
                            className="w-full flex items-center gap-3 p-2 hover:bg-gray-800 text-gray-300 rounded-lg transition text-sm text-left"
                        >
                            {copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
                            {copied ? "Copied!" : "Copy Text"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
