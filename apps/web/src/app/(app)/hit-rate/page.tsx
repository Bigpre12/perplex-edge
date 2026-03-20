"use client";
import { useState, useEffect, Suspense } from "react";
import { api, isApiError } from "@/lib/api";
import { Loader2, TrendingUp, Users, Activity, Calendar, AreaChart, Filter, ChevronDown, ChevronUp, Info, Search } from "lucide-react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

import { useLucrixStore } from "@/store";
import SportSelector from "@/components/shared/SportSelector";
import { OutlierCard } from "@/components/hit-rate/OutlierCard";
import { OutlierFilterBar } from "@/components/hit-rate/OutlierFilterBar";
import { OutlierHero } from "@/components/hit-rate/OutlierHero";
import { OutlierLeaderboard } from "@/components/hit-rate/OutlierLeaderboard";

function HitRateContent() {
    const activeSport = useLucrixStore((state: any) => state.activeSport);
    const searchParams = useSearchParams();
    const router = useRouter();

    // Outlier Filters
    const [filters, setFilters] = useState({
        window: 10,
        min_hit_rate: 0.70,
        market: "all"
    });

    const [searchQuery, setSearchQuery] = useState("");
    const [outliers, setOutliers] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const handleFilterChange = (key: string, value: any) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    };

    useEffect(() => {
        async function fetchOutliers() {
            setLoading(true);
            try {
                const res = await api.hitRateOutliers({
                    sport: activeSport === "all" ? undefined : activeSport,
                    ...filters,
                    market: filters.market === "all" ? undefined : filters.market
                });

                if (!isApiError(res)) {
                    setOutliers(Array.isArray(res) ? res : []);
                } else {
                    setError("Failed to fetch outlier data.");
                }
            } catch (err) {
                setError("Outlier Engine currently updating.");
            } finally {
                setLoading(false);
            }
        }
        fetchOutliers();
    }, [activeSport, filters]);

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
                <div className="p-4 bg-brand-danger/10 border border-brand-danger/20 rounded-2xl text-brand-danger font-bold">
                    {error}
                </div>
                <button onClick={() => window.location.reload()} className="text-brand-cyan hover:underline text-sm font-black uppercase">
                    Retry Connection
                </button>
            </div>
        );
    }

    const filteredOutliers = outliers.filter(o => 
        o.player_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        o.market.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="p-4 md:p-6 text-white max-w-7xl mx-auto space-y-8 pb-32">
            {/* Nav / Sport Tabs */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-brand-cyan mb-2 flex items-center gap-2">
                        <Activity size={12} className="animate-pulse" />
                        Prop Intelligence
                    </h2>
                    <h1 className="text-4xl font-black tracking-tighter text-white uppercase font-display italic leading-none">
                        Outlier Props
                    </h1>
                </div>

                <div className="w-full md:w-auto">
                    <SportSelector />
                </div>
            </div>

            <OutlierHero count={filteredOutliers.length} lastSync="Live" />

            <div className="space-y-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/5 pb-4">
                    <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto">
                        <h2 className="text-xl font-black uppercase italic font-display text-white flex items-center gap-2 shrink-0">
                            <TrendingUp size={20} className="text-brand-success" />
                            Hot Streaks (70%+)
                        </h2>
                        <div className="relative w-full md:w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-textMuted" size={16} />
                            <input 
                                type="text"
                                placeholder="Search player or market..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-lucrix-surface border border-lucrix-border rounded-lg pl-10 pr-4 py-2 text-xs font-bold focus:border-brand-cyan outline-none transition-colors"
                            />
                        </div>
                    </div>
                    <OutlierFilterBar filters={filters} onChange={handleFilterChange} />
                </div>

                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[1, 2, 3, 4, 5, 6].map(i => (
                            <div key={i} className="h-64 bg-lucrix-surface border border-lucrix-border rounded-2xl animate-pulse" />
                        ))}
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {filteredOutliers.slice(0, 12).map((o, i) => (
                                <OutlierCard key={i} data={o} />
                            ))}
                        </div>

                        {filteredOutliers.length === 0 && (
                            <div className="py-24 text-center space-y-6 bg-lucrix-surface/30 rounded-3xl border border-dashed border-lucrix-border">
                                <div className="mx-auto size-20 bg-white/5 rounded-full flex items-center justify-center text-textMuted border border-white/10">
                                    <Search size={40} />
                                </div>
                                <div className="max-w-md mx-auto space-y-2">
                                    <h3 className="text-2xl font-black text-white italic uppercase font-display">No Outliers Found</h3>
                                    <p className="text-textMuted text-sm font-medium">
                                        No players currently matching these filters. Try lowering the hit rate threshold or expanding your sample window.
                                    </p>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>

            <div className="pt-12">
                <OutlierLeaderboard outliers={outliers} />
            </div>

            {/* Disclaimer */}
            <div className="mt-12 p-6 bg-lucrix-dark rounded-2xl border border-white/5 text-center">
                <p className="text-[10px] text-textMuted font-bold uppercase tracking-widest leading-relaxed">
                    Data based on historical game results and settled book lines. Past performance does not guarantee future results. 
                    Always gamble responsibly. Intel updated every 5 minutes.
                </p>
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
