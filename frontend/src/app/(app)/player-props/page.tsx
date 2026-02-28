"use client";

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useBrainData } from '@/hooks/useBrainData';
import { API_ENDPOINTS } from "@/lib/apiConfig";
import { getAuthToken } from '@/lib/auth';
import { PropCard } from '@/components/props/PropCard';
import { FilterBar } from '@/components/props/FilterBar';
import { PropSkeleton } from '@/components/ui/PropSkeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import { Search } from 'lucide-react';

function PlayerPropsContent() {
    const searchParams = useSearchParams();
    const activeSport = searchParams.get('sport') || 'basketball_nba';

    const [props, setProps] = useState<any[]>([]);
    const [isLoadingPicks, setIsLoadingPicks] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [userTier, setUserTier] = useState<string>('free');

    const { marketIntel } = useBrainData(activeSport);

    const fetchProps = async (sport: string) => {
        setIsLoadingPicks(true);
        const token = getAuthToken();
        try {
            const res = await fetch(`${API_ENDPOINTS.ODDS}?sport_key=${sport}&limit=50`, {
                headers: {
                    ...(token ? { "Authorization": `Bearer ${token}` } : {})
                }
            });
            const data = await res.json();
            if (data.tier) setUserTier(data.tier);
            if (data.items && data.items.length > 0) {
                setProps(data.items);
            } else {
                setProps([]);
            }
        } catch (err) {
            console.error("Failed to fetch props:", err);
            setProps([]);
        } finally {
            setIsLoadingPicks(false);
        }
    };

    useEffect(() => {
        fetchProps(activeSport);

        const ws = new WebSocket(API_ENDPOINTS.WS_ODDS);
        ws.onopen = () => console.log("🚀 Connected to Live EV Engine Stream");
        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                if (message.type === 'LIVE_EV_UPDATE' && message.data?.items) {
                    setProps(message.data.items);
                }
            } catch (err) {
                console.error("WebSocket Message Error:", err);
            }
        };
        return () => ws.close();
    }, [activeSport]);

    const filteredProps = props.filter(p =>
        (p.player?.name || p.player_name || '').toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="px-4 pb-20 max-w-7xl mx-auto">
            {/* Header & Search */}
            <div className="flex flex-col gap-4 mb-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-black tracking-tight text-white mb-1 uppercase italic">Pick Intel</h1>
                        <p className="text-[10px] text-[#6B7280] font-black uppercase tracking-widest flex items-center gap-2">
                            <span className="size-1.5 rounded-full bg-[#22C55E] animate-pulse" /> Live Market Feed
                        </p>
                    </div>
                    {/* Search - Mobile compact */}
                    <div className="relative group max-w-[160px] sm:max-w-xs w-full">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#6B7280] group-focus-within:text-[#F5C518]">
                            <Search size={14} />
                        </div>
                        <input
                            type="text"
                            placeholder="Search player..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full bg-[#141424] border border-[#1E1E35] text-white text-xs rounded-full focus:ring-1 focus:ring-[#F5C518] focus:border-[#F5C518] block pl-9 py-2.5 transition-all outline-none"
                        />
                    </div>
                </div>

                {/* Filter Bar */}
                <FilterBar />
            </div>

            {/* Content Area */}
            {isLoadingPicks ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Array(9).fill(0).map((_, i) => <PropSkeleton key={i} />)}
                </div>
            ) : filteredProps.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 items-start">
                    {filteredProps.map((prop, idx) => (
                        <PropCard
                            key={`${prop.id}-${idx}`}
                            prop={{
                                ...prop,
                                player: prop.player || { name: prop.player_name, position: prop.position || 'N/A' },
                                market: prop.market || { stat_type: prop.stat_type },
                                line_value: prop.line_value || prop.line,
                                side: prop.side || 'over',
                                odds: prop.odds || -110,
                                display_edge: prop.display_edge || prop.edge || 0,
                                model_probability: prop.model_probability || prop.confidence_score || 0,
                                confidence_score: prop.confidence_score || 0,
                                kelly_units: prop.kelly_units || 0
                            }}
                            tier={userTier}
                        />
                    ))}
                </div>
            ) : (
                <EmptyState onReset={() => setSearchQuery('')} />
            )}
        </div>
    );
}

export default function PlayerProps() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center py-20">
                <div className="animate-bounce text-[#F5C518] text-2xl mb-4">🎯</div>
                <p className="text-[#6B7280] text-sm">Aggregating quantum props...</p>
            </div>
        }>
            <PlayerPropsContent />
        </Suspense>
    );
}
