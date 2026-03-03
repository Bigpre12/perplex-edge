"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Bolt, LayoutDashboard, Calculator, ExternalLink, RefreshCw, TrendingUp as Savings, Loader2, Target, Zap } from 'lucide-react';
import { API_BASE_URL } from "@/lib/apiConfig";

const AVAILABLE_BOOKS = [
    { key: 'fanduel', name: 'FanDuel' },
    { key: 'draftkings', name: 'DraftKings' },
    { key: 'betmgm', name: 'BetMGM' },
    { key: 'pinnacle', name: 'Pinnacle' }
];

type TabType = 'arbitrage' | 'middles' | 'ev';

function ArbitrageContent() {
    const searchParams = useSearchParams();
    const activeSport = searchParams.get('sport') || 'basketball_nba';

    const [activeTab, setActiveTab] = useState<TabType>('arbitrage');
    const [items, setItems] = useState<any[]>([]);
    const [selectedId, setSelectedId] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [investment, setInvestment] = useState(1000);
    const [isHistorical, setIsHistorical] = useState(false);
    const [selectedBooks, setSelectedBooks] = useState<string[]>(AVAILABLE_BOOKS.map(b => b.key));

    const toggleBook = (bookKey: string) => {
        if (selectedBooks.includes(bookKey)) {
            setSelectedBooks(selectedBooks.filter(b => b !== bookKey));
        } else {
            setSelectedBooks([...selectedBooks, bookKey]);
        }
    };

    const fetchItems = async () => {
        setLoading(true);
        try {
            let endpoint = '';
            if (activeTab === 'arbitrage') endpoint = 'arbitrage-finder';
            else if (activeTab === 'middles') endpoint = 'middles';
            else if (activeTab === 'ev') endpoint = 'ev-feed';

            const res = await fetch(`${API_BASE_URL}/api/immediate/${endpoint}?sport_key=${activeSport}`);
            const data = await res.json();

            const fetchedItems = data.opportunities || data.items || [];
            setItems(fetchedItems);
            setIsHistorical(data.status === 'historical_backtest');

            if (fetchedItems.length > 0) {
                setSelectedId(fetchedItems[0].id || 0);
            } else {
                setSelectedId(null);
            }
        } catch (err) {
            console.error(`Failed to fetch ${activeTab}:`, err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, [activeTab, activeSport]);

    const filteredItems = items.filter(item => {
        if (activeTab === 'arbitrage') {
            const b1 = item.book1?.name?.toLowerCase() || '';
            const b2 = item.book2?.name?.toLowerCase() || '';
            return selectedBooks.some(b => b1.includes(b) || b2.includes(b));
        } else if (activeTab === 'middles') {
            const b1 = item.over_side?.book?.toLowerCase() || '';
            const b2 = item.under_side?.book?.toLowerCase() || '';
            return selectedBooks.some(b => b1.includes(b) || b2.includes(b));
        } else {
            const b1 = item.sportsbook?.toLowerCase() || item.sportsbook_key || '';
            return selectedBooks.some(b => b1.includes(b));
        }
    });

    const currentItem = filteredItems.find((item, index) => (item.id === selectedId || index === selectedId)) || filteredItems[0];

    // Calculation logic based on tab
    let profitPct = 0;
    let netProfit = 0;
    let wager1 = 0;
    let wager2 = 0;

    const parseOdds = (odds: any) => {
        if (!odds) return 1.0;
        const num = typeof odds === 'string' ? parseInt(odds) : odds;
        if (isNaN(num)) return 1.0;
        if (num > 0) return (num / 100) + 1;
        return (100 / Math.abs(num)) + 1;
    };

    if (activeTab === 'arbitrage' && currentItem) {
        const odds1 = parseOdds(currentItem.book1.odds);
        const odds2 = parseOdds(currentItem.book2.odds);
        const implied1 = 1 / odds1;
        const implied2 = 1 / odds2;
        const totalImplied = implied1 + implied2;
        wager1 = investment * (implied1 / totalImplied);
        wager2 = investment * (implied2 / totalImplied);
        profitPct = ((1 / totalImplied) - 1) * 100;
        netProfit = investment * (profitPct / 100);
    } else if (activeTab === 'ev' && currentItem) {
        profitPct = (currentItem.edge || 0) * 100;
        netProfit = investment * (currentItem.edge || 0);
        wager1 = investment;
    }

    return (
        <div className="flex gap-8">
            {/* Left Sidebar (Filters) */}
            <aside className="hidden xl:flex w-64 flex-col space-y-6">
                <div className="glass-panel p-4 rounded-xl space-y-6">
                    <div className="space-y-1">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Value Discovery</h3>
                        <SidebarLink icon={<LayoutDashboard size={18} />} label="Arbitrage Feed" active={activeTab === 'arbitrage'} onClick={() => setActiveTab('arbitrage')} />
                        <SidebarLink icon={<Target size={18} />} label="Middles Scanner" active={activeTab === 'middles'} onClick={() => setActiveTab('middles')} />
                        <SidebarLink icon={<Zap size={18} />} label="+EV Prop Feed" active={activeTab === 'ev'} onClick={() => setActiveTab('ev')} />
                    </div>

                    <div className="h-px bg-slate-800 w-full"></div>

                    <div className="space-y-4">
                        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider px-3">Active Books</h3>
                        <div className="space-y-2 px-3">
                            {AVAILABLE_BOOKS.map(book => (
                                <ToggleItem
                                    key={book.key}
                                    label={book.name}
                                    active={selectedBooks.includes(book.key)}
                                    onClick={() => toggleBook(book.key)}
                                />
                            ))}
                        </div>
                    </div>

                    <div className="mt-auto p-4 rounded-xl bg-gradient-to-br from-emerald-primary/10 to-transparent border border-emerald-primary/10">
                        <div className="flex items-center gap-2 mb-2">
                            <Bolt className="text-emerald-primary" size={18} />
                            <span className="text-sm font-bold text-white">Projected Day</span>
                        </div>
                        <p className="text-2xl font-mono font-bold text-white tracking-tight">
                            ${filteredItems.length > 0 ? filteredItems.reduce((sum, item) => sum + (item.profit ? parseFloat(item.profit) : item.profit_potential === 'High' ? 150 : (item.edge * 1000 || 0)), 0).toFixed(2) : '0.00'}
                        </p>
                        <p className="text-[10px] text-emerald-primary/80 mt-1 uppercase font-bold tracking-widest">+{filteredItems.length > 0 ? (filteredItems.length * 2) : 0}% Confidence</p>
                    </div>
                </div>
            </aside>

            {/* Main Container */}
            <div className="flex-1 space-y-8 min-w-0">
                <div className="flex items-end justify-between">
                    <div>
                        <h2 className="text-2xl font-bold text-white tracking-tight uppercase">
                            {activeTab === 'arbitrage' ? 'Arbitrage Finder' : activeTab === 'middles' ? 'Middle Scanner' : '+EV Value Feed'}
                        </h2>
                        <p className={`text-sm mt-1 flex items-center gap-2 ${isHistorical ? 'text-amber-500' : 'text-slate-400'}`}>
                            <span className="relative flex size-2">
                                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isHistorical ? 'bg-amber-500' : 'bg-emerald-primary'}`}></span>
                                <span className={`relative inline-flex rounded-full h-2 w-2 ${isHistorical ? 'bg-amber-500' : 'bg-emerald-primary'}`}></span>
                            </span>
                            {isHistorical ? 'Historical Backtest Mode' : `Scanning markets`} • High Liquidity
                        </p>
                    </div>
                    <button onClick={() => fetchItems()} className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#121e16] border border-slate-800/60 text-slate-400 hover:text-white text-xs font-medium transition-colors">
                        <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
                        Refresh
                    </button>
                </div>

                <div className="space-y-4">
                    {loading ? (
                        <div className="py-20 text-center flex flex-col items-center gap-3">
                            <Loader2 className="animate-spin text-emerald-primary" size={32} />
                            <p className="text-slate-400 text-sm">Aggregating market inefficiencies...</p>
                        </div>
                    ) : filteredItems.length > 0 ? (
                        filteredItems.map((item, idx) => (
                            <ValueCard
                                key={idx}
                                index={idx}
                                tab={activeTab}
                                data={item}
                                active={selectedId === (item.id || idx)}
                                onClick={() => setSelectedId(item.id || idx)}
                            />
                        ))
                    ) : (
                        <div className="py-20 text-center border border-dashed border-slate-800 rounded-2xl">
                            <p className="text-slate-400 text-sm">No {activeTab} opportunities found currently. Scanning daily slate...</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Execution Panel Side Panel */}
            <aside className="hidden 2xl:flex w-96 flex-col">
                <div className="glass-panel rounded-2xl flex flex-col h-full sticky top-24 max-h-[calc(100vh-120px)] overflow-hidden">
                    <div className="p-6 border-b border-slate-800/60 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-emerald-primary/10 rounded-lg text-emerald-primary">
                                <Calculator size={20} />
                            </div>
                            <h2 className="text-xl font-bold text-white tracking-tight">Execution</h2>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-6 space-y-8">
                        {currentItem ? (
                            <>
                                <div className="space-y-2">
                                    <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                                        <span>{currentItem.sport || currentItem.sport_label}</span><div className="size-1 rounded-full bg-slate-700"></div><span>{currentItem.market}</span>
                                    </div>
                                    <h3 className="text-2xl font-bold text-white leading-tight">{currentItem.match || currentItem.game || currentItem.player_name}</h3>
                                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-primary/10 text-emerald-primary text-xs font-bold border border-emerald-primary/20">
                                        <Savings size={14} /> {activeTab === 'ev' ? 'Projected Edge' : 'Potential Profit'}: {profitPct.toFixed(2)}%
                                    </div>
                                </div>

                                <div className="space-y-3">
                                    <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-widest">Investment</label>
                                    <div className="relative">
                                        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 font-mono text-lg">$</span>
                                        <input
                                            className="w-full bg-[#0a110c] border border-slate-800 rounded-xl py-4 pl-10 pr-4 text-white font-mono text-xl focus:ring-1 focus:ring-emerald-primary outline-none"
                                            type="number"
                                            value={investment}
                                            onChange={(e) => setInvestment(Number(e.target.value))}
                                        />
                                    </div>
                                </div>

                                {activeTab === 'arbitrage' && (
                                    <div className="bg-[#0a110c] rounded-xl border border-slate-800/60 overflow-hidden p-4 space-y-4">
                                        <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/5">
                                            <div>
                                                <p className="text-[10px] font-bold text-slate-500 uppercase">{currentItem.book1.name}</p>
                                                <p className="text-sm text-white font-bold">{currentItem.book1.selection} ({currentItem.book1.odds})</p>
                                            </div>
                                            <p className="text-lg font-mono font-bold text-emerald-primary">${wager1.toFixed(2)}</p>
                                        </div>
                                        <div className="flex justify-between items-center bg-white/5 p-3 rounded-lg border border-white/5">
                                            <div>
                                                <p className="text-[10px] font-bold text-slate-500 uppercase">{currentItem.book2.name}</p>
                                                <p className="text-sm text-white font-bold">{currentItem.book2.selection} ({currentItem.book2.odds})</p>
                                            </div>
                                            <p className="text-lg font-mono font-bold text-emerald-primary">${wager2.toFixed(2)}</p>
                                        </div>
                                    </div>
                                )}

                                {activeTab === 'middles' && (
                                    <div className="bg-primary/5 rounded-xl border border-primary/20 p-6 space-y-4">
                                        <div className="text-center">
                                            <p className="text-[10px] font-black text-primary uppercase tracking-widest mb-1">Middle Window</p>
                                            <p className="text-3xl font-black text-white">{currentItem.window}</p>
                                            <p className="text-xs font-bold text-slate-500 mt-1">{currentItem.width} Unit Width</p>
                                        </div>
                                        <div className="grid grid-cols-2 gap-2 text-center">
                                            <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                                                <p className="text-[8px] font-bold text-slate-500 uppercase">{currentItem.over_side.book}</p>
                                                <p className="text-xs font-bold text-white">OVER {currentItem.over_side.line}</p>
                                            </div>
                                            <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                                                <p className="text-[8px] font-bold text-slate-500 uppercase">{currentItem.under_side.book}</p>
                                                <p className="text-xs font-bold text-white">UNDER {currentItem.under_side.line}</p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {activeTab === 'ev' && (
                                    <div className="p-6 rounded-2xl bg-primary/10 border border-primary/20">
                                        <p className="text-xs text-slate-400 mb-2 font-bold uppercase tracking-widest">AI Consensus</p>
                                        <div className="flex justify-between items-end">
                                            <div>
                                                <p className="text-2xl font-black text-white">{currentItem.line_value} {currentItem.side?.toUpperCase()}</p>
                                                <p className="text-sm font-bold text-primary mt-1">{currentItem.odds} Odds</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-[10px] font-bold text-slate-500 uppercase">Confidence</p>
                                                <p className="text-xl font-bold text-emerald-primary">{(currentItem.confidence_score * 100).toFixed(0)}%</p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div className="grid gap-3">
                                    {activeTab === 'arbitrage' ? (
                                        <>
                                            <ExecutionButton book={currentItem.book1.name} />
                                            <ExecutionButton book={currentItem.book2.name} />
                                        </>
                                    ) : activeTab === 'middles' ? (
                                        <>
                                            <ExecutionButton book={currentItem.over_side.book} label="Bet Over" />
                                            <ExecutionButton book={currentItem.under_side.book} label="Bet Under" />
                                        </>
                                    ) : (
                                        <ExecutionButton book={currentItem.sportsbook} label="Place All-In Bet" />
                                    )}
                                </div>
                            </>
                        ) : (
                            <div className="text-center py-20 text-slate-500">Select an opportunity to execute</div>
                        )}
                    </div>

                    <div className="p-6 bg-[#0a110c] border-t border-slate-800/60 rounded-b-2xl">
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-xs text-slate-500">Net Multiplier</span>
                            <span className="text-sm font-mono text-emerald-primary">x{(1 + (profitPct / 100)).toFixed(2)}</span>
                        </div>
                        <div className="p-3 bg-emerald-primary/10 rounded-lg border border-emerald-primary/20 flex items-center justify-center gap-2">
                            <Bolt size={18} className="text-emerald-primary" />
                            <span className="text-emerald-primary font-bold text-sm">
                                {activeTab === 'ev' ? `Exp. Profit: $${netProfit.toFixed(2)}` : `Secured Profit: $${netProfit.toFixed(2)}`}
                            </span>
                        </div>
                    </div>
                </div>
            </aside>
        </div>
    );
}

function SidebarLink({ icon, label, active, onClick }: any) {
    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg font-bold text-sm transition-all border ${active
                ? 'bg-emerald-primary/10 text-emerald-primary border-emerald-primary/20'
                : 'text-slate-500 border-transparent hover:text-white hover:bg-white/5'
                }`}
        >
            {icon}
            <span>{label}</span>
        </button>
    );
}

