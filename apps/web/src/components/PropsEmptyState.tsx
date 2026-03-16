"use client";
import React, { useEffect, useState } from "react";
import { Clock, RefreshCw, Calendar } from "lucide-react";
import { motion } from "framer-motion";

interface Game {
    home: string;
    away: string;
    time: string;
}

export default function PropsEmptyState({ sport = "NBA" }) {
    const [games, setGames] = useState<Game[]>([]);
    const [nextTipoff, setNextTipoff] = useState("");

    useEffect(() => {
        // ESPN scoreboard for context
        const path = sport.toLowerCase().includes("nba") ? "basketball/nba" : "basketball/nba";
        fetch(`https://site.api.espn.com/apis/site/v2/sports/${path}/scoreboard`)
            .then(r => r.json())
            .then(data => {
                const events = data.events ?? [];
                const parsed: Game[] = events.map((e: any) => ({
                    away: e.competitions[0].competitors.find((c: any) => c.homeAway === "away")?.team.shortDisplayName,
                    home: e.competitions[0].competitors.find((c: any) => c.homeAway === "home")?.team.shortDisplayName,
                    time: new Date(e.date).toLocaleTimeString("en-US", {
                        hour: "numeric",
                        minute: "2-digit",
                        timeZone: "America/New_York",
                    })
                }));
                setGames(parsed.slice(0, 5));

                if (events.length > 0) {
                    const earliest = new Date(events[0].date);
                    earliest.setHours(earliest.getHours() - 3);
                    setNextTipoff(earliest.toLocaleTimeString("en-US", {
                        hour: "numeric", minute: "2-digit"
                    }));
                }
            })
            .catch(() => { });
    }, [sport]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-20 px-4 text-center"
        >
            <div className="w-20 h-20 bg-brand-success/10 rounded-full flex items-center justify-center mb-6 border border-brand-success/20 shadow-glow shadow-brand-success/20">
                <Clock className="text-brand-success w-10 h-10" />
            </div>

            <h2 className="text-2xl font-black text-white italic uppercase tracking-tighter mb-2 font-display">
                Lines Warming Up
            </h2>
            <p className="text-textSecondary text-sm max-w-md mx-auto mb-8 font-medium">
                {sport} props typically post 4-6 hours before tip-off. Our engine is currently scanning for early value.
            </p>

            {games.length > 0 && (
                <div className="w-full max-w-sm bg-lucrix-surface backdrop-blur-md rounded-2xl border border-lucrix-border p-4 mb-8 shadow-card">
                    <div className="flex items-center gap-2 mb-4 text-[10px] font-black text-textMuted uppercase tracking-widest px-1">
                        <Calendar size={12} /> Today&apos;s Slate
                    </div>
                    <div className="space-y-2">
                        {games.map((g, i) => (
                            <div key={i} className="flex justify-between items-center bg-lucrix-dark/50 p-3 rounded-xl border border-lucrix-border/50">
                                <span className="text-xs font-black text-white uppercase tracking-tight font-display">
                                    {g.away} <span className="text-textMuted">@</span> {g.home}
                                </span>
                                <span className="text-[10px] font-mono text-brand-success font-bold">{g.time}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="space-y-4">
                {nextTipoff && (
                    <p className="text-[10px] font-black text-brand-success uppercase tracking-widest bg-brand-success/5 px-4 py-2 rounded-full border border-brand-success/10">
                        Check back after {nextTipoff} ET for live lines
                    </p>
                )}

                <button
                    onClick={() => window.location.reload()}
                    className="group flex items-center gap-2 text-[10px] font-black text-textMuted uppercase tracking-widest hover:text-white transition-colors mx-auto"
                >
                    <RefreshCw size={12} className="group-hover:rotate-180 transition-transform duration-500" />
                    Manually Sync Slate
                </button>
            </div>
        </motion.div>
    );
}
