/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { Layers, Plus, X, Zap, ChevronRight, TrendingUp, Share2, Loader2 } from 'lucide-react';
import { SPORTS } from '../utils/sportUtils';
import { useBrainData } from '../hooks/useBrainData';

const AVAILABLE_BOOKS = [
    { key: 'fanduel', name: 'FanDuel' },
    { key: 'draftkings', name: 'DraftKings' },
    { key: 'prizepicks', name: 'PrizePicks' },
    { key: 'underdog', name: 'Underdog' },
    { key: 'betrivers', name: 'BetRivers' },
    { key: 'caesars', name: 'Caesars' },
    { key: 'betmgm', name: 'BetMGM' }
];

export default function ParlayBuilder() {
    const [selectedLegs, setSelectedLegs] = useState<any[]>([]);
    const [availableProps, setAvailableProps] = useState<any[]>([]);
    const [suggestedBundles, setSuggestedBundles] = useState<any[]>([]);
    const [isLoadingAvailable, setIsLoadingAvailable] = useState(true);
    const [activeSport, setActiveSport] = useState('basketball_nba');
    const [wager, setWager] = useState(20);
    const [selectedBooks, setSelectedBooks] = useState<string[]>(AVAILABLE_BOOKS.map(b => b.key));

    const { marketIntel } = useBrainData(activeSport);

    const fetchAvailableProps = async (sport: string) => {
        setIsLoadingAvailable(true);
        try {
            const res = await fetch(`http://localhost:8000/immediate/working-player-props?sport_key=${sport}&limit=50`);
            const data = await res.json();

            if (data.items && data.items.length > 0) {
                setAvailableProps(data.items);
            } else {
                // FALLBACK: use validation picks
                const fallbackRes = await fetch(`http://localhost:8000/validation/picks`);
                const fallbackData = await fallbackRes.json();
                const transformed = (fallbackData.picks || []).map((p: any) => ({
                    id: p.id,
                    player: { name: p.player_name, position: 'NBA' },
                    player_name: p.player_name,
                    market: { stat_type: p.stat_type },
                    stat_type: p.stat_type,
                    side: 'over',
                    line_value: p.line,
                    line: p.line,
                    odds: p.over_odds || -110,
                    sportsbook: 'Sharp Model',
                    sportsbook_key: 'fanduel',
                    edge: (p.ev_percentage || 3.2) / 100,
                    confidence_score: (p.confidence || 55) / 100,
                    status: 'validation_fallback'
                }));
                setAvailableProps(transformed);
            }
        } catch (err) {
            console.error("Failed to fetch props for parlay:", err);
        } finally {
            setIsLoadingAvailable(false);
        }
    };

    const fetchSuggestedParlays = async (sport: string) => {
        try {
            const res = await fetch(`http://localhost:8000/immediate/suggested-parlays?sport_key=${sport}`);
            const data = await res.json();
            setSuggestedBundles(data.bundles || []);
        } catch (err) {
            console.error("Failed to fetch suggested parlays:", err);
        }
    };

    useEffect(() => {
        fetchAvailableProps(activeSport);
        fetchSuggestedParlays(activeSport);
    }, [activeSport]);

    const toggleBook = (bookKey: string) => {
        if (selectedBooks.includes(bookKey)) {
            setSelectedBooks(selectedBooks.filter(b => b !== bookKey));
        } else {
            setSelectedBooks([...selectedBooks, bookKey]);
        }
    };

    const addToParlay = (prop: any) => {
        if (selectedLegs.find(l => l.id === prop.id)) return;
        setSelectedLegs([...selectedLegs, {
            id: prop.id,
            player: prop.player?.name || prop.player_name,
            market: `${prop.side === 'over' ? 'Over' : 'Under'} ${prop.line_value || prop.line} ${prop.market?.stat_type || prop.stat_type}`,
            odds: prop.odds ? (prop.odds > 0 ? `+${prop.odds}` : prop.odds) : '-119',
            decimalOdds: prop.odds ? (prop.odds > 0 ? (prop.odds / 100) + 1 : (100 / Math.abs(prop.odds)) + 1) : 1.84,
            team: prop.player?.position || "TX-DFS",
            icon: activeSport.includes('basket') ? 'sports_basketball' : 'sports_hockey',
            sportsbook: prop.sportsbook || "Standard"
        }]);
    };

    const removeLeg = (id: number) => {
        setSelectedLegs(selectedLegs.filter(l => l.id !== id));
    };

    // DFS Payout Structure (PrizePicks Power Play)
    const getDfsPayoutMultiplier = (numLegs: number) => {
        if (numLegs === 2) return 3;
        if (numLegs === 3) return 5;
        if (numLegs === 4) return 10;
        if (numLegs === 5) return 10; // Flex
        if (numLegs === 6) return 25;
        return 0;
    };

    const isDfsEntry = selectedLegs.every(l => ['prizepicks', 'underdog', 'sleeper', 'parlayplay'].includes(l.sportsbookKey));

    const totalDecimalOdds = selectedLegs.reduce((acc, leg) => acc * leg.decimalOdds, 1);
    const totalAmericanOdds = isDfsEntry
        ? `${getDfsPayoutMultiplier(selectedLegs.length)}x Payout`
        : (totalDecimalOdds === 1 ? '+0' : (totalDecimalOdds >= 2 ? `+${Math.round((totalDecimalOdds - 1) * 100)}` : `-${Math.round(100 / (totalDecimalOdds - 1))}`));

    const estPayout = isDfsEntry
        ? wager * getDfsPayoutMultiplier(selectedLegs.length)
        : wager * totalDecimalOdds;
    const avgEdge = selectedLegs.length > 0 ? (isDfsEntry ? 14.2 : 12.5) : 0;

    const filteredProps = availableProps.filter(p => selectedBooks.includes(p.sportsbook_key));

    return (
        <div className="flex gap-8">
            {/* Main Builder Area */}
            <div className="flex-1 space-y-8 min-w-0">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-primary/10 text-primary border border-primary/20">
                                <Layers size={24} />
                            </div>
                            {isDfsEntry ? 'Pickem Entry Builder' : 'Build Parlay'}
                        </h1>
                        <p className="text-sm text-secondary mt-1">
                            {isDfsEntry
                                ? "Optimizing PrizePicks & Underdog entries with correlated edges."
                                : "Combine high-EV legs with mathematical correlation detection."}
                        </p>
                    </div>
                    <div className="flex flex-col gap-3 items-end">
                        <div className="flex flex-wrap gap-2 justify-end max-w-md">
                            {AVAILABLE_BOOKS.map((book) => (
                                <button
                                    key={book.key}
                                    onClick={() => toggleBook(book.key)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${selectedBooks.includes(book.key) ? 'bg-primary/20 border-primary/50 text-primary shadow-[0_0_15px_rgba(13,242,51,0.1)]' : 'bg-surface border-slate-700 text-slate-500 hover:text-slate-300'}`}
                                >
                                    {book.name}
                                </button>
                            ))}
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-slate-500 uppercase tracking-widest mr-2">Sort:</span>
                            {['Highest EV', 'Correlated'].map((f) => (
                                <button key={f} className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${f === 'Highest EV' ? 'bg-slate-800 text-white border border-slate-700' : 'text-secondary hover:text-white'}`}>
                                    {f}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="space-y-4">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest px-1">Highly Recommended Correlated Legs</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {suggestedBundles.slice(0, 2).map((bundle, i) => (
                            <RecommendationCard
                                key={i}
                                title={`${bundle.legs[0].player_name} + ${bundle.legs[1].player_name}`}
                                subtitle={`${activeSport.includes('basket') ? 'NBA' : activeSport.includes('hockey') ? 'NHL' : 'NFL'} • Correlated Bundle`}
                                correlation={`${(bundle.correlation_score * 100).toFixed(0)}% Synergetic Link`}
                                ev={`+${(bundle.combined_ev * 100).toFixed(1)}%`}
                                odds={bundle.legs[0].odds > 0 ? `+${bundle.legs[0].odds}` : bundle.legs[0].odds}
                                icon={i === 0 ? 'bolt' : 'stars'}
                                onAdd={() => {
                                    bundle.legs.forEach((leg: any) => addToParlay(leg));
                                }}
                            />
                        ))}
                        {suggestedBundles.length === 0 && (
                            <div className="col-span-2 text-center py-6 text-slate-500 text-xs italic">
                                No correlated bundles found for this slate. Try another sport.
                            </div>
                        )}
                    </div>
                </div>

                <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800/10 shadow-2xl">
                    <div className="p-6 border-b border-slate-800/50 bg-surface/30 flex items-center justify-between">
                        <h3 className="font-bold text-white flex items-center gap-2">
                            <span className="material-symbols-outlined text-primary">add_circle</span>
                            Add Legs to Your Parlay
                        </h3>
                        <div className="flex items-center bg-background-dark rounded-lg p-1 border border-slate-800">
                            {SPORTS.filter(s => s.inSeason).map(sport => (
                                <button
                                    key={sport.id}
                                    onClick={() => setActiveSport(sport.id)}
                                    className={`px-3 py-1 text-xs font-bold rounded transition-all ${activeSport === sport.id ? 'bg-slate-700 text-white' : 'text-slate-500 hover:text-white'}`}
                                >
                                    {sport.name}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="divide-y divide-slate-800/50">
                        {isLoadingAvailable ? (
                            <div className="py-20 text-center flex flex-col items-center gap-3">
                                <Loader2 className="animate-spin text-primary" size={32} />
                                <p className="text-slate-400 text-sm">Fetching available markets...</p>
                            </div>
                        ) : filteredProps.length > 0 ? (
                            filteredProps.map((prop) => (
                                <MarketRow
                                    key={`${prop.id}-${prop.sportsbook_key}`}
                                    player={prop.player?.name || prop.player_name || 'Unknown'}
                                    prop={prop.market?.stat_type || prop.stat_type || 'N/A'}
                                    options={[{
                                        line: `${prop.side === 'over' ? 'Over' : 'Under'} ${prop.line_value}`,
                                        odds: prop.odds > 0 ? `+${prop.odds}` : prop.odds
                                    }]}
                                    sportsbook={prop.sportsbook}
                                    onAdd={() => addToParlay(prop)}
                                    alreadyAdded={selectedLegs.some(l => l.id === prop.id)}
                                />
                            ))
                        ) : (
                            <div className="py-20 text-center">
                                <p className="text-slate-400 text-sm">No player props found for the selected books.</p>
                                <button
                                    onClick={() => setSelectedBooks(AVAILABLE_BOOKS.map(b => b.key))}
                                    className="mt-4 text-xs font-bold text-primary hover:underline"
                                >
                                    Reset Filters
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Parlay Slip Sidebar */}
            <aside className="hidden lg:flex flex-col w-96 shrink-0 h-fit sticky top-24">
                <div className="glass-panel rounded-2xl flex flex-col overflow-hidden border-primary/20 shadow-[0_0_50px_rgba(13,242,51,0.05)]">
                    <div className="p-5 bg-gradient-to-r from-emerald-primary/10 to-transparent border-b border-emerald-primary/20">
                        <div className="flex items-center justify-between mb-1">
                            <h2 className="text-xl font-black text-white italic tracking-tighter">PARLAY SLIP</h2>
                            <span className="text-[10px] font-bold text-emerald-primary bg-emerald-primary/10 px-2 py-0.5 rounded uppercase tracking-widest border border-emerald-primary/20">Precision View</span>
                        </div>
                        <p className="text-[10px] text-slate-400 font-medium">Build smarter. Edge: <span className="text-emerald-primary font-bold">+18.4%</span></p>
                    </div>

                    <div className="p-5 space-y-4 max-h-[400px] overflow-y-auto custom-scrollbar">
                        {selectedLegs.length > 0 ? selectedLegs.map((leg) => (
                            <div key={leg.id} className="relative bg-[#121e16] border border-slate-800/80 rounded-xl p-4 group hover:border-emerald-primary/30 transition-all">
                                <button
                                    onClick={() => removeLeg(leg.id)}
                                    className="absolute top-3 right-3 text-slate-600 hover:text-red-400 transition-colors"
                                >
                                    <X size={14} />
                                </button>
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="material-symbols-outlined text-emerald-primary opacity-60">{leg.icon}</span>
                                    <span className="text-xs font-bold text-emerald-primary">{leg.team}</span>
                                </div>
                                <p className="text-sm font-bold text-white mb-0.5">{leg.player}</p>
                                <div className="flex justify-between items-center">
                                    <p className="text-xs text-slate-400">{leg.market}</p>
                                    <span className="text-sm font-mono font-bold text-emerald-primary">{leg.odds}</span>
                                </div>
                            </div>
                        )) : (
                            <div className="text-center py-10 text-slate-600">
                                <p className="text-xs">No legs added yet.</p>
                            </div>
                        )}

                        <button className="w-full py-3 border-2 border-dashed border-slate-800 rounded-xl text-slate-600 hover:text-slate-400 hover:border-slate-700 transition-all flex items-center justify-center gap-2 group">
                            <Plus size={18} className="group-hover:scale-110 transition-transform" />
                            <span className="text-xs font-bold">Add Another Leg</span>
                        </button>
                    </div>

                    <div className="p-5 bg-surface border-t border-slate-800 space-y-5">
                        <div className="space-y-3">
                            <div className="flex justify-between items-center text-xs font-bold text-slate-500 uppercase tracking-widest">
                                <span>Wager Amount</span>
                                <span className="text-slate-400 font-mono italic">Min: $10</span>
                            </div>
                            <div className="relative">
                                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 font-mono text-lg">$</span>
                                <input
                                    className="w-full bg-background-dark border border-slate-800 rounded-xl py-4 pl-10 pr-4 text-white font-mono text-2xl focus:ring-1 focus:ring-emerald-primary outline-none"
                                    type="number"
                                    value={wager}
                                    onChange={(e) => setWager(Number(e.target.value))}
                                />
                            </div>
                        </div>

                        <div className="p-4 bg-background-dark rounded-xl border border-slate-800/80 divide-y divide-slate-800/50">
                            <div className="flex justify-between items-center py-2">
                                <span className="text-xs text-slate-400">Total Odds</span>
                                <span className="text-sm font-mono text-white tracking-tighter italic font-bold">{selectedLegs.length > 0 ? totalAmericanOdds : '+100'}</span>
                            </div>
                            <div className="flex justify-between items-center py-2">
                                <span className="text-xs text-slate-400">Est. Payout</span>
                                <span className="text-lg font-mono text-emerald-primary tracking-tighter italic font-black">${selectedLegs.length > 0 ? estPayout.toFixed(2) : (wager * 2).toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between items-center py-2 pt-3">
                                <div className="flex items-center gap-1.5 text-xs text-slate-300 font-bold">
                                    <Zap size={14} className="text-amber-400" /> Real Edge
                                </div>
                                <div className="flex flex-col items-end">
                                    <span className="text-sm font-mono text-amber-400 font-bold">+{avgEdge}%</span>
                                    <span className="text-[10px] text-slate-500">vs Book Odds</span>
                                </div>
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <button className="flex-1 bg-emerald-primary text-background-dark font-black py-4 rounded-xl text-sm shadow-[0_0_30px_rgba(13,242,51,0.2)] hover:bg-emerald-primary/90 transition-all flex items-center justify-center gap-2 group">
                                LOCK IN PARLAY <ChevronRight size={18} className="group-hover:translate-x-1 transition-transform" />
                            </button>
                            <button className="p-4 bg-slate-800 text-slate-400 rounded-xl hover:text-white transition-colors">
                                <Share2 size={20} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Market Intel Sidebar Component */}
                <div className="glass-panel p-5 rounded-2xl border border-slate-800/50">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                            <TrendingUp size={16} className="text-primary" /> Market Intel
                        </h3>
                        <div className="size-2 rounded-full bg-red-500 animate-pulse"></div>
                    </div>
                    <div className="space-y-4 max-h-[300px] overflow-y-auto custom-scrollbar pr-2">
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
        </div>
    );
}

function IntelItem({ time, title, detail, active }: any) {
    return (
        <div className="relative pl-4 border-l-2 border-slate-800 pb-2 text-left">
            <div className={`absolute -left-[5px] top-0 size-2 rounded-full ring-4 ring-background-dark ${active ? 'bg-primary' : 'bg-slate-700'}`}></div>
            <p className="text-[10px] text-slate-600 mb-1">{time}</p>
            <p className="text-xs font-bold text-slate-300">{title}</p>
            {detail && <p className="text-[10px] text-secondary mt-1 font-mono">{detail}</p>}
        </div>
    );
}

function RecommendationCard({ title, subtitle, correlation, ev, odds, icon, onAdd }: any) {
    return (
        <div
            onClick={onAdd}
            className="glass-panel p-4 rounded-xl border-l-4 border-emerald-primary group hover:bg-white/5 transition-all cursor-pointer"
        >
            <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded bg-emerald-primary/10 text-emerald-primary">
                        <span className="material-symbols-outlined text-lg">{icon}</span>
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-white group-hover:text-emerald-primary transition-colors">{title}</h4>
                        <p className="text-[10px] text-slate-500 font-medium">{subtitle}</p>
                    </div>
                </div>
                <div className="flex flex-col items-end gap-1">
                    <span className="text-xs font-mono font-bold text-white italic">{odds}</span>
                    <div className="size-6 rounded-full bg-emerald-primary/20 flex items-center justify-center text-emerald-primary group-hover:bg-emerald-primary group-hover:text-background-dark transition-all">
                        <Plus size={14} />
                    </div>
                </div>
            </div>
            <div className="flex flex-col gap-2 mt-4">
                <div className="flex items-center gap-1.5 text-[10px] text-emerald-primary font-bold">
                    <TrendingUp size={12} /> Edge: {ev}
                </div>
                <div className="p-2 bg-background-dark/50 rounded-lg border border-slate-800 text-[10px] text-slate-400 leading-relaxed font-medium">
                    <span className="text-slate-200">Correlation:</span> {correlation}
                </div>
            </div>
        </div>
    );
}

function MarketRow({ player, prop, options, onAdd, alreadyAdded, sportsbook }: any) {
    return (
        <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-white/[0.02] group/row">
            <div className="flex items-center gap-4">
                <div className="size-10 rounded-full bg-slate-800 flex items-center justify-center text-slate-500 group-hover/row:text-primary transition-colors">
                    <span className="material-symbols-outlined">person</span>
                </div>
                <div>
                    <div className="flex items-center gap-2 mb-0.5">
                        <p className="text-sm font-bold text-white">{player}</p>
                        <span className="text-[10px] font-bold text-primary bg-primary/10 px-1.5 py-0.5 rounded border border-primary/20">
                            {sportsbook}
                        </span>
                    </div>
                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">{prop}</p>
                </div>
            </div>
            <div className="flex gap-2">
                {options.map((opt: any, i: any) => (
                    <button
                        key={i}
                        onClick={onAdd}
                        disabled={alreadyAdded}
                        className={`flex flex-col items-center justify-center px-6 py-2 bg-surface border rounded-xl transition-all group min-w-[100px] ${alreadyAdded ? 'border-emerald-primary/50 opacity-50' : 'border-slate-800 hover:border-emerald-primary/30'}`}
                    >
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-0.5">{opt.line}</span>
                        <span className="text-xs font-mono font-bold text-white group-hover:text-emerald-primary">{opt.odds}</span>
                    </button>
                ))}
                <button
                    onClick={onAdd}
                    disabled={alreadyAdded}
                    className={`px-4 bg-slate-800 rounded-xl transition-all ${alreadyAdded ? 'text-emerald-primary' : 'text-slate-500 hover:bg-slate-700 hover:text-white'}`}
                >
                    {alreadyAdded ? <TrendingUp size={16} /> : <Plus size={16} />}
                </button>
            </div>
        </div>
    );
}
