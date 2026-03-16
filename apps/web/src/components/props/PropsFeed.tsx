'use client';

import { useEffect, useState } from 'react';
import { api, API, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';
import { useLucrixStore } from "@/store";
import { PropCard, PropData } from './PropCard';
import { SkeletonGrid } from '../SkeletonCard';
import PropsEmptyState from '../PropsEmptyState';

export default function PropsFeed({ sport }: { sport: SportKey }) {
    const [props, setProps] = useState<PropData[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<'all' | 'sharp' | 'top'>('all');
    const { backendOnline } = useLucrixStore();

    useEffect(() => {
        if (!backendOnline) return;
        let isMounted = true;

        const load = async () => {
            try {
                // We use the new consolidated props endpoint
                const res = await api.get<any>(API.props(sport));

                if (isMounted && !isApiError(res)) {
                    // Normalize backend data to PropData interface if needed
                    const rawProps = Array.isArray(res) ? res : res.props || [];
                    const normalized: PropData[] = rawProps.map((p: any) => ({
                        id: p.id || p.prop_id || `${p.player_name}-${p.stat_type}`,
                        player_name: p.player_name || p.player || 'Unknown',
                        team: p.team || 'N/A',
                        stat_type: p.stat_type || p.stat || 'prop',
                        line: p.line || p.line_value || 0,
                        side: p.side || 'over',
                        odds: p.odds || 0,
                        grade: p.grade || 'C',
                        hit_rates: {
                            total: p.hit_rate || 0,
                            l5: p.l5_hit_rate || p.hit_rate || 0,
                            l10: p.l10_hit_rate || p.hit_rate || 0,
                            l20: p.l20_hit_rate || p.hit_rate || 0,
                        },
                        books: p.books || {},
                        is_sharp: p.is_sharp || p.sharp || false,
                        steam_score: p.steam_score || 0,
                        ev_percent: p.ev_percent || p.edge || 0,
                    }));
                    setProps(normalized);
                }
            } catch (err) {
                console.error("[PropsFeed] Error loading props:", err);
            } finally {
                if (isMounted) setLoading(false);
            }
        };

        load();
        const interval = setInterval(load, 20000); // 20s refresh
        return () => {
            isMounted = false;
            clearInterval(interval);
        };
    }, [sport, backendOnline]);

    const filtered = props.filter(p => {
        if (filter === 'sharp') return p.is_sharp || (p.steam_score ?? 0) > 5;
        if (filter === 'top') return ['S', 'A', 'Elite', 'Good'].includes(p.grade);
        return true;
    });

    if (loading && props.length === 0) {
        return <SkeletonGrid count={6} />;
    }

    if (props.length === 0 && !loading) {
        return <PropsEmptyState sport={sport} />;
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-lucrix-surface p-4 rounded-xl border border-lucrix-border shadow-card">
                <div className="flex items-center gap-3">
                    <div className="w-2 h-8 bg-brand-cyan rounded-full shadow-glow shadow-brand-cyan/40" />
                    <div>
                        <h2 className="text-xl font-black text-white italic uppercase tracking-tighter font-display">Market Pulse</h2>
                        <p className="text-[10px] text-textMuted font-bold uppercase tracking-widest">{filtered.length} Live Opportunities</p>
                    </div>
                </div>

                <div className="flex items-center gap-2 bg-lucrix-dark p-1 rounded-lg border border-lucrix-border">
                    {(['all', 'sharp', 'top'] as const).map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-4 py-1.5 rounded-md text-[10px] font-black uppercase tracking-widest transition-all ${filter === f
                                ? 'bg-brand-cyan text-black shadow-glow shadow-brand-cyan/30'
                                : 'text-textSecondary hover:text-white'
                                }`}
                        >
                            {f === 'sharp' ? '🐋 SHARP' : f === 'top' ? '⭐ ELITE' : 'ALL'}
                        </button>
                    ))}
                </div>
            </div>

            {filtered.length === 0 ? (
                <div className="text-center py-20 bg-lucrix-dark/50 rounded-2xl border border-dashed border-lucrix-border backdrop-blur-sm">
                    <div className="text-3xl mb-4">🔦</div>
                    <h3 className="text-sm font-black text-white uppercase tracking-tighter italic">No Matches Found</h3>
                    <p className="text-[10px] text-textMuted font-bold uppercase tracking-widest mt-2">
                        Try adjusting your filters for the current slate.
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {filtered.map(prop => (
                        <PropCard key={prop.id} prop={prop} />
                    ))}
                </div>
            )}
        </div>
    );
}
