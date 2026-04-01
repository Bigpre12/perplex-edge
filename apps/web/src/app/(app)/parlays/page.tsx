"use client";

import { useState } from "react";
import { Zap, Target, BarChart3, ShieldCheck, CheckCircle2 } from "lucide-react";
import { clsx } from "clsx";
import GateLock from "@/components/GateLock";
import { api, isApiError } from "@/lib/api";
import { useSport } from "@/hooks/useSport";
import { useLucrixStore } from "@/store";
import { motion, AnimatePresence } from "framer-motion";
import { ParlayLegCard } from "@/components/parlay/ParlayLegCard";

export default function ParlayPage() {
    const { sport } = useSport();
    const { parlayLegs: legs, addLeg, removeLeg, clearParlay } = useLucrixStore();
    const [analysis, setAnalysis] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [aiBuilding, setAiBuilding] = useState(false);

    const handleAiBuild = async (override?: boolean) => {
        setAiBuilding(true);
        try {
            const data = await (api as any).buildParlay(sport);
            const newLegs = Array.isArray(data) ? data : (data.legs || []);
            if (override === true) {
                clearParlay();
                newLegs.forEach((leg: any) => addLeg(leg));
            } else {
                // Add first missing leg
                const missing = newLegs.find((nl: any) => !legs.find((l: any) => l.prop_id === nl.prop_id));
                if (missing) addLeg(missing);
            }
            setAnalysis(null);
        } catch (e) {
            console.error("AI Build failed", e);
        } finally {
            setAiBuilding(false);
        }
    };

    const runAnalysis = async () => {
        if (legs.length === 0) return;
        setLoading(true);
        try {
            // Map legs to simulation format
            const simLegs = legs.map(leg => ({
                player_name: leg.player_name || leg.selection || "Unknown",
                market: leg.stat_category || leg.market_key || "Prop",
                line: Number(leg.line) || 0,
                side: (leg.side || "over").toLowerCase(),
                over_price: Number(leg.odds_over || leg.odds || -110),
                under_price: Number(leg.odds_under || -110),
                historical_hit_rate: Number(leg.confidence || 0.5)
            }));

            const result = await (api as any).simulate(simLegs, 100, 10000);
            
            if (result && !isApiError(result)) {
                setAnalysis({
                    sgp_grade: result.roi > 5 ? "S" : result.roi > 2 ? "A" : result.roi > 0 ? "B" : "C",
                    total_correlation_score: result.edge?.toFixed(2) || "0.00",
                    edge: ((result.edge || 0) * 100).toFixed(1),
                    win_rate: ((result.win_rate || 0) * 100).toFixed(1),
                    ev: result.expected_value || 0,
                    roi: result.roi || 0,
                    max_drawdown: result.max_drawdown || 0,
                    confidence: result.confidence?.toUpperCase() || "MEDIUM",
                    true_prob: ((result.true_probability || 0) * 100).toFixed(1),
                });
            }
        } catch (e) {
            console.error("Simulation failed:", e);
        } finally {
            setLoading(false);
        }
    };

    const totalOddsMultiplier = legs.reduce((acc, leg) => {
        const odds = Number(leg.odds || leg.odds_over || -110);
        const multiplier = odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
        return acc * multiplier;
    }, 1);

    const americanOddsRaw = totalOddsMultiplier >= 2
        ? Math.round((totalOddsMultiplier - 1) * 100)
        : Math.round(-100 / (totalOddsMultiplier - 1));

    const displayAmericanOdds = americanOddsRaw > 0 ? `+${americanOddsRaw}` : americanOddsRaw;

    // Grade Color Mappings
    const gradeStyles: Record<string, string> = {
        'S': 'text-yellow-400 border-yellow-400 shadow-[0_0_25px_rgba(250,204,21,0.5)]',
        'A': 'text-emerald-400 border-emerald-400 shadow-[0_0_25px_rgba(52,211,153,0.5)]',
        'B': 'text-blue-400 border-blue-400 shadow-[0_0_25px_rgba(96,165,250,0.5)]',
        'C': 'text-slate-400 border-slate-400 shadow-[0_0_25px_rgba(148,163,184,0.5)]',
    };

    return (
        <div className="pb-32 space-y-10 pt-10 px-6 max-w-[1400px] mx-auto text-white">
            {/* Premium Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/5 pb-10">
                <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                >
                    <div className="flex items-center gap-4 mb-2">
                        <h1 className="text-4xl font-black italic tracking-tighter uppercase font-display leading-none">
                            Parlay <span className="text-brand-primary">Matrix</span>
                        </h1>
                        <button
                            onClick={() => handleAiBuild(true)}
                            disabled={aiBuilding}
                            className="flex items-center gap-2 px-4 py-1.5 bg-brand-primary/10 border border-brand-primary/20 rounded-full text-[10px] font-black uppercase tracking-widest text-brand-primary hover:bg-brand-primary hover:text-white transition-all disabled:opacity-50"
                        >
                            <Zap size={14} className={aiBuilding ? "animate-spin" : "fill-current"} />
                            {aiBuilding ? "Neural Building..." : "Build Me a Parlay"}
                        </button>
                    </div>
                    <p className="text-textMuted text-xs font-bold uppercase tracking-widest leading-none">
                        Cross-Market Simulation & Correlation Engine
                    </p>
                </motion.div>
                
                <div className="flex items-center gap-4 bg-white/5 backdrop-blur-md border border-white/10 p-4 rounded-2xl shadow-xl">
                    <div className="flex flex-col items-center px-4 border-r border-white/10">
                        <span className="text-[9px] font-black uppercase tracking-widest text-textMuted mb-1">Active Legs</span>
                        <span className="text-xl font-black italic text-white">{legs.length}</span>
                    </div>
                    <div className="flex flex-col items-center px-4">
                        <span className="text-[9px] font-black uppercase tracking-widest text-textMuted mb-1">Total Odds</span>
                        <span className="text-xl font-black italic text-brand-primary">{legs.length > 0 ? displayAmericanOdds : "---"}</span>
                    </div>
                </div>
            </div>

            <GateLock feature="parlay">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                    <div className="lg:col-span-8 space-y-6">
                        <AnimatePresence mode="wait">
                            {loading ? (
                                <motion.div 
                                    key="loading"
                                    initial={{ opacity: 0, scale: 0.98 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 1.02 }}
                                    className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-3xl p-16 flex flex-col items-center justify-center text-center space-y-6 h-[450px]"
                                >
                                    <div className="relative">
                                        <div className="w-20 h-20 border-4 border-brand-primary/10 border-t-brand-primary rounded-full animate-spin" />
                                        <Zap size={24} className="absolute inset-0 m-auto text-brand-primary animate-pulse" />
                                    </div>
                                    <div className="space-y-2">
                                        <h3 className="text-2xl font-black italic uppercase tracking-tighter">Running Monte Carlo</h3>
                                        <p className="text-textMuted text-xs font-bold uppercase tracking-widest animate-pulse italic">
                                            Simulating 10,000 trials... Processing Correlation Matrix...
                                        </p>
                                    </div>
                                </motion.div>
                            ) : analysis ? (
                                <motion.div 
                                    key="analysis"
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-3xl overflow-hidden"
                                >
                                    <div className="bg-gradient-to-br from-brand-primary/20 via-transparent to-transparent p-10 flex flex-col md:flex-row items-center justify-between gap-8 border-b border-white/5">
                                        <div className="flex items-center gap-6">
                                            <div className="relative group">
                                                <div className="absolute -inset-4 bg-brand-primary/20 rounded-full blur-2xl group-hover:bg-brand-primary/40 transition duration-500" />
                                                <div className={clsx(
                                                    "relative w-24 h-24 rounded-full border-4 flex items-center justify-center bg-lucrix-dark/80 transition-all duration-700",
                                                    gradeStyles[analysis.sgp_grade] || gradeStyles['C']
                                                )}>
                                                    <span className="text-5xl font-black italic">{analysis.sgp_grade}</span>
                                                </div>
                                            </div>
                                            <div>
                                                <h2 className="text-2xl font-black italic uppercase tracking-tighter mb-1">Institutional Grade</h2>
                                                <p className="text-textMuted text-[10px] font-black uppercase tracking-widest italic">Blended High-Confidence Signal</p>
                                            </div>
                                        </div>

                                        <div className="text-center md:text-right">
                                            <div className="text-[10px] font-black uppercase tracking-widest text-textMuted mb-2 italic">Projected ROI</div>
                                            <div className={clsx(
                                                "text-5xl font-black italic leading-none drop-shadow-[0_0_15px_rgba(16,185,129,0.3)]",
                                                analysis.roi > 0 ? "text-brand-success" : "text-brand-danger"
                                            )}>
                                                {analysis.roi > 0 ? "+" : ""}{analysis.roi}%
                                            </div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-y md:divide-y-0 divide-white/5">
                                        <div className="p-8 group hover:bg-white/5 transition-colors">
                                            <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-2 italic">Win Probability</p>
                                            <div className="text-2xl font-black text-white">{analysis.win_rate}%</div>
                                        </div>
                                        <div className="p-8 group hover:bg-white/5 transition-colors">
                                            <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-2 italic">True Edge</p>
                                            <div className="text-2xl font-black text-brand-success">+{analysis.edge}%</div>
                                        </div>
                                        <div className="p-8 group hover:bg-white/5 transition-colors">
                                            <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-2 italic">Confidence</p>
                                            <div className="text-2xl font-black text-brand-primary italic">{analysis.confidence}</div>
                                        </div>
                                        <div className="p-8 group hover:bg-white/5 transition-colors">
                                            <p className="text-[9px] font-black text-textMuted uppercase tracking-widest mb-2 italic">Kelly Max</p>
                                            <div className="text-2xl font-black text-white">{(analysis.roi / 5).toFixed(2)}u</div>
                                        </div>
                                    </div>

                                    <div className="p-6 bg-white/5 border-t border-white/5">
                                        <div className="flex items-center gap-3 text-textMuted">
                                            <ShieldCheck size={18} className="text-brand-primary" />
                                            <p className="text-xs font-bold leading-relaxed">
                                                Matrix confidence is derived from <span className="text-white italic">10,000 algorithmic trials</span>. 
                                                Cross-market correlation indicates a <span className="text-brand-success italic">{analysis.confidence.toLowerCase()} strength</span> level.
                                            </p>
                                        </div>
                                    </div>
                                </motion.div>
                            ) : legs.length === 0 ? (
                                <motion.div 
                                    key="empty"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 rounded-3xl p-16 text-center border-dashed h-[450px] flex flex-col items-center justify-center"
                                >
                                    <div className="p-6 rounded-3xl bg-white/5 border border-white/5 mb-8">
                                        <Target className="text-textMuted/40" size={48} />
                                    </div>
                                    <h3 className="text-xl font-black italic uppercase tracking-tighter text-white mb-2">Build Your Slip</h3>
                                    <p className="text-textMuted text-sm font-bold max-w-sm mx-auto italic leading-relaxed mb-8">
                                        Add legs from the Props Board or Alpha Scanner.<br/>Begin your cross-market correlation analysis.
                                    </p>
                                    <button 
                                        onClick={() => handleAiBuild(true)}
                                        disabled={aiBuilding}
                                        className="bg-brand-primary hover:bg-brand-primary-hover text-white px-10 py-4 rounded-2xl font-black uppercase tracking-widest text-sm transition-all shadow-xl shadow-brand-primary/20 hover:scale-105 active:scale-95 flex items-center gap-2"
                                    >
                                        <Zap size={18} className={aiBuilding ? "animate-spin" : "fill-current"} />
                                        {aiBuilding ? "Generating Matrix..." : "AI BUILD PARLAY"}
                                    </button>
                                </motion.div>
                            ) : (
                                <motion.div 
                                    key="pending"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="bg-lucrix-surface/40 backdrop-blur-xl border border-white/10 p-16 rounded-3xl text-center h-[450px] flex flex-col items-center justify-center"
                                >
                                    <div className="p-6 rounded-3xl bg-white/5 border border-white/10 mb-8 animate-pulse">
                                        <BarChart3 size={48} className="text-brand-primary" />
                                    </div>
                                    <h3 className="text-2xl font-black italic uppercase tracking-tighter text-white mb-2">Analysis Required</h3>
                                    <p className="text-textMuted text-sm font-bold max-w-sm mx-auto italic mb-8 leading-relaxed">
                                        You have successfully added {legs.length} legs. Run the simulator to calculate true edge and correlation matrix.
                                    </p>
                                    <button 
                                        onClick={runAnalysis}
                                        className="bg-brand-primary hover:bg-brand-primary-hover text-white px-10 py-4 rounded-2xl font-black uppercase tracking-widest text-sm transition-all shadow-xl shadow-brand-primary/20 hover:scale-105 active:scale-95"
                                    >
                                        Execute Simulation Matrix
                                    </button>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <div className="lg:col-span-4 space-y-6">
                        <div className="bg-lucrix-surface/60 backdrop-blur-2xl border border-white/10 rounded-3xl p-6 shadow-2xl sticky top-24 overflow-hidden">
                            <div className="absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 bg-brand-primary/10 rounded-full blur-3xl opacity-50" />
                            
                            <div className="relative flex items-center justify-between mb-8 pb-4 border-b border-white/5">
                                <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-brand-primary inline-flex items-center gap-2">
                                    <CheckCircle2 size={12} className="text-brand-primary" /> Parlay Slip
                                </h2>
                                <span className="text-[9px] font-black uppercase text-textMuted italic">NEURAL v2.4</span>
                            </div>

                            <div className="space-y-4 mb-8 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                <AnimatePresence mode="popLayout">
                                    {legs.length === 0 ? (
                                        <motion.div 
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            className="py-20 text-center"
                                        >
                                            <p className="text-[10px] text-textMuted font-black uppercase tracking-widest italic opacity-50">
                                                Slip is Neutral...
                                            </p>
                                        </motion.div>
                                    ) : (
                                        legs.map((leg: any, i: number) => (
                                            <ParlayLegCard 
                                                key={leg.id || leg.prop_id} 
                                                leg={leg} 
                                                index={i} 
                                                onRemove={removeLeg} 
                                                onAiAdd={() => handleAiBuild(false)}
                                                aiLoading={aiBuilding}
                                            />
                                        ))
                                    )}
                                </AnimatePresence>
                            </div>

                            <div className="relative p-6 bg-white/5 rounded-2xl border border-white/5 space-y-6">
                                <div className="flex justify-between items-end">
                                    <div>
                                        <span className="text-[9px] font-black uppercase tracking-widest text-textMuted mb-2 block italic">Implied Alpha</span>
                                        <span className="text-3xl font-black italic text-brand-primary leading-none">
                                            {legs.length > 0 ? displayAmericanOdds : "---"}
                                        </span>
                                    </div>
                                    <div className="text-right">
                                        <span className="text-[9px] font-black uppercase tracking-widest text-textMuted mb-2 block italic">Confidence</span>
                                        <span className={clsx(
                                            "text-xs font-black italic",
                                            analysis ? "text-brand-primary" : "text-white/20"
                                        )}>
                                            {loading ? "CALC..." : (analysis?.confidence || "PENDING")}
                                        </span>
                                    </div>
                                </div>

                                <button
                                    onClick={runAnalysis}
                                    disabled={legs.length < 2 || loading}
                                    className={clsx(
                                        "w-full py-5 rounded-2xl font-black uppercase tracking-widest text-xs transition-all shadow-2xl",
                                        legs.length >= 2 && !loading 
                                            ? "bg-brand-primary text-white shadow-brand-primary/20 hover:bg-brand-primary-hover hover:scale-[1.02] active:scale-95" 
                                            : "bg-white/5 text-white/20 cursor-not-allowed border border-white/5"
                                    )}>
                                    {loading ? "Simulating..." : "Execute Simulation"}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </GateLock>
        </div>
    );
}
