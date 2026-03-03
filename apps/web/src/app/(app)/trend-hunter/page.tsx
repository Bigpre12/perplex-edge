"use client";

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Zap, Search, Bell, ChevronDown, Filter, BarChart3, Database } from 'lucide-react';
import { API_BASE_URL } from '@/lib/apiConfig';
import { TrendCard } from '@/components/TrendHunter/TrendCard';
import { EmptyState } from '@/components/ui/EmptyState';

const SPORTS_LIST = [
    { id: 'basketball_nba', name: 'NBA', icon: '🏀' },
    { id: 'americanfootball_nfl', name: 'NFL', icon: '🏈' },
    { id: 'icehockey_nhl', name: 'NHL', icon: '🏒' },
    { id: 'baseball_mlb', name: 'MLB', icon: '⚾' },
    { id: 'soccer_usa_mls', name: 'Soccer', icon: '⚽' },
];

const STAT_CATEGORIES = ['Popular', 'Points', 'Rebounds', 'Assists', '3-Pointers'];

function TrendHunterContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const activeSport = searchParams.get('sport') || 'basketball_nba';

    const [timeframe, setTimeframe] = useState('10g');
    const [statFilter, setStatFilter] = useState('Popular');
    const [sortBy, setSortBy] = useState('Hit Rate');
    const [trends, setTrends] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchTrends = async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE_URL}/api/trends/hit-rates?sport_key=${activeSport}&timeframe=${timeframe}`);
            const data = await res.json();
            setTrends(data.items || []);
        } catch (err) {
            console.error("Failed to fetch trends", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTrends();
    }, [activeSport, timeframe]);

    const handleSportChange = (sportId: string) => {
        const params = new URLSearchParams(searchParams);
        params.set('sport', sportId);
        router.push(`/trend-hunter?${params.toString()}`);
    };

    // Derived filtering based on stat category
    const filteredTrends = trends.filter(t => {
        if (statFilter === 'Popular') return true;
        if (statFilter === '3-Pointers' && t.stat_type.includes('3PT')) return true;
        return t.stat_type.toLowerCase().includes(statFilter.toLowerCase().replace('s', ''));
    });

    return (
        <div className="min-h-screen bg-[#0F1115] text-gray-100">
            {/* Sticky Sub-nav */}
            <nav className="sticky top-0 z-40 bg-[#181B21] border-b border-gray-800 shadow-xl overflow-hidden">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex space-x-8 py-3 overflow-x-auto scrollbar-hide no-scrollbar">
                        {SPORTS_LIST.map((sport) => (
                            <button
                                key={sport.id}
                                onClick={() => handleSportChange(sport.id)}
                                className={`flex items-center space-x-2 pb-2 -mb-3 transition-all whitespace-nowrap border-b-2 font-bold text-sm ${activeSport === sport.id
                                        ? 'text-primary border-primary'
                                        : 'text-gray-500 border-transparent hover:text-gray-300'
                                    }`}
                            >
                                <span className="text-xs">{sport.icon}</span>
                                <span>{sport.name}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Search & Filter Bar */}
                <div className="flex flex-col md:flex-row gap-4 mb-8 items-start md:items-center justify-between">
                    <div className="flex flex-wrap gap-2">
                        {STAT_CATEGORIES.map((cat) => (
                            <button
                                key={cat}
                                onClick={() => setStatFilter(cat)}
                                className={`px-5 py-2 rounded-full text-xs font-black uppercase tracking-widest transition-all ${statFilter === cat
                                        ? 'bg-primary text-white shadow-[0_0_15px_rgba(16,185,129,0.3)]'
                                        : 'bg-[#181B21] border border-gray-800 text-gray-400 hover:border-gray-600'
                                    }`}
                            >
                                {cat}
                            </button>
                        ))}
                    </div>

                    <div className="flex items-center gap-4 w-full md:w-auto">
                        <div className="flex bg-[#141424] p-1 rounded-xl border border-gray-800">
                            {['5g', '10g', '30g'].map((t) => (
                                <button
                                    key={t}
                                    onClick={() => setTimeframe(t)}
                                    className={`px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all ${timeframe === t
                                            ? 'bg-primary text-white shadow-lg'
                                            : 'text-gray-500 hover:text-white'
                                        }`}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>

                        <div className="flex items-center text-[10px] font-black uppercase tracking-widest text-gray-500 gap-2 ml-auto">
                            <span>Sort By:</span>
                            <div className="flex items-center gap-1 text-white cursor-pointer hover:text-primary transition-colors">
                                {sortBy} <ChevronDown size={14} />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Grid */}
                {loading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {Array(6).fill(0).map((_, i) => (
                            <div key={i} className="h-64 bg-[#181B21] animate-pulse rounded-2xl border border-gray-800" />
                        ))}
                    </div>
                ) : filteredTrends.length > 0 ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                    >
                        <AnimatePresence mode="popLayout">
                            {filteredTrends.map((trend) => (
                                <TrendCard key={trend.id} trend={trend} />
                            ))}
                        </AnimatePresence>
                    </motion.div>
                ) : (
                    <EmptyState
                        title="No Trends Found"
                        description={`We couldn't find any players hitting over 50% for ${statFilter} in ${activeSport}. try another filter.`}
                    />
                )}
            </main>

            {/* Premium Stats Footer */}
            <div className="fixed bottom-0 left-0 right-0 bg-[#0F1115]/80 backdrop-blur-md border-t border-gray-800/50 py-3 px-6 z-30">
                <div className="max-w-7xl mx-auto flex items-center justify-between text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5 text-emerald-500">
                            <span className="flex size-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            Live Market Data
                        </div>
                        <div className="hidden sm:flex items-center gap-1.5">
                            <Database size={10} />
                            Source: BallDontLie v1 API
                        </div>
                    </div>
                    <div>
                        LUCRIX Institutional Grade Analytics
                    </div>
                </div>
            </div>

            <style jsx global>{`
                .no-scrollbar::-webkit-scrollbar {
                    display: none;
                }
                .no-scrollbar {
                    -ms-overflow-style: none;
                    scrollbar-width: none;
                }
            `}</style>
        </div>
    );
}

export default function TrendHunterPage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center py-20 min-h-screen bg-[#0F1115]">
                <Zap className="text-primary animate-pulse mb-4" size={48} />
                <p className="text-gray-500 text-sm font-black uppercase tracking-[0.3em]">Institutional Scan Active...</p>
            </div>
        }>
            <TrendHunterContent />
        </Suspense>
    );
}
