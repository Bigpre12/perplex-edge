"use client";
import { useState, useEffect } from "react";
import { api, isApiError } from "@/lib/api";
import { HitRateLight } from "@/components/HitRateLight";
import { Loader2, TrendingUp, Users, Activity, Calendar } from "lucide-react";

import { Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";

interface SummaryData {
    sport: string;
    overall_hit_rate: number;
    sample_size: number;
    last_updated: string;
}

interface PlayerHitRate {
    player: string;
    prop_type: string;
    hit_rate: number;
    sample_size: number;
    streak: string;
}

function HitRateContent() {
    const searchParams = useSearchParams();
    const router = useRouter();

    // Initialize from URL or default to all
    const initialSport = searchParams.get("sport") || "all";

    const [summary, setSummary] = useState<SummaryData | null>(null);
    const [players, setPlayers] = useState<PlayerHitRate[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [sport, setSport] = useState(initialSport);
    const [slateOnly, setSlateOnly] = useState(false);

    // Sync sport state with URL
    useEffect(() => {
        const currentSport = searchParams.get("sport") || "all";
        if (currentSport !== sport) {
            setSport(currentSport);
        }
    }, [searchParams, sport]);

    const handleSportChange = (newSport: string) => {
        setSport(newSport);
        const params = new URLSearchParams(searchParams.toString());
        params.set("sport", newSport);
        router.push(`/hit-rate?${params.toString()}`);
    };

    useEffect(() => {
        async function fetchData() {
            setLoading(true);
            setError(null);
            try {
                const [summaryRes, playersRes] = await Promise.all([
                    api.hitRateSummary(sport),
                    api.hitRateByPlayer(sport, slateOnly)
                ]);

                if (!isApiError(summaryRes)) setSummary(summaryRes);
                if (!isApiError(playersRes)) setPlayers(Array.isArray(playersRes) ? playersRes : []);
            } catch (err) {
                console.error("Failed to fetch hit rate data:", err);
                setError("Failed to load hit rate analytics.");
            } finally {
                setLoading(false);
            }
        }
        fetchData();
    }, [sport, slateOnly]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
                <Loader2 className="w-12 h-12 text-emerald-500 animate-spin" />
                <p className="text-gray-400 font-medium animate-pulse">Analyzing performance data...</p>
            </div>
        );
    }

    return (
        <div className="p-6 text-white max-w-7xl mx-auto space-y-8 pb-24 animate-in fade-in duration-700">
            {/* Header section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="space-y-1">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                        Historical Hit Rate
                    </h1>
                    <p className="text-gray-400 text-sm flex items-center gap-2">
                        <Activity className="w-4 h-4 text-emerald-500" />
                        Live tracking for {sport === 'all' ? 'Global Market' : sport.replace('basketball_', '').replace('americanfootball_', '').replace('icehockey_', '').toUpperCase()}
                    </p>
                </div>

                <div className="flex items-center gap-4 bg-white/5 p-2 rounded-2xl border border-white/10 backdrop-blur-xl">
                    {/* Slate Toggle */}
                    <button
                        onClick={() => setSlateOnly(!slateOnly)}
                        className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${slateOnly
                            ? "bg-emerald-500 text-black shadow-lg shadow-emerald-500/20"
                            : "bg-transparent text-gray-400 hover:text-white"
                            }`}
                    >
                        <Calendar className="w-4 h-4" />
                        {slateOnly ? "Live Slate: On" : "Show All Data"}
                    </button>

                    <div className="h-6 w-px bg-white/10" />

                    <select
                        value={sport}
                        onChange={(e) => handleSportChange(e.target.value)}
                        aria-label="Select sport"
                        className="bg-transparent text-xs font-bold text-gray-300 outline-none cursor-pointer hover:text-white transition-colors"
                    >
                        <option value="all" className="bg-zinc-900">All Sports</option>
                        <option value="basketball_nba" className="bg-zinc-900">NBA Basketball</option>
                        <option value="basketball_ncaab" className="bg-zinc-900">NCAAB</option>
                        <option value="americanfootball_nfl" className="bg-zinc-900">NFL Football</option>
                        <option value="icehockey_nhl" className="bg-zinc-900">NHL Hockey</option>
                    </select>
                </div>
            </div>

            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm">
                    {error}
                </div>
            )}

            {/* Top Level Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-b from-white/10 to-transparent p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                        <TrendingUp className="w-16 h-16 text-emerald-500" />
                    </div>
                    <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Overall Accuracy</p>
                    <h2 className="text-4xl font-black mt-2 text-emerald-400">
                        {summary?.overall_hit_rate}%
                    </h2>
                    <p className="text-gray-500 text-xs mt-2 italic">Based on {sport === 'all' ? 'all' : ''} settled graded props</p>
                </div>

                <div className="bg-gradient-to-b from-white/10 to-transparent p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                        <Calendar className="w-16 h-16 text-blue-500" />
                    </div>
                    <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Sample Size</p>
                    <h2 className="text-4xl font-black mt-2 text-blue-400">
                        {summary?.sample_size}
                    </h2>
                    <p className="text-gray-500 text-xs mt-2">Props graded since last reset</p>
                </div>

                <div className="bg-gradient-to-b from-white/10 to-transparent p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 transition-transform">
                        <Users className="w-16 h-16 text-purple-500" />
                    </div>
                    <p className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Player Coverage</p>
                    <h2 className="text-4xl font-black mt-2 text-purple-400">
                        {players.length}
                    </h2>
                    <p className="text-gray-500 text-xs mt-2">Unique players in filtered dataset</p>
                </div>
            </div>

            {/* Players Table */}
            <div className="space-y-4">
                <div className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-gray-400" />
                    <h2 className="text-xl font-bold">Per-Player Breakdown</h2>
                </div>

                <div className="bg-zinc-900/50 rounded-2xl border border-white/5 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-white/5 bg-white/5">
                                    <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Player</th>
                                    <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Market</th>
                                    <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Streak</th>
                                    <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-widest text-center">Hit Rate</th>
                                    <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-widest text-right">Sample</th>
                                </tr>
                            </thead>
                            <tbody>
                                {players.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} className="p-12 text-center text-gray-500">
                                            {slateOnly ? "No players from today's slate found in historical data." : "No player specific data settled yet."}
                                        </td>
                                    </tr>
                                ) : (
                                    players.map((p, idx) => (
                                        <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                                            <td className="p-4">
                                                <div className="font-bold text-white group-hover:text-emerald-400 transition-colors">
                                                    {p.player}
                                                </div>
                                            </td>
                                            <td className="p-4">
                                                <span className="px-2 py-1 bg-white/5 border border-white/10 rounded text-[10px] font-mono text-gray-400">
                                                    {p.prop_type}
                                                </span>
                                            </td>
                                            <td className="p-4">
                                                <span className={`text-xs font-bold ${p.streak.includes('0/') ? 'text-red-400' : 'text-emerald-400'
                                                    }`}>
                                                    {p.streak}
                                                </span>
                                            </td>
                                            <td className="p-4 flex justify-center">
                                                <HitRateLight hitRate={p.hit_rate / 100} size="sm" label="" />
                                            </td>
                                            <td className="p-4 text-right text-gray-400 font-mono text-sm">
                                                {p.sample_size}G
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function HitRatePage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
                <Loader2 className="w-12 h-12 text-emerald-500 animate-spin" />
                <p className="text-gray-400 font-medium">Loading Hit Rate Engine...</p>
            </div>
        }>
            <HitRateContent />
        </Suspense>
    );
}
