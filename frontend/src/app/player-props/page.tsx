"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Download, ChevronDown, Brain, Star, History, Loader2, Search } from 'lucide-react';
import { SPORTS } from '@/utils/sportUtils';
import { useBrainData } from '@/hooks/useBrainData';
import TrendChart from '@/components/TrendChart';
import MatchupIntelligence from '@/components/MatchupIntelligence';
import SportsbookDeeplinks from '@/components/SportsbookDeeplinks';
import PlayerTrendsModal from '@/components/PlayerTrendsModal';
import { HitRateStack } from '@/components/HitRateLight';
import { getAuthToken } from '@/lib/auth';
import BetSlipShare from '@/components/BetSlipShare';
import { API_BASE_URL, API_ENDPOINTS } from "@/lib/apiConfig";

const AVAILABLE_BOOKS = [
    { key: 'fanduel', name: 'FanDuel' },
    { key: 'draftkings', name: 'DraftKings' },
    { key: 'prizepicks', name: 'PrizePicks' },
    { key: 'underdog', name: 'Underdog' },
    { key: 'betrivers', name: 'BetRivers' },
    { key: 'caesars', name: 'Caesars' },
    { key: 'betmgm', name: 'BetMGM' }
];

export default function PlayerProps() {
    const [expandedRow, setExpandedRow] = useState<number | null>(null);
    const [activeSport, setActiveSport] = useState('basketball_nba');
    const [props, setProps] = useState<any[]>([]);
    const [isLoadingPicks, setIsLoadingPicks] = useState(true);
    const [selectedPropForModal, setSelectedPropForModal] = useState<any>(null);
    const [selectedBooks, setSelectedBooks] = useState<string[]>(AVAILABLE_BOOKS.map(b => b.key));
    const [searchQuery, setSearchQuery] = useState('');
    const [sortColumn, setSortColumn] = useState<'edge' | 'odds' | 'player'>('edge');
    const [sortDirection, setSortDirection] = useState<'desc' | 'asc'>('desc');

    const { marketIntel, decisions } = useBrainData(activeSport);

    const fetchProps = async (sport: string) => {
        setIsLoadingPicks(true);
        try {
            const res = await fetch(`${API_BASE_URL}/immediate/working-player-props?sport_key=${sport}&limit=50`);
            const data = await res.json();

            if (data.items && data.items.length > 0) {
                setProps(data.items);
            } else {
                // FALLBACK: use validation picks when slate is empty
                const fallbackRes = await fetch(`${API_BASE_URL}/validation/picks`);
                const fallbackData = await fallbackRes.json();
                const transformed = (fallbackData.picks || []).map((p: any) => ({
                    id: p.id,
                    player: { name: p.player_name, position: p.position || 'NBA', team: p.team || p.player_team || '' },
                    player_name: p.player_name,
                    market: { stat_type: p.stat_type },
                    stat_type: p.stat_type,
                    line_value: p.line,
                    line: p.line,
                    side: 'over',
                    odds: p.over_odds || -110,
                    sportsbook: 'Sharp Model',
                    sportsbook_key: 'fanduel',
                    edge: (p.ev_percentage || 3.2) / 100,
                    confidence_score: (p.confidence || 55) / 100,
                    trend_data: null,
                    matchup: { def_rank_vs_pos: p.dvp_rank || null, opponent: p.opponent || '', last_5_hit_rate: p.hit_rate_l5 || null },
                    volatility: 'medium',
                    line_velocity: null,
                    status: 'validation_fallback',
                    injury_status: p.injury_status || null
                }));
                setProps(transformed);
            }
        } catch (err) {
            console.error("Failed to fetch props:", err);
        } finally {
            setIsLoadingPicks(false);
        }
    };

    useEffect(() => {
        fetchProps(activeSport);

        // Establish Real-Time EV Stream
        const ws = new WebSocket('ws://localhost:8000/api/ws/live-odds');

        ws.onopen = () => console.log("🚀 Connected to Live EV Engine Stream");

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                if (message.type === 'LIVE_EV_UPDATE' && message.data?.items) {
                    // Update the grid instantaneously without polling
                    setProps(message.data.items);
                }
            } catch (err) {
                console.error("WebSocket Message Error:", err);
            }
        };

        return () => {
            ws.close();
        };
    }, [activeSport]);

    const toggleBook = (bookKey: string) => {
        if (selectedBooks.includes(bookKey)) {
            setSelectedBooks(selectedBooks.filter(b => b !== bookKey));
        } else {
            setSelectedBooks([...selectedBooks, bookKey]);
        }
    };

    const filteredProps = props.filter(p =>
        selectedBooks.includes(p.sportsbook_key) &&
        (p.player?.name || p.player_name || '').toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handleSort = (column: 'edge' | 'odds' | 'player') => {
        if (sortColumn === column) {
            setSortDirection(sortDirection === 'desc' ? 'asc' : 'desc');
        } else {
            setSortColumn(column);
            setSortDirection('desc'); // Default to high-to-low for new columns
        }
    };

    const sortedProps = [...filteredProps].sort((a, b) => {
        let valA, valB;
        if (sortColumn === 'edge') {
            valA = a.edge || 0;
            valB = b.edge || 0;
        } else if (sortColumn === 'odds') {
            // Treat American odds correctly (-110 < +150)
            valA = a.odds > 0 ? a.odds : (10000 / Math.abs(a.odds));
            valB = b.odds > 0 ? b.odds : (10000 / Math.abs(b.odds));
        } else {
            valA = (a.player?.name || a.player_name || '').toLowerCase();
            valB = (b.player?.name || b.player_name || '').toLowerCase();
        }

        if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
        if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
        return 0;
    });

    return (
        <div className="flex gap-6">
            {/* Page Sidebar Filters */}
            <aside className="hidden xl:flex flex-col w-64 shrink-0 space-y-6">
                <div className="glass-panel p-4 rounded-xl space-y-6">
                    <div>
                        <h3 className="text-xs font-bold text-secondary uppercase tracking-wider mb-3">Sport</h3>
                        <div className="space-y-1">
                            {SPORTS.filter(s => s.inSeason).map(sport => (
                                <FilterButton
                                    key={sport.id}
                                    icon={sport.icon}
                                    label={sport.name}
                                    count={sport.id === activeSport ? props.length : 0}
                                    active={activeSport === sport.id}
                                    onClick={() => setActiveSport(sport.id)}
                                />
                            ))}
                        </div>
                    </div>

                    <div>
                        <h3 className="text-xs font-bold text-secondary uppercase tracking-wider mb-3">Markets</h3>
                        <div className="space-y-2">
                            {activeSport.includes('basket') ? (
                                <>
                                    <Checkbox label="Points" checked />
                                    <Checkbox label="Rebounds" checked />
                                    <Checkbox label="Assists" checked />
                                    <Checkbox label="3-Pointers" />
                                </>
                            ) : activeSport.includes('hockey') ? (
                                <>
                                    <Checkbox label="Points" checked />
                                    <Checkbox label="Goals" checked />
                                    <Checkbox label="Assists" checked />
                                    <Checkbox label="Shots on Goal" />
                                </>
                            ) : (
                                <>
                                    <Checkbox label="Passing Yards" checked />
                                    <Checkbox label="Rushing Yards" checked />
                                    <Checkbox label="Anytime TD" />
                                    <Checkbox label="Receptions" />
                                </>
                            )}
                        </div>
                    </div>

                    <div className="pt-4 border-t border-slate-700/50">
                        <div className="bg-gradient-to-br from-surface to-[#0f1719] rounded-xl p-4 border border-slate-700/50">
                            <div className="flex items-start gap-3 mb-2">
                                <div className="p-1.5 rounded bg-amber-500/20 text-amber-500">
                                    <TrendingUp size={18} />
                                </div>
                                <div>
                                    <h4 className="text-sm font-bold text-white">Live Market Move</h4>
                                    <p className="text-xs text-slate-400 mt-1">
                                        Sharp pressure detected on <span className="text-white font-medium">{decisions[0]?.details.player_name || 'Active Picks'}</span>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Grid Content */}
            <div className="flex-1 min-w-0">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                    <div>
                        <div className="flex items-center gap-3">
                            <h1 className="text-2xl font-black tracking-tight text-white">Market Intel & Picks</h1>
                            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-black tracking-widest bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                                <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" /> LIVE STREAM
                            </div>
                        </div>
                        <p className="text-sm text-secondary mt-1">
                            AI-powered value detection across the entire daily sports slate.
                        </p>
                    </div>

                    <div className="flex-1 max-w-md mx-4 hidden lg:block">
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search size={16} className="text-slate-500" />
                            </div>
                            <input
                                type="text"
                                placeholder="Search players..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-surface border border-slate-700 text-white text-sm rounded-lg focus:ring-primary focus:border-primary block pl-10 p-2.5 transition-colors"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex flex-wrap gap-2 justify-end max-w-sm">
                            {AVAILABLE_BOOKS.map((book) => (
                                <button
                                    key={book.key}
                                    onClick={() => toggleBook(book.key)}
                                    className={`px-2.5 py-1.5 rounded-lg text-xs font-bold transition-all border ${selectedBooks.includes(book.key) ? 'bg-primary/20 border-primary/50 text-primary' : 'bg-surface border-slate-700 text-slate-500 hover:text-white'}`}
                                >
                                    {book.name}
                                </button>
                            ))}
                        </div>
                        <div className="h-8 w-px bg-slate-800 mx-2"></div>
                        <div className="flex items-center bg-surface rounded-lg p-1 border border-slate-700">
                            <button className="px-3 py-1.5 rounded text-xs font-bold bg-primary text-background-dark shadow-lg shadow-primary/20">Sharp Model</button>
                        </div>
                        <button className="flex items-center gap-2 px-3 py-2 bg-primary text-background-dark font-bold rounded-lg text-sm hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20">
                            <Download size={18} /> <span>Export</span>
                        </button>
                    </div>
                </div>

                <div className="glass-panel rounded-xl overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-slate-800 text-[10px] uppercase tracking-widest text-slate-500 font-bold bg-[#0c1416]/50">
                                    <th className="px-6 py-4 cursor-pointer hover:text-white transition-colors group" onClick={() => handleSort('player')}>
                                        <div className="flex items-center gap-1">Player {sortColumn === 'player' && <span className="text-primary">{sortDirection === 'desc' ? '↓' : '↑'}</span>}</div>
                                    </th>
                                    <th className="px-6 py-4">Matchup</th>
                                    <th className="px-6 py-4">Prop / Line</th>
                                    <th className="px-6 py-4 cursor-pointer hover:text-white transition-colors group" onClick={() => handleSort('odds')}>
                                        <div className="flex items-center gap-1">Source / Odds {sortColumn === 'odds' && <span className="text-primary">{sortDirection === 'desc' ? '↓' : '↑'}</span>}</div>
                                    </th>
                                    <th className="px-6 py-4 text-right cursor-pointer hover:text-white transition-colors group" onClick={() => handleSort('edge')}>
                                        <div className="flex items-center justify-end gap-1">Model / Edge {sortColumn === 'edge' && <span className="text-primary">{sortDirection === 'desc' ? '↓' : '↑'}</span>}</div>
                                    </th>
                                    <th className="px-4 py-4 w-10"></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/50">
                                {isLoadingPicks ? (
                                    <tr>
                                        <td colSpan={6} className="py-20 text-center">
                                            <div className="flex flex-col items-center gap-3">
                                                <Loader2 className="animate-spin text-primary" size={32} />
                                                <p className="text-slate-400 text-sm">Aggregating daily slate picks...</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : sortedProps.length > 0 ? (
                                    <AnimatePresence mode="popLayout">
                                        {sortedProps.map((prop, idx) => (
                                            <PlayerRow
                                                key={`${prop.id}-${prop.sportsbook_key || idx}`}
                                                id={prop.id}
                                                idx={idx}
                                                expanded={expandedRow === prop.id}
                                                onClick={() => setExpandedRow(expandedRow === prop.id ? null : prop.id)}
                                                image={prop.player_image || `https://ui-avatars.com/api/?name=${encodeURIComponent(prop.player?.name || 'Player')}&background=101f19&color=0df233`}
                                                name={prop.player?.name || 'Unknown Player'}
                                                pos={prop.player?.position || 'N/A'}
                                                matchup={`${prop.player_team || prop.player?.team || ''} vs ${prop.matchup?.opponent || ''}`}
                                                time="Upcoming"
                                                prop={prop.market?.stat_type || prop.stat_type || 'Market'}
                                                line={`${prop.side === 'over' ? 'Over' : 'Under'} ${prop.line_value || prop.line || '0'}`}
                                                odds={prop.odds > 0 ? `+${prop.odds}` : prop.odds || '-110'}
                                                edge={`${((prop.edge || 0) * 100).toFixed(1)}%`}
                                                confidence={(prop.confidence_score || 0) > 0.8 ? "High" : (prop.confidence_score || 0) > 0.6 ? "Moderate" : "Low"}
                                                progress={Math.round((prop.confidence_score || 0) * 100)}
                                                sportsbook={prop.sportsbook}
                                                trendData={prop.trend_data}
                                                matchupData={prop.matchup}
                                                usageData={prop.usage}
                                                performanceSplits={prop.performance_splits}
                                                volatility={prop.volatility}
                                                lineVelocity={prop.line_velocity}
                                                injuryStatus={prop.injury_status}
                                                propId={prop.id}
                                                onOpenModal={() => setSelectedPropForModal(prop)}
                                            />
                                        ))}
                                    </AnimatePresence>
                                ) : (
                                    <tr>
                                        <td colSpan={6} className="py-20 text-center">
                                            <p className="text-slate-400 text-sm">No picks available for the current daily slate.</p>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Right Column Intelligence */}
            <aside className="hidden 2xl:flex flex-col w-80 shrink-0 space-y-6">
                <div className="glass-panel p-5 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                            <Star size={16} className="text-primary" /> Perplex Picks
                        </h3>
                        <span className="text-[10px] text-slate-500 bg-surface px-1.5 py-0.5 rounded">Live Intelligence</span>
                    </div>
                    <div className="space-y-4">
                        {decisions.slice(0, 3).map((dec, i) => (
                            <PerformerItem
                                key={i}
                                name={dec.details.player_name}
                                team={`${dec.details.stat_type} • ${dec.details.side.toUpperCase()}`}
                                hitRate={`${(dec.details.confidence * 100).toFixed(0)}%`}
                                tier={dec.confidence_tier}
                                image={`https://ui-avatars.com/api/?name=${encodeURIComponent(dec.details.player_name)}&background=0df233&color=101f19`}
                            />
                        ))}
                        {decisions.length === 0 && <p className="text-[10px] text-slate-500 italic">No AI recommendations currently available.</p>}
                    </div>
                </div>

                <div className="flex items-center justify-between px-2">
                    <div className="flex items-center gap-2">
                        <div className={`size-1.5 rounded-full ${decisions.length > 0 ? 'bg-primary animate-pulse' : 'bg-slate-600'}`}></div>
                        <span className="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">
                            {decisions.length > 0 ? 'Engine Synchronized' : 'Syncing Engine...'}
                        </span>
                    </div>
                </div>

                <div className="glass-panel p-5 rounded-xl">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                            <History size={16} className="text-primary" /> Market Intel
                        </h3>
                        <div className="size-2 rounded-full bg-red-500 animate-pulse"></div>
                    </div>
                    <div className="space-y-4 max-h-[500px] overflow-y-auto custom-scrollbar pr-2">
                        {marketIntel.map((item, i) => (
                            <IntelItem
                                key={i}
                                time={new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                title={item.title}
                                detail={item.content}
                                active={i === 0}
                            />
                        ))}
                        {marketIntel.length === 0 && <p className="text-[10px] text-slate-500 italic">Fetching the latest news...</p>}
                    </div>
                </div>
            </aside>

            {/* Trends Modal Overlay */}
            <PlayerTrendsModal
                isOpen={!!selectedPropForModal}
                onClose={() => setSelectedPropForModal(null)}
                propData={selectedPropForModal}
            />
        </div>
    );
}

function FilterButton({ icon, label, count, active, onClick }: any) {
    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors ${active ? 'bg-primary/10 text-primary font-medium' : 'hover:bg-white/5 text-slate-400'}`}
        >
            <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-lg">{icon}</span>
                <span className="text-sm">{label}</span>
            </div>
            {count > 0 && <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${active ? 'bg-primary/20 text-primary' : 'bg-slate-800 text-slate-500'}`}>{count}</span>}
        </button>
    );
}