function ToggleItem({ label, active, onClick }: any) {
    return (
        <label className="flex items-center justify-between group cursor-pointer" onClick={onClick}>
            <span className={`text-[12px] font-bold transition-colors ${active ? 'text-slate-200' : 'text-slate-500 group-hover:text-white'}`}>{label}</span>
            <div className={`w-8 h-4 rounded-full relative transition-colors ${active ? 'bg-emerald-primary/20' : 'bg-slate-800'}`}>
                <div className={`absolute top-0.5 size-3 rounded-full transition-all ${active ? 'right-0.5 bg-emerald-primary shadow-[0_0_8px_rgba(13,242,51,0.5)]' : 'left-0.5 bg-slate-600'}`}></div>
            </div>
        </label>
    );
}

function ValueCard({ tab, data, active, onClick }: any) {
    if (tab === 'arbitrage') {
        return (
            <div
                onClick={onClick}
                className={`group relative bg-[#121e16] hover:bg-[#1a2b20] rounded-xl border p-5 transition-all duration-200 cursor-pointer ${active ? 'border-emerald-primary/40 shadow-[0_0_30px_rgba(13,242,51,0.08)]' : 'border-slate-800/60 hover:border-slate-700'}`}
            >
                <div className="flex flex-col md:flex-row gap-6 items-center">
                    <div className="flex-1 w-full">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="px-2 py-0.5 rounded bg-emerald-primary/10 text-emerald-primary text-[8px] font-black uppercase tracking-widest border border-emerald-primary/20">Arbitrage</div>
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{data.sport} • {data.market}</span>
                        </div>
                        <h3 className="text-lg font-bold text-white group-hover:text-emerald-primary transition-colors">{data.match}</h3>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="text-right">
                            <p className="text-[9px] font-bold text-slate-500 uppercase">Profit</p>
                            <p className="text-2xl font-black text-emerald-primary">{data.profit}</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    if (tab === 'middles') {
        return (
            <div
                onClick={onClick}
                className={`group relative bg-[#121e16] hover:bg-[#1a2b20] rounded-xl border p-5 transition-all duration-200 cursor-pointer ${active ? 'border-primary/40 shadow-[0_0_30px_rgba(13,242,51,0.08)]' : 'border-slate-800/60 hover:border-slate-700'}`}
            >
                <div className="flex flex-col md:flex-row gap-6 items-center">
                    <div className="flex-1 w-full">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="px-2 py-0.5 rounded bg-primary/10 text-primary text-[8px] font-black uppercase tracking-widest border border-primary/20">Middle</div>
                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{data.market}</span>
                        </div>
                        <h3 className="text-lg font-bold text-white group-hover:text-primary transition-colors">{data.game}</h3>
                    </div>
                    <div className="flex items-center gap-6">
                        <div className="text-center">
                            <p className="text-[9px] font-bold text-slate-500 uppercase">Window</p>
                            <p className="text-lg font-black text-white">{data.window}</p>
                        </div>
                        <div className="text-right min-w-[80px]">
                            <p className="text-[9px] font-bold text-slate-500 uppercase">Potential</p>
                            <p className={`text-xl font-black ${data.profit_potential === 'High' ? 'text-emerald-primary' : 'text-amber-500'}`}>{data.profit_potential}</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Default: +EV Prop
    return (
        <div
            onClick={onClick}
            className={`group relative bg-[#121e16] hover:bg-[#1a2b20] rounded-xl border p-5 transition-all duration-200 cursor-pointer ${active ? 'border-emerald-primary/40 shadow-[0_0_30px_rgba(13,242,51,0.08)]' : 'border-slate-800/60 hover:border-slate-700'}`}
        >
            <div className="flex flex-col md:flex-row gap-6 items-center">
                <div className="flex-1 w-full">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="px-2 py-0.5 rounded bg-primary/20 text-primary text-[8px] font-black uppercase tracking-widest border border-primary/20">VAL-EV+</div>
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">{data.sport_label} • {data.market?.stat_type || data.stat_type}</span>
                    </div>
                    <h3 className="text-lg font-bold text-white group-hover:text-primary transition-colors">{data.player_name || data.player?.name}</h3>
                </div>
                <div className="flex items-center gap-4 border-l border-slate-800/60 pl-6">
                    <div className="text-right">
                        <p className="text-[9px] font-bold text-slate-500 uppercase">Edge</p>
                        <p className="text-2xl font-black text-emerald-primary">{(data.edge * 100).toFixed(1)}%</p>
                    </div>
                    <div className="text-right">
                        <p className="text-[9px] font-bold text-slate-500 uppercase">Odds</p>
                        <p className="text-lg font-bold text-white">{data.odds}</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ExecutionButton({ book, label }: any) {
    return (
        <button className="flex flex-col items-center justify-center gap-2 p-4 rounded-xl bg-[#121e16] hover:bg-[#1a2b20] border border-slate-800 hover:border-emerald-primary/30 transition-all group">
            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest group-hover:text-slate-300">{label || `Place Bet @`}</span>
            <div className="flex items-center gap-2 text-white font-bold text-sm">
                <ExternalLink size={16} /> {book}
            </div>
        </button>
    );
}

export default function Arbitrage() {
    return (
        <Suspense fallback={
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="animate-spin text-emerald-primary mb-4" size={32} />
                <p className="text-slate-400 text-sm">Initializing execution feeds...</p>
            </div>
        }>
            <ArbitrageContent />
        </Suspense>
    );
}
