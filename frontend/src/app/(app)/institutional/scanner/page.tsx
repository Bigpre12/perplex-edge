"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Radar,
    Search,
    Zap,
    TrendingUp,
    BarChart3,
    Clock,
    Filter,
    ArrowUpRight,
    ArrowDownRight,
    Loader2,
    ShieldAlert,
    Activity,
    Server,
    Globe,
    Share2,
    CheckCircle2
} from "lucide-react";
import { getAuthToken } from "@/lib/auth";
import { API_BASE_URL, API_ENDPOINTS } from "@/lib/apiConfig";

const SPORTS_TO_SCAN = [
    { key: 'basketball_nba', name: 'NBA', icon: 'sports_basketball' },
    { key: 'icehockey_nhl', name: 'NHL', icon: 'sports_hockey' },
    { key: 'americanfootball_nfl', name: 'NFL', icon: 'sports_football' },
    { key: 'baseball_mlb', name: 'MLB', icon: 'sports_baseball' }
];

export default function InstitutionalScanner() {
    const [allProps, setAllProps] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeFilters, setActiveFilters] = useState<string[]>(['high_ev', 'institutional']);
    const [scanProgress, setScanProgress] = useState(0);

    const fetchAllSports = async () => {
        setLoading(true);
        setScanProgress(0);
        let consolidated: any[] = [];
        const token = getAuthToken();

        try {
            for (let i = 0; i < SPORTS_TO_SCAN.length; i++) {
                const sport = SPORTS_TO_SCAN[i];
                const res = await fetch(`${API_ENDPOINTS.ODDS}?sport_key=${sport.key}&limit=20`, {
                    headers: {
                        ...(token ? { "Authorization": `Bearer ${token}` } : {})
                    }
                });
                if (res.ok) {
                    const data = await res.json();
                    const items = (data.items || []).map((p: any) => ({
                        ...p,
                        sport_display: sport.name,
                        steam_pressure: Math.random() * 100, // Mocked steam
                        liquidity: Math.random() > 0.5 ? 'High' : 'Medium'
                    }));
                    consolidated = [...consolidated, ...items];
                }
                setScanProgress(((i + 1) / SPORTS_TO_SCAN.length) * 100);
            }
            setAllProps(consolidated.sort((a, b) => (b.ev_percent || 0) - (a.ev_percent || 0)));
        } catch (err) {
            console.error("Scanner failed:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSignal = async (prop: any) => {
        const token = getAuthToken();
        try {
            await fetch(API_ENDPOINTS.SIGNAL, {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(prop)
            });
            alert("Signal dispatched to secure relay.");
        } catch (err) {
            console.error("Signal failed:", err);
        }
    };

    const handleQuickTrack = async (prop: any) => {
        const token = getAuthToken();
        try {
            // Mocking the track-bet endpoint call
            await fetch(`${API_ENDPOINTS.LEDGER}/track`, {
                method: 'POST',
                headers: {
                    "Authorization": `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    prop_id: prop.id,
                    side: prop.side,
                    odds_taken: prop.odds_taken || prop.odds,
                    line_taken: prop.line_value || prop.line,
                    sportsbook: prop.sportsbook
                })
            });
            alert("Prop tracked successfully in personal ledger.");
        } catch (err) {
            console.error("Track failed:", err);
        }
    };

    useEffect(() => {
        fetchAllSports();
        const interval = setInterval(fetchAllSports, 60000); // Auto-refresh every minute
        return () => clearInterval(interval);
    }, []);

    const filteredProps = allProps.filter(p => {
        if (activeFilters.includes('high_ev') && (p.ev_percent || 0) < 5) return false;
        return true;
    });

    return (
        <div className="space-y-8 pb-12">
            {/* Command Header */}
            <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-primary/20 rounded-lg text-primary animate-pulse">
                            <Radar size={24} />
                        </div>
                        <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic">Institutional Command Center</h1>
                    </div>
                    <p className="text-secondary text-sm font-medium flex items-center gap-2">
                        <Globe size={14} className="text-emerald-500" /> Scanning global markets for multi-asset steam pressure
                    </p>
                </div>

                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                    <ScannerMetric label="Global Latency" value="14ms" status="Optimal" />
                    <ScannerMetric label="Sharp Consensus" value="Strong" status="Aggressive" />
                    <ScannerMetric label="Active Edges" value={filteredProps.length.toString()} status="Live" />
                    <button
                        onClick={fetchAllSports}
                        className="px-6 py-3 bg-primary text-background-dark font-black rounded-xl hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-2"
                    >
                        {loading ? <Loader2 className="animate-spin" size={18} /> : <Zap size={18} />}
                        FORCE RE-SCAN
                    </button>
                </div>
            </div>

            {/* Scan Progress Bar */}
            <AnimatePresence>
                {loading && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="w-full h-1 bg-slate-900 rounded-full overflow-hidden"
                    >
                        <motion.div
                            className="h-full bg-primary shadow-[0_0_10px_#0df233]"
                            animate={{ width: `${scanProgress}%` }}
                        />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Main Scanner Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Real-time Feed */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="flex items-center justify-between px-2">
                        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] flex items-center gap-2">
                            <Activity size={14} /> High-Intensity Market Feed
                        </h3>
                        <div className="flex gap-2">
                            {['NBA', 'NHL', 'NFL'].map(s => (
                                <span key={s} className="text-[10px] font-bold text-slate-400 bg-white/5 px-2 py-0.5 rounded border border-white/10 uppercase">{s}</span>
                            ))}
                        </div>
                    </div>

                    <div className="glass-premium rounded-3xl border-white/[0.05] overflow-hidden">
                        <table className="w-full text-left">
                            <thead className="bg-white/[0.02] border-b border-white/[0.05]">
                                <tr>
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Market / Asset</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">Steam Pressure</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-center">Edge EV</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Liquidity</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/[0.03]">
                                {filteredProps.map((prop, i) => (
                                    <ScannerRow
                                        key={i}
                                        prop={prop}
                                        onQuickTrack={handleQuickTrack}
                                        onSignal={handleSignal}
                                    />
                                ))}
                                {filteredProps.length === 0 && !loading && (
                                    <tr>
                                        <td colSpan={4} className="py-20 text-center text-slate-500 italic text-sm">
                                            No institutional-grade edges identified in current scan cycle.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Intelligence Sidebar */}
                <div className="space-y-6">
                    <div className="glass-panel p-6 rounded-3xl border-white/[0.05] bg-gradient-to-br from-[#0c1416]/50 to-transparent">
                        <h3 className="text-sm font-black text-white mb-6 flex items-center gap-2 italic">
                            <ShieldAlert size={18} className="text-amber-400" /> RISK INTELLIGENCE ALERT
                        </h3>
                        <div className="space-y-4">
                            <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20">
                                <p className="text-xs font-bold text-amber-500 mb-1 tracking-tight">Market Volatility Warning</p>
                                <p className="text-[10px] text-slate-300 leading-relaxed">
                                    Severe steam pressure detected in NBA Rebounds market. Institutional sharps are aggressive on Underdog lines. Proceed with cautious units.
                                </p>
                            </div>
                            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
                                <p className="text-xs font-bold text-emerald-500 mb-1 tracking-tight">High Liquidity Opportunuty</p>
                                <p className="text-[10px] text-slate-300 leading-relaxed">
                                    NHL Moneyline markets at BetRivers showing 15% discrepancy vs Sharp Model consensus. High execution probability.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="glass-panel p-6 rounded-3xl border-white/[0.05]">
                        <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-6">System Health</h3>
                        <div className="space-y-4">
                            <SystemHeartbeat label="FastAPI Hub" status="Healthy" load="12%" />
                            <SystemHeartbeat label="PostgreSQL DB" status="Healthy" load="4%" />
                            <SystemHeartbeat label="ML Ingestor" status="Healthy" load="84%" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ScannerRow({ prop, onQuickTrack, onSignal }: any) {
    return (
        <motion.tr
            whileHover={{ backgroundColor: 'rgba(255,255,255,0.02)' }}
            className="group cursor-default"
        >
            <td className="px-6 py-5">
                <div className="flex items-center gap-4">
                    <div className="size-10 rounded-xl bg-surface border border-white/5 flex items-center justify-center text-primary group-hover:bg-primary/10 group-hover:border-primary/20 transition-all">
                        <span className="material-symbols-outlined text-xl">
                            {prop.sport_display === 'NBA' ? 'sports_basketball' : 'sports_hockey'}
                        </span>
                    </div>
                    <div>
                        <div className="flex items-center gap-2">
                            <p className="text-sm font-black text-white">{prop.player_name || prop.player?.name}</p>
                            <span className="text-[9px] font-black bg-white/5 text-slate-400 px-1.5 py-0.5 rounded border border-white/10 uppercase tracking-tighter">
                                {prop.sport_display}
                            </span>
                        </div>
                        <p className="text-[10px] text-secondary font-bold uppercase mt-0.5">
                            {prop.side === 'over' ? 'OVER' : 'UNDER'} {prop.line_value || prop.line} {prop.stat_type || prop.market?.stat_type}
                        </p>
                    </div>
                </div>
            </td>
            <td className="px-6 py-5 text-center">
                <div className="flex flex-col items-center gap-1.5">
                    <div className="h-1 w-20 bg-slate-800 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${prop.steam_pressure}%` }}
                            className={`h-full ${prop.steam_pressure > 70 ? 'bg-red-500 shadow-[0_0_5px_rgba(239,68,68,0.5)]' : 'bg-primary'}`}
                        />
                    </div>
                    <span className="text-[10px] font-black text-slate-500 uppercase">
                        {prop.steam_pressure > 70 ? 'High Steam' : 'Stable'}
                    </span>
                </div>
            </td>
            <td className="px-6 py-5 text-center">
                <div className="inline-flex flex-col items-center">
                    <span className="text-lg font-black text-primary italic">+{prop.ev_percent || prop.edge * 100}%</span>
                    <span className="text-[9px] font-bold text-emerald-500/60 uppercase">High Edge</span>
                </div>
            </td>
            <td className="px-6 py-5 text-right">
                <div className="flex items-center justify-end gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        onClick={() => onQuickTrack(prop)}
                        className="p-2 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 rounded-lg text-emerald-500 transition-all"
                        title="Quick Track"
                    >
                        <CheckCircle2 size={16} />
                    </button>
                    <button
                        onClick={() => onSignal(prop)}
                        className="p-2 bg-primary/10 hover:bg-primary/20 border border-primary/20 rounded-lg text-primary transition-all"
                        title="Dispatch Signal"
                    >
                        <Share2 size={16} />
                    </button>
                    <div className="flex flex-col items-end min-w-[80px]">
                        <p className={`text-xs font-black uppercase ${prop.liquidity === 'High' ? 'text-emerald-500' : 'text-amber-500'}`}>
                            {prop.liquidity}
                        </p>
                        <p className="text-[10px] text-slate-500 font-mono">{prop.sportsbook}</p>
                    </div>
                </div>
            </td>
        </motion.tr>
    );
}

function ScannerMetric({ label, value, status }: any) {
    return (
        <div className="glass-premium px-5 py-3 rounded-2xl border-white/5 flex flex-col justify-center">
            <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-1">{label}</p>
            <div className="flex items-center justify-between">
                <span className="text-lg font-black text-white">{value}</span>
                <span className={`text-[9px] font-black px-1.5 py-0.5 rounded ${status === 'Aggressive' ? 'text-red-500 bg-red-500/10' : 'text-primary bg-primary/10'}`}>
                    {status}
                </span>
            </div>
        </div>
    );
}

function SystemHeartbeat({ label, status, load }: any) {
    return (
        <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
                <Server size={12} className="text-slate-500" />
                <span className="text-xs font-bold text-slate-300">{label}</span>
            </div>
            <div className="flex items-center gap-4">
                <span className="text-[10px] font-mono text-slate-500">LOAD: {load}</span>
                <div className="size-2 rounded-full bg-primary shadow-[0_0_5px_#0df233]"></div>
            </div>
        </div>
    );
}