function Checkbox({ label, checked }: any) {
    return (
        <label className="flex items-center gap-3 px-1 cursor-pointer group">
            <div className={`size-4 rounded border transition-colors flex items-center justify-center ${checked ? 'bg-primary border-primary' : 'border-slate-600 group-hover:border-primary'}`}>
                {checked && <span className="material-symbols-outlined text-[10px] text-black font-bold">check</span>}
            </div>
            <span className={`text-sm transition-colors ${checked ? 'text-slate-200' : 'text-slate-500 group-hover:text-primary'}`}>{label}</span>
        </label>
    );
}

function PlayerRow({ expanded, onClick, image, name, pos, matchup, time, prop, line, odds, sportsbook, edge, confidence, progress, trendData, matchupData, usageData, performanceSplits, volatility, idx, injuryStatus, propId, onOpenModal }: any) {
    const [isTracked, setIsTracked] = useState(false);
    const [isTracking, setIsTracking] = useState(false);
    const [kellyData, setKellyData] = useState<any>(null);
    const [bestPrice, setBestPrice] = useState<any>(null);

    useEffect(() => {
        const fetchBestPrice = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/shop/best-price/${propId || 0}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.status !== 'error') setBestPrice(data);
                }
            } catch (err) {
                console.error("Best price fetch error:", err);
            }
        };
        if (propId) fetchBestPrice();
    }, [propId]);

    useEffect(() => {
        const fetchKelly = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/kelly/size/${propId || 0}?bankroll=1000&side=${line.toLowerCase().includes('over') ? 'over' : 'under'}`);
                if (res.ok) setKellyData(await res.json());
            } catch (err) {
                console.error("Kelly fetch error:", err);
            }
        };
        if (propId) fetchKelly();
    }, [propId, line]);

    const handleTrackBet = async () => {
        const token = getAuthToken();
        if (!token) {
            alert("Please login to track bets");
            return;
        }

        setIsTracking(true);
        try {
            const res = await fetch(`${API_ENDPOINTS.LEDGER}/track`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    slip_type: "straight",
                    sportsbook: sportsbook || "Sharp Model",
                    total_odds: parseInt(odds),
                    legs: [{
                        prop_id: propId || 0,
                        side: line.toLowerCase().includes('over') ? 'over' : 'under',
                        odds_taken: parseInt(odds),
                        line_taken: getLineValue()
                    }]
                })
            });

            if (!res.ok) throw new Error("Failed to track bet");

            setIsTracked(true);
            setTimeout(() => setIsTracked(false), 3000);
        } catch (err) {
            console.error(err);
            alert("Error tracking bet. Ensure you are logged in.");
        } finally {
            setIsTracking(false);
        }
    };
    // Safety check for line parsing
    const getLineValue = () => {
        if (!line) return 0;
        const parts = line.split(' ');
        const val = parseFloat(parts[parts.length - 1]);
        return isNaN(val) ? 0 : val;
    };

    return (
        <>
            <motion.tr
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                onClick={onClick}
                className={`group cursor-pointer hover:bg-white/[0.02] transition-colors ${expanded ? 'bg-white/[0.04]' : ''}`}
            >
                <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                        <img src={image} className="size-10 rounded-full object-cover border border-slate-700" alt="" />
                        <div>
                            <p className="text-sm font-bold text-white tracking-tight">
                                {name} {injuryStatus && <span className="text-red-500 text-[10px] uppercase ml-1 animate-pulse">({injuryStatus})</span>}
                            </p>
                            <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">{pos}</p>
                        </div>
                    </div>
                </td>
                <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
                            {matchup} <span className="text-[10px] text-slate-500 font-normal">{time}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${matchupData?.def_rank_vs_pos <= 10 ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' :
                                matchupData?.def_rank_vs_pos >= 20 ? 'bg-red-500/10 border-red-500/20 text-red-500' :
                                    'bg-slate-800 border-slate-700 text-slate-400'
                                }`}>
                                D-RANK: {matchupData?.def_rank_vs_pos ? `#${matchupData.def_rank_vs_pos}` : 'N/A'}
                            </span>
                            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">vs {matchupData?.opponent || 'Opp'}</span>
                        </div>
                        {matchupData?.l10_trend && (
                            <div className="flex items-center gap-1 mt-1">
                                <span className="text-[9px] text-slate-500 font-bold mr-1">L10</span>
                                {matchupData.l10_trend.map((hit: boolean, i: number) => (
                                    <div key={i} className={`h-3 w-1.5 rounded-sm ${hit ? 'bg-emerald-500' : 'bg-red-500/80'}`}></div>
                                ))}
                            </div>
                        )}
                    </div>
                </td>

                <td className="px-6 py-4">
                    <div className="flex items-center gap-4">
                        <div>
                            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-0.5">{prop}</p>
                            <p className="text-sm font-bold text-white">{line}</p>
                        </div>
                        {/* <Sparkline velocity={lineVelocity || 0} /> */}
                    </div>
                </td>
                <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                        <div className="inline-flex px-2 py-1 rounded bg-info/10 border border-info/20 self-start">
                            <p className="text-[10px] font-black uppercase text-info tracking-tighter">{sportsbook || 'Sharp'}</p>
                        </div>
                        {bestPrice && bestPrice.best_sportsbook !== sportsbook && (
                            <div className="inline-flex px-2 py-1 rounded bg-primary/20 border border-primary/30 self-start animate-bounce">
                                <p className="text-[10px] font-black uppercase text-primary tracking-tighter flex items-center gap-1">
                                    <TrendingUp size={10} /> BEST: {bestPrice.best_sportsbook} ({bestPrice.best_over_odds > 0 ? '+' : ''}{bestPrice.best_over_odds})
                                </p>
                            </div>
                        )}
                    </div>
                    {volatility === 'high' && (
                        <span className="text-[8px] font-black text-amber-500 uppercase flex items-center gap-1">
                            <TrendingUp size={10} /> High Volatility
                        </span>
                    )}
                    {kellyData && (
                        <div className="flex items-center gap-1 mt-1">
                            <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${kellyData.recommended_units >= 2 ? 'bg-primary/20 border-primary/30 text-primary' : 'bg-slate-800 border-slate-700 text-slate-400'
                                }`}>
                                REC: {kellyData.recommended_units} UNITS
                            </span>
                        </div>
                    )}
                </td>
                <td className="px-6 py-4 text-right">
                    <div className="flex flex-col items-end gap-1.5">
                        <div className="flex items-center gap-1.5">
                            <span className="text-xs text-emerald-primary font-black italic">{edge} Edge</span>
                        </div>
                        <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-primary glow-emerald shadow-[0_0_8px_rgba(13,242,51,0.5)] transition-all duration-1000" style={{ width: `${progress}%` }}></div>
                        </div>
                        <span className="text-[10px] text-primary font-bold uppercase tracking-tighter opacity-70">{confidence} Confidence</span>
                    </div>
                </td>
                <td className="px-4 py-4 text-right">
                    <ChevronDown className={`text-slate-600 transition-all duration-300 ${expanded ? 'rotate-180 text-primary' : ''}`} size={20} />
                </td>
            </motion.tr >
            {expanded && (
                <tr className="bg-white/[0.02]">
                    <td colSpan={6} className="px-6 py-0 focus:outline-none">
                        <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="py-8 border-t border-slate-800/50 flex gap-8 overflow-hidden"
                        >
                            <div className="w-1 bg-gradient-to-b from-primary to-transparent rounded-full shrink-0"></div>
                            <div className="flex-1 space-y-6">
                                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2">
                                            <div className="p-1.5 rounded bg-primary/10">
                                                <Brain size={14} className="text-primary" />
                                            </div>
                                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Logic Analysis</span>
                                        </div>
                                        <div className="glass-premium p-4 rounded-xl border-white/[0.05] space-y-4">
                                            <p className="text-xs text-slate-300 leading-relaxed font-medium">
                                                AI Model detection: This line is showing significant sharp pressure. {name} has cleared this line in {matchupData?.last_5_hit_rate || '3/5'} games. Matchup vs {matchupData?.opponent} is {matchupData?.rating}.
                                            </p>
                                            <div className="pt-2 border-t border-white/5">
                                                <HitRateStack
                                                    splits={{
                                                        l5: (performanceSplits?.last_5?.rate || 60) / 100,
                                                        l10: (performanceSplits?.last_10?.rate || 70) / 100,
                                                        l20: (performanceSplits?.last_20?.rate || 55) / 100,
                                                        vs_opp: (performanceSplits?.away?.rate || 80) / 100
                                                    }}
                                                    size="sm"
                                                />
                                            </div>
                                        </div>
                                        <MatchupIntelligence
                                            oppRank={matchupData?.def_rank_vs_pos || 15}
                                            paceFactor={matchupData?.pace || 'Avg'}
                                            trend={matchupData?.last_5_hit_rate || '3/5'}
                                        />
                                    </div>

                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2">
                                            <div className="p-1.5 rounded bg-emerald-primary/10">
                                                <TrendingUp size={14} className="text-emerald-primary" />
                                            </div>
                                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Performance History</span>
                                        </div>
                                        <div className="glass-premium p-3 rounded-xl border-white/[0.05]">
                                            <TrendChart
                                                data={trendData || []}
                                                line={getLineValue()}
                                                statType={prop}
                                            />
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2">
                                            <div className="p-1.5 rounded bg-amber-500/10">
                                                <Star size={14} className="text-amber-500" />
                                            </div>
                                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Market Indicators</span>
                                        </div>
                                        <div className="glass-premium p-5 rounded-xl border-white/[0.05] space-y-3">
                                            <div className="flex items-center justify-between">
                                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{usageData?.metric || 'Usage'}</span>
                                                <span className="text-xs font-black text-primary">{usageData?.value || 'N/A'}</span>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Trend</span>
                                                <span className={`text-[10px] font-bold ${usageData?.trend === 'Upward' ? 'text-emerald-primary' : 'text-slate-300'}`}>{usageData?.trend || 'Stable'}</span>
                                            </div>
                                            <div className="pt-2 border-t border-white/5">
                                                <p className="text-[10px] text-slate-400 italic">"{usageData?.context || 'Consistent player role'}"</p>
                                            </div>
                                        </div>
                                    </div>

                                </div>
                            </div>
                            <div className="w-64 flex flex-col gap-4">
                                <SportsbookDeeplinks
                                    playerName={name}
                                    statType={prop}
                                    line={getLineValue()}
                                    side={line.toLowerCase().includes('over') ? 'over' : 'under'}
                                    odds={parseInt(odds)}
                                />
                                <BetSlipShare
                                    pick={{
                                        player_name: name,
                                        stat_type: prop,
                                        line: getLineValue(),
                                        side: line.toLowerCase().includes('over') ? 'over' : 'under',
                                        odds: parseInt(odds),
                                        sportsbook: sportsbook || "Sharp Model",
                                        edge: parseFloat(edge.replace('%', '')) / 100
                                    }}
                                />
                                <button
                                    onClick={(e) => { e.stopPropagation(); onOpenModal(); }}
                                    className="w-full py-3 border border-primary/30 rounded-xl text-xs font-black uppercase tracking-widest text-primary hover:bg-primary/10 transition-all active:scale-[0.98]"
                                >
                                    ANALYZE TRENDS
                                </button>
                                <button
                                    onClick={(e) => { e.stopPropagation(); handleTrackBet(); }}
                                    disabled={isTracking || isTracked}
                                    className={`w-full py-3 border rounded-xl text-xs font-black uppercase tracking-widest transition-all ${isTracked
                                        ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-500'
                                        : 'border-white/10 glass-premium text-slate-300 hover:bg-white/5 active:scale-[0.98]'
                                        }`}
                                >
                                    {isTracking ? 'SYNCING...' : isTracked ? 'TRACKED ✓' : 'ADD TO TRACKER'}
                                </button>
                            </div>
                        </motion.div>
                    </td>
                </tr>
            )
            }
        </>
    );
}



function PerformerItem({ name, team, hitRate, image, tier }: any) {
    const tierColors: any = {
        high: "text-emerald-primary",
        mid: "text-amber-500",
        speculative: "text-slate-400"
    };

    return (
        <div className="flex items-center justify-between group cursor-pointer p-2 rounded-lg hover:bg-white/[0.03] transition-all border border-transparent hover:border-white/5">
            <div className="flex items-center gap-3">
                <div className="relative">
                    <img src={image} className="size-8 rounded-full border border-slate-700" alt="" />
                    <div className={`absolute -top-1 -right-1 size-2.5 rounded-full border-2 border-[#101f19] ${tier === 'high' ? 'bg-primary' : tier === 'mid' ? 'bg-amber-500' : 'bg-slate-600'}`}></div>
                </div>
                <div>
                    <p className="text-xs font-bold text-white group-hover:text-primary transition-colors">{name}</p>
                    <p className="text-[10px] text-slate-500 flex items-center gap-1">
                        {team}
                        {tier && <span className={`uppercase font-black text-[8px] ${tierColors[tier]}`}>• {tier}</span>}
                    </p>
                </div>
            </div>
            <div className="text-right">
                <p className={`text-xs font-bold ${tier === 'high' ? 'text-emerald-primary' : tier === 'mid' ? 'text-amber-500' : 'text-slate-300'}`}>{hitRate}</p>
                <p className="text-[10px] text-slate-500">Hit Rate</p>
            </div>
        </div>
    );
}

function IntelItem({ time, title, detail, active }: any) {
    return (
        <div className="relative pl-4 border-l-2 border-slate-800 pb-2">
            <div className={`absolute -left-[5px] top-0 size-2 rounded-full ring-4 ring-background-dark ${active ? 'bg-primary' : 'bg-slate-700'}`}></div>
            <p className="text-[10px] text-slate-600 mb-1">{time}</p>
            <p className="text-xs font-bold text-slate-300">{title}</p>
            {detail && <p className="text-[10px] text-secondary mt-1 font-mono">{detail}</p>}
        </div>
    );
}

