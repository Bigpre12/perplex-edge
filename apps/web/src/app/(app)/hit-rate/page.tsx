"use client";
import { useState, useEffect, Suspense } from "react";
import { api, isApiError } from "@/lib/api";
import { Loader2, TrendingUp, Users, Activity, Calendar, AreaChart, Filter, ChevronDown, ChevronUp, Info } from "lucide-react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

import { PerformanceSummary } from "@/components/hit-rate/PerformanceSummary";
import { PerformanceChart } from "@/components/hit-rate/PerformanceChart";

interface SummaryData {
    overall_hit_rate: number;
    roi: number;
    graded_picks: number;
    streak: string;
    status: string;
    last_updated: string;
}

interface PlayerPerformance {
    player: string;
    prop_type: string;
    hit_rate: number;
    sample_size: number;
    confidence_badge: string;
    streak: string;
}

function ConfidenceBadge({ tier }: { tier: string }) {
    const styles: Record<string, string> = {
        "High Confidence": "bg-brand-success/10 text-brand-success border-brand-success/30 shadow-brand-success/10",
        "Reliable": "bg-brand-cyan/10 text-brand-cyan border-brand-cyan/30 shadow-brand-cyan/10",
        "Early Read": "bg-brand-warning/10 text-brand-warning border-brand-warning/30 shadow-brand-warning/10",
        "Limited Sample": "bg-white/5 text-textMuted border-white/10"
    };
    
    return (
        <span className={`px-2 py-0.5 rounded-sm border text-[9px] font-black uppercase tracking-widest shadow-sm ${styles[tier] || styles["Limited Sample"]}`}>
            {tier}
        </span>
    );
}

