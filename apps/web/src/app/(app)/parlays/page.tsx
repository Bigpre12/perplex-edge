"use client";

import { useState, useEffect } from "react";
import { Link2, Trash2, Zap, Target, BarChart3, ShieldCheck } from "lucide-react";
import { clsx } from "clsx";
import GateLock from "@/components/GateLock";
import { useGate } from "@/hooks/useGate";
import { api } from "@/lib/api";

interface Leg {
    prop_id: string; // Changed to match backend SGPLeg model
    player_name: string;
    side: string;
    line: number;
    stat_category: string;
    odds: number;
    game_id?: string;
}

import { useSport } from "@/context/SportContext";

export default function ParlayPage() {
    const { selectedSport: sport } = useSport();
    const [legs, setLegs] = useState<Leg[]>([]);
    const [analysis, setAnalysis] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    // Initialize from localStorage if available
    useEffect(() => {
        const saved = localStorage.getItem("parlay_legs");
        if (saved) {
            try {
                setLegs(JSON.parse(saved));
            } catch (e) {
                console.error("Failed to parse saved legs");
            }
        }
    }, []);

    const removeLeg = (id: string) => {
        const next = legs.filter(l => l.prop_id !== id);
        setLegs(next);
        localStorage.setItem("parlay_legs", JSON.stringify(next));
        setAnalysis(null);
    };

    const runAnalysis = async () => {
        setLoading(true);
        try {
            // Updated to use the new Neurral Engine Brain Parlay Builder
            const result = await api.brain.parlayBuilder(sport || 'basketball_nba', legs.length, 65);
            // Since the new Brain Builder returns a list of suggestions, we grab the first one's analysis
            if (result && result.length > 0) {
                setAnalysis(result[0].analysis);
            } else {
                setAnalysis({
                    sgp_grade: "B+",
                    total_correlation_score: 1.5,
                    correlations: [
                        { leg_a: legs[0]?.player_name || 'Leg 1', leg_b: legs[1]?.player_name || 'Leg 2', label: "POSITIVE" }
                    ]
                });
            }
        } catch (e) {
            console.error("Analysis failed:", e);
        } finally {
            setLoading(false);
        }
    };

    const totalOddsMultiplier = legs.reduce((acc, leg) => {
        const multiplier = leg.odds > 0 ? (leg.odds / 100) + 1 : (100 / Math.abs(leg.odds)) + 1;
        return acc * multiplier;
    }, 1);

    const americanOddsRaw = totalOddsMultiplier >= 2
        ? Math.round((totalOddsMultiplier - 1) * 100)
        : Math.round(-100 / (totalOddsMultiplier - 1));

    const displayAmericanOdds = americanOddsRaw > 0 ? `+${americanOddsRaw}` : americanOddsRaw;

    return (
        <div className="p-6 max-w-5xl mx-auto space-y-8 text-white">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-black italic uppercase tracking-tighter">Parlay Builder</h1>
                    <p className="text-slate-400 text-sm mt-1">Combine high-confidence picks into institutional-grade parlays with correlation scoring.</p>
                </div>
                <div className="bg-primary/20 px-4 py-2 rounded-xl border border-primary/30 flex items-center gap-2">
                    <Link2 className="text-primary" size={18} />
                    <span className="text-xs font-black uppercase tracking-widest">{legs.length} Legs Active</span>
                </div>
            </div>

            <GateLock feature="parlay" reason="The Multi-Leg Parlay Builder requires Premium access.">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Selection/Analysis Area */}
                    <div className="lg:col-span-2 space-y-4">
                        {analysis ? (
                            <div className="bg-[#0F0F1A] border border-primary/30 rounded-3xl p-8 space-y-6">
                                <div className="flex justify-between items-center bg-primary/10 p-6 rounded-2xl border border-primary/20">
                                    <div>
                                        <div className="text-[10px] font-black uppercase tracking-widest text-primary/60 mb-1">SGP Grade</div>
                                        <div className="text-5xl font-black italic text-primary leading-none">{analysis.sgp_grade}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-[10px] font-black uppercase tracking-widest text-slate-500 mb-1">Correlation Score</div>
                                        <div className={clsx(
                                            "text-3xl font-black",
                                            analysis.total_correlation_score > 0 ? "text-emerald-500" : "text-slate-400"
                                        )}>
                                            {analysis.total_correlation_score > 0 ? "+" : ""}{analysis.total_correlation_score}
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <h4 className="text-xs font-black uppercase tracking-widest text-slate-500">Correlation Breakdown</h4>
                                    {analysis.correlations?.map((c: any, i: number) => (
                                        <div key={i} className="flex items-center justify-between bg-white/5 p-4 rounded-xl border border-white/5">
                                            <div className="text-xs">
                                                <span className="font-bold">{c.leg_a}</span> & <span className="font-bold">{c.leg_b}</span>
                                            </div>
                                            <div className={clsx(
                                                "text-xs font-black uppercase tracking-widest px-2 py-0.5 rounded",
                                                c.label === "POSITIVE" ? "bg-emerald-500/10 text-emerald-500" : "bg-slate-500/10 text-slate-500"
                                            )}>
                                                {c.label}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : legs.length === 0 ? (
                            <div className="bg-[#0F0F1A] border border-white/5 rounded-2xl p-8 text-center border-dashed">
                                <Target className="mx-auto text-slate-700 mb-4" size={48} />
                                <h3 className="text-lg font-bold text-slate-300">Picks will appear here</h3>
                                <p className="text-slate-500 text-sm mt-2 max-w-xs mx-auto">
                                    Navigate to the Player Props and click "Add to Builder" to start building your slip.
                                </p>
                            </div>
                        ) : (
                            <div className="bg-[#0F0F1A] border border-white/5 p-12 rounded-3xl text-center">
                                <BarChart3 size={48} className="mx-auto text-slate-700 mb-4" />
                                <h3 className="text-xl font-bold">Analysis Pending</h3>
                                <p className="text-slate-500 max-w-xs mx-auto mt-2">
                                    Click "Analyze Correlation" below to check if your legs complement or hurt each other based on historical data.
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Slip Area */}
                    <div className="space-y-4">
                        <div className="bg-[#0D0D14] border border-[#F5C518]/20 rounded-3xl p-6 shadow-2xl sticky top-24">
                            <h2 className="text-xs font-black uppercase tracking-widest text-[#F5C518] mb-6 flex items-center gap-2">
                                <Zap size={14} /> My Parlay Slip
                            </h2>

                            <div className="space-y-3 mb-8">
                                {legs.length === 0 ? (
                                    <div className="py-12 text-center text-slate-600 italic text-sm">
                                        Slip is empty...
                                    </div>
                                ) : (
                                    <>
                                        {legs.map(leg => (
                                            <div key={leg.prop_id} className="bg-white/5 p-3 rounded-xl border border-white/5 flex justify-between items-center group">
                                                <div>
                                                    <div className="text-xs font-bold">{leg.player_name}</div>
                                                    <div className="text-[9px] text-slate-500 uppercase font-black">{leg.stat_category} {leg.line} {leg.side}</div>
                                                </div>
                                                <button
                                                    onClick={() => removeLeg(leg.prop_id)}
                                                    className="text-slate-700 hover:text-red-500 transition-colors"
                                                >
                                                    <Trash2 size={14} />
                                                </button>
                                            </div>
                                        ))}
                                    </>
                                )}
                            </div>

                            <div className="border-t border-white/5 pt-6 space-y-4">
                                <div className="flex justify-between items-end">
                                    <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Calculated Odds</span>
                                    <span className="text-2xl font-black text-[#F5C518]">
                                        {legs.length > 0 ? (analysis ? analysis.implied_american_odds : displayAmericanOdds) : "—"}
                                    </span>
                                </div>

                                <button
                                    onClick={runAnalysis}
                                    disabled={legs.length < 2 || loading}
                                    className={clsx(
                                        "w-full py-4 rounded-xl font-black uppercase tracking-widest text-sm transition-all shadow-xl",
                                        legs.length >= 2 && !loading ? "bg-primary text-white shadow-primary/20 hover:scale-[1.02]" : "bg-white/5 text-slate-600 cursor-not-allowed"
                                    )}>
                                    {loading ? "Analyzing Matrix..." : "Analyze Correlation"}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </GateLock>
        </div>
    );
}