function HitRateContent() {
    const searchParams = useSearchParams();
    const router = useRouter();

    const initialSport = searchParams.get("sport") || "all";
    const [sport, setSport] = useState(initialSport);
    const [slateOnly, setSlateOnly] = useState(false);
    const [showLimited, setShowLimited] = useState(false);
    
    const [summary, setSummary] = useState<SummaryData | null>(null);
    const [players, setPlayers] = useState<PlayerPerformance[]>([]);
    const [trends, setTrends] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isTableExpanded, setIsTableExpanded] = useState(true);

    const handleSportChange = (newSport: string) => {
        setSport(newSport);
        const params = new URLSearchParams(searchParams.toString());
        params.set("sport", newSport);
        router.push(`/hit-rate?${params.toString()}`);
    };

    useEffect(() => {
        async function fetchData() {
            setLoading(true);
            try {
                const [summaryRes, playersRes, trendsRes] = await Promise.all([
                    api.hitRateSummary(sport),
                    api.hitRateByPlayer(sport, slateOnly),
                    api.hitRateTrends(sport)
                ]);

                if (!isApiError(summaryRes)) setSummary(summaryRes);
                if (!isApiError(playersRes)) setPlayers(Array.isArray(playersRes) ? playersRes : []);
                if (!isApiError(trendsRes)) setTrends(Array.isArray(trendsRes) ? trendsRes : []);
            } catch (err) {
                setError("Performance Engine currently updating.");
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [sport, slateOnly]);

    const filteredPlayers = players.filter(p => showLimited || p.sample_size >= 10);
    const topPerformers = players.filter(p => p.sample_size >= 15).slice(0, 3);

    return (
        <div className="p-6 text-white max-w-7xl mx-auto space-y-10 pb-24">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 pt-4">
                <div className="space-y-1">
                    <h1 className="text-4xl font-black tracking-tight text-white uppercase font-display italic leading-none">Performance</h1>
                    <div className="flex items-center gap-3">
                        <span className="size-1.5 rounded-full bg-brand-success animate-pulse shadow-glow shadow-brand-success/50" />
                        <p className="text-[10px] text-textMuted font-black uppercase tracking-[0.2em]">
                            Verifiable Track Record • {sport === 'all' ? 'GLOBAL' : sport.toUpperCase()}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-3 bg-lucrix-surface p-1.5 rounded-xl border border-lucrix-border shadow-inner">
                    <button
                        onClick={() => setSlateOnly(!slateOnly)}
                        className={`px-4 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${slateOnly
                            ? "bg-brand-purple text-white shadow-glow shadow-brand-purple/20"
                            : "text-textMuted hover:text-white"
                            }`}
                    >
                        {slateOnly ? "Live Slate" : "All Historical"}
                    </button>
                    <div className="w-px h-4 bg-lucrix-border" />
                    <select
                        value={sport}
                        onChange={(e) => handleSportChange(e.target.value)}
                        className="bg-transparent text-[10px] font-black uppercase tracking-widest text-white px-2 py-2 outline-none cursor-pointer"
                    >
                        <option value="all" className="bg-lucrix-dark">All Markets</option>
                        <option value="basketball_nba" className="bg-lucrix-dark">NBA</option>
                        <option value="americanfootball_nfl" className="bg-lucrix-dark">NFL</option>
                        <option value="icehockey_nhl" className="bg-lucrix-dark">NHL</option>
                    </select>
                </div>
            </div>

            {/* Hero Metrics */}
            <PerformanceSummary 
                winRate={summary?.overall_hit_rate || 0}
                roi={summary?.roi || 0}
                gradedPicks={summary?.graded_picks || 0}
                streak={summary?.streak || "0/0"}
                loading={loading}
            />

            {/* Analysis Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* Trend Chart (Above fold) */}
                <div className="lg:col-span-8">
                    <PerformanceChart data={trends} loading={loading} />
                </div>

                {/* Top Performers (Above fold) */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 shadow-card h-full flex flex-col">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-sm font-black text-white uppercase tracking-widest font-display italic">Top Performers</h3>
                            <Users size={16} className="text-brand-cyan" />
                        </div>

                        <div className="space-y-4 flex-1">
                            {topPerformers.length > 0 ? topPerformers.map((p, i) => (
                                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-lucrix-dark/30 border border-lucrix-border/50 hover:border-brand-cyan/30 transition-all">
                                    <div>
                                        <p className="text-xs font-black text-white uppercase">{p.player}</p>
                                        <p className="text-[9px] text-textMuted font-bold uppercase">{p.prop_type}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-black text-brand-success">{p.hit_rate}%</p>
                                        <p className="text-[8px] text-textMuted font-black uppercase">{p.sample_size} GRADES</p>
                                    </div>
                                </div>
                            )) : (
                                <div className="h-full flex flex-col items-center justify-center py-10 opacity-40">
                                    <Activity size={32} className="mb-2" />
                                    <p className="text-[9px] font-black uppercase tracking-tighter">Awaiting Performance Data</p>
                                </div>
                            )}
                        </div>
                        
                        <div className="mt-6 pt-4 border-t border-lucrix-border">
                            <button 
                                onClick={() => setIsTableExpanded(!isTableExpanded)}
                                className="w-full text-center text-[10px] font-black uppercase tracking-[.2em] text-brand-cyan hover:text-white transition-all flex items-center justify-center gap-2"
                            >
                                {isTableExpanded ? "Collapsing Details" : "Expand Full Log"}
                                {isTableExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Detailed Performance Table (Below fold) */}
            <AnimatePresence>
                {isTableExpanded && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="space-y-4"
                    >
                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                            <div className="flex items-center gap-2">
                                <Filter size={18} className="text-textSecondary" />
                                <h2 className="text-lg font-black text-white uppercase font-display italic">Detailed Performance Log</h2>
                            </div>
                            
                            <div className="flex items-center gap-3">
                                <button 
                                    onClick={() => setShowLimited(!showLimited)}
                                    className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest border transition-all ${showLimited ? 'bg-white/10 border-white/20 text-white' : 'bg-transparent border-white/5 text-textMuted'}`}
                                >
                                    {showLimited ? "Showing All Samples" : "Hide Limited Samples"}
                                </button>
                                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-lucrix-dark/50 border border-lucrix-border rounded-lg">
                                    <Info size={12} className="text-brand-cyan" />
                                    <span className="text-[9px] font-bold text-textSecondary uppercase tracking-tighter">Confidence based on volume</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl overflow-hidden shadow-card">
                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="bg-lucrix-dark/50 border-b border-lucrix-border">
                                            <th className="p-4 text-[10px] font-black text-textMuted uppercase tracking-widest">Top Performers</th>
                                            <th className="p-4 text-[10px] font-black text-textMuted uppercase tracking-widest">Market</th>
                                            <th className="p-4 text-[10px] font-black text-textMuted uppercase tracking-widest">Confidence</th>
                                            <th className="p-4 text-[10px] font-black text-textMuted uppercase tracking-widest text-center">Accuracy</th>
                                            <th className="p-4 text-[10px] font-black text-textMuted uppercase tracking-widest text-right">Graded Picks</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-lucrix-border/50">
                                        {filteredPlayers.length > 0 ? filteredPlayers.map((p, idx) => (
                                            <tr key={idx} className="hover:bg-white/[0.02] transition-colors group">
                                                <td className="p-4 font-black text-white group-hover:text-brand-cyan transition-colors uppercase text-xs">
                                                    {p.player}
                                                </td>
                                                <td className="p-4">
                                                    <span className="text-[10px] font-mono text-textSecondary uppercase bg-lucrix-dark/50 px-2 py-1 rounded border border-lucrix-border">
                                                        {p.prop_type}
                                                    </span>
                                                </td>
                                                <td className="p-4">
                                                    <ConfidenceBadge tier={p.confidence_badge} />
                                                </td>
                                                <td className="p-4 text-center">
                                                    <div className="flex flex-col items-center">
                                                        <span className={`text-sm font-black ${p.hit_rate >= 55 ? 'text-brand-success' : 'text-white'}`}>
                                                            {p.hit_rate}%
                                                        </span>
                                                        <div className="w-12 h-1 bg-lucrix-dark overflow-hidden rounded-full mt-1">
                                                            <div 
                                                                className={`h-full ${p.hit_rate >= 55 ? 'bg-brand-success' : 'bg-brand-cyan'}`} 
                                                                style={{ width: `${p.hit_rate}%` }} 
                                                            />
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="p-4 text-right">
                                                    <span className="text-xs font-mono font-bold text-textSecondary">{p.sample_size}G</span>
                                                </td>
                                            </tr>
                                        )) : (
                                            <tr>
                                                <td colSpan={5} className="p-20 text-center">
                                                    <div className="flex flex-col items-center gap-3 opacity-50">
                                                        <Activity size={40} className="text-textMuted" />
                                                        <p className="text-xs font-black uppercase tracking-widest">Performance will appear after picks are graded</p>
                                                        <p className="text-[10px] font-bold text-textMuted uppercase">Need at least 10 graded picks for a reliable read</p>
                                                    </div>
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Metric Definitions */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 pt-10 opacity-60 grayscale hover:grayscale-0 hover:opacity-100 transition-all">
                {[
                    { label: "Win Rate", desc: "Percent of graded picks that won." },
                    { label: "ROI", desc: "Profit efficiency over graded picks." },
                    { label: "Graded Picks", desc: "Picks with verifiable settled outcomes." },
                    { label: "Confidence", desc: "How trustworthy the trend is based on volume." }
                ].map(item => (
                    <div key={item.label} className="space-y-1">
                        <p className="text-[10px] font-black text-white uppercase tracking-widest">{item.label}</p>
                        <p className="text-[9px] text-textMuted font-bold uppercase leading-relaxed tracking-tight">{item.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function HitRatePage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
                <Loader2 className="w-12 h-12 text-brand-cyan animate-spin" />
                <p className="text-[10px] font-black text-textMuted uppercase tracking-widest animate-pulse">Engaging Analytics Matrix...</p>
            </div>
        }>
            <HitRateContent />
        </Suspense>
    );
}
