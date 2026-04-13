"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    TrendingUp,
    Target,
    ShieldCheck,
    Clock,
    ArrowUpRight,
    ArrowDownRight,
    ChevronRight,
    Filter,
    Download,
    Share2,
    Loader2,
    Brain,
    Plus,
    X,
    CheckCircle2
} from "lucide-react";
import { api, isApiError } from "@/lib/api";
import { clsx } from "clsx";

export default function LedgerPage() {
    const [bets, setBets] = useState<any[]>([]);
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [selectedSlip, setSelectedSlip] = useState<any>(null);
    const [showShareModal, setShowShareModal] = useState(false);
    const [showAddModal, setShowAddModal] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form State for Manual Entry
    const [newBet, setNewBet] = useState({
        player_name: "",
        market_key: "",
        line: "",
        odds: "-110",
        stake: "1",
        sportsbook: "DraftKings",
        side: "Over"
    });

    const fetchData = async () => {
        setLoading(true);
        try {
            const [betsRes, statsRes] = await Promise.all([
                (api as any).ledgerMyBets(),
                (api as any).ledgerStats()
            ]);

            if (!isApiError(betsRes)) setBets(betsRes || []);
            if (!isApiError(statsRes)) setStats(statsRes);
        } catch (err) {
            console.error("Failed to fetch ledger data:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleAddBet = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            const res = await (api as any).ledgerCreateBet({
                ...newBet,
                line: Number(newBet.line),
                odds: Number(newBet.odds),
                stake: Number(newBet.stake)
            });
            if (!isApiError(res)) {
                setShowAddModal(false);
                fetchData();
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    // ROI calculation: (Profit / Total Staked) * 100
    const calculatedROI = stats?.total_staked > 0 
        ? ((stats.profit_loss / stats.total_staked) * 100).toFixed(1)
        : stats?.roi ? (stats.roi * 100).toFixed(1) : '0.0';

    if (loading) {
        return (
            <div className="h-[60vh] flex flex-col items-center justify-center space-y-4">
                <Loader2 className="animate-spin text-brand-primary" size={40} />
                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-textMuted animate-pulse">Syncing Ledger...</p>
            </div>
        );
    }

    return (
        <div className="pb-32 space-y-10 pt-10 px-6 max-w-[1400px] mx-auto text-white">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/5 pb-10">
                <div>
                  <h1 className="text-4xl font-black italic tracking-tighter uppercase font-display leading-none mb-2">
                      Intelligence <span className="text-brand-primary">Ledger</span>
                  </h1>
                  <p className="text-textMuted text-xs font-bold uppercase tracking-widest italic">Institutional Bankroll & ROI Tracker</p>
                </div>
                <div className="flex gap-4">
                    <button 
                        onClick={() => setShowAddModal(true)}
                        className="flex items-center gap-2 px-6 py-3 bg-brand-primary text-white font-black rounded-xl text-xs hover:bg-brand-primary/90 transition-all shadow-xl shadow-brand-primary/20"
                    >
                        <Plus size={16} /> MANUAL ENTRY
                    </button>
                    <button className="flex items-center gap-2 px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest text-textMuted hover:text-white hover:bg-white/10 transition-all">
                        <Download size={14} /> EXPORT CSV
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    label="Net Profit"
                    value={`$${stats?.profit_loss?.toLocaleString() || '0.00'}`}
                    trend={stats?.profit_loss >= 0 ? "Profit" : "Drawdown"}
                    color={stats?.profit_loss >= 0 ? "emerald" : "red"}
                    icon={stats?.profit_loss >= 0 ? <ArrowUpRight size={20} /> : <ArrowDownRight size={20} />}
                />
                <StatCard
                    label="Yield (ROI)"
                    value={`${calculatedROI}%`}
                    trend="Efficiency"
                    color="primary"
                    icon={<TrendingUp size={20} />}
                />
                <StatCard
                    label="Win Rate"
                    value={`${stats?.win_rate?.toFixed(1) || '0.0'}%`}
                    trend="Market Accuracy"
                    color="blue"
                    icon={<ShieldCheck size={20} />}
                />
                <StatCard
                    label="Volume"
                    value={stats?.total_bets || '0'}
                    trend="Tracked Units"
                    color="slate"
                    icon={<Clock size={20} />}
                />
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-10">
                <div className="xl:col-span-2 space-y-6">
                   <div className="bg-lucrix-surface border border-white/10 rounded-3xl overflow-hidden shadow-card">
                      <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between bg-lucrix-dark/30">
                          <h3 className="text-sm font-black text-white flex items-center gap-2 uppercase tracking-widest italic">
                              <Brain size={16} className="text-brand-primary shadow-glow shadow-brand-primary/50" /> Placement Log
                          </h3>
                      </div>
                      <div className="overflow-x-auto">
                          <table className="w-full text-left">
                              <thead className="text-[9px] text-textMuted font-black uppercase tracking-widest bg-white/[0.02]">
                                  <tr>
                                      <th className="px-8 py-5">Date</th>
                                      <th className="px-8 py-5">Market / Selection</th>
                                      <th className="px-8 py-5">Book</th>
                                      <th className="px-8 py-5">Odds</th>
                                      <th className="px-8 py-5 text-right">Result</th>
                                  </tr>
                              </thead>
                              <tbody className="divide-y divide-white/5">
                                  {bets.length > 0 ? (
                                      bets.map((bet, i) => (
                                          <tr key={i} className="hover:bg-white/[0.02] transition-colors group">
                                              <td className="px-8 py-5">
                                                  <p className="text-[11px] text-white font-bold">{new Date(bet.placed_at || bet.created_at).toLocaleDateString()}</p>
                                                  <p className="text-[9px] text-textMuted uppercase font-mono">{new Date(bet.placed_at || bet.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                                              </td>
                                              <td className="px-8 py-5">
                                                  <p className="text-xs font-black text-white uppercase italic">{bet.player_name || bet.selection || 'General Market'}</p>
                                                  <p className="text-[9px] text-textMuted uppercase font-bold tracking-widest">{bet.market_key || bet.slip_type}</p>
                                              </td>
                                              <td className="px-8 py-5">
                                                  <span className="text-[10px] font-black text-brand-primary/80 uppercase italic">{bet.sportsbook}</span>
                                              </td>
                                              <td className="px-8 py-5">
                                                  <span className="font-mono text-xs font-black text-brand-primary">{bet.odds || bet.total_odds > 0 ? `+${bet.odds || bet.total_odds}` : bet.odds || bet.total_odds}</span>
                                              </td>
                                              <td className="px-8 py-5 text-right">
                                                  <span className={clsx(
                                                      "px-3 py-1 rounded text-[9px] font-black uppercase tracking-widest",
                                                      bet.status === 'won' || bet.status === 'HIT' ? 'bg-brand-success/10 text-brand-success' :
                                                      bet.status === 'lost' || bet.status === 'MISS' ? 'bg-brand-danger/10 text-brand-danger' :
                                                      'bg-white/5 text-textMuted'
                                                  )}>
                                                      {bet.status}
                                                  </span>
                                              </td>
                                          </tr>
                                      ))
                                  ) : (
                                      <tr>
                                          <td colSpan={5} className="py-24 text-center text-textMuted font-black uppercase italic tracking-widest text-[10px]">
                                              No intelligence data recorded in this cycle.
                                          </td>
                                      </tr>
                                  )}
                              </tbody>
                          </table>
                      </div>
                   </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    <div className="bg-lucrix-surface border border-white/10 p-8 rounded-3xl shadow-card">
                        <h3 className="text-xs font-black text-white mb-8 flex items-center gap-2 uppercase tracking-widest">
                            <Target size={16} className="text-brand-primary" /> Sector Allocation
                        </h3>
                        <div className="space-y-6">
                            <ExposureBar label="NBA Props" percent={stats?.allocation?.nba || 65} color="bg-brand-primary" />
                            <ExposureBar label="College Hoops" percent={stats?.allocation?.ncaa || 20} color="bg-blue-500" />
                            <ExposureBar label="Sharp Moves" percent={stats?.allocation?.sharp || 15} color="bg-emerald-500" />
                        </div>
                    </div>

                    <div className="bg-gradient-to-br from-brand-primary/20 to-transparent border border-brand-primary/20 p-8 rounded-3xl shadow-glow shadow-brand-primary/10">
                        <div className="flex items-center gap-3 mb-4">
                            <Brain size={20} className="text-brand-primary" />
                            <h3 className="text-xs font-black text-white uppercase tracking-widest">Neural Advisory</h3>
                        </div>
                        <p className="text-[11px] font-bold text-textSecondary leading-relaxed italic">
                            Your closing line edge is currently trending <span className="text-brand-success font-black">+4.2%</span>. 
                            Institutional volume is flow-correlated on your over-sized units. Maintain discipline.
                        </p>
                    </div>
                </div>
            </div>

            {/* Manual Entry Modal */}
            <AnimatePresence>
                {showAddModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-6">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setShowAddModal(false)}
                            className="absolute inset-0 bg-lucrix-dark/90 backdrop-blur-md"
                        />
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            className="relative w-full max-w-xl bg-lucrix-surface border border-white/10 p-10 rounded-[2.5rem] shadow-2xl"
                        >
                            <button 
                                onClick={() => setShowAddModal(false)} 
                                className="absolute top-8 right-8 text-textMuted hover:text-white transition-colors"
                                title="Close Modal"
                            >
                                <X size={20} />
                            </button>

                            <div className="flex items-center gap-4 mb-10">
                                <div className="p-3 bg-brand-primary/10 border border-brand-primary/20 rounded-2xl text-brand-primary shadow-glow shadow-brand-primary/20">
                                    <Plus size={24} />
                                </div>
                                <div>
                                    <h2 className="text-2xl font-black text-white italic uppercase tracking-tighter leading-none">Record Entry</h2>
                                    <p className="text-[9px] text-textMuted font-black uppercase tracking-[0.2em] mt-2">Manual Intelligence Override</p>
                                </div>
                            </div>

                            <form onSubmit={handleAddBet} className="space-y-6">
                                <div className="grid grid-cols-2 gap-6">
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-textMuted uppercase tracking-widest">Player / Team</label>
                                        <input 
                                            type="text" 
                                            required
                                            value={newBet.player_name}
                                            onChange={(e) => setNewBet({...newBet, player_name: e.target.value})}
                                            className="w-full bg-lucrix-dark/50 border border-white/10 rounded-xl px-4 py-3 text-xs font-bold text-white focus:border-brand-primary/50 outline-none" 
                                            placeholder="e.g. LeBron James"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-textMuted uppercase tracking-widest">Market</label>
                                        <input 
                                            type="text" 
                                            required
                                            value={newBet.market_key}
                                            onChange={(e) => setNewBet({...newBet, market_key: e.target.value})}
                                            className="w-full bg-lucrix-dark/50 border border-white/10 rounded-xl px-4 py-3 text-xs font-bold text-white focus:border-brand-primary/50 outline-none" 
                                            placeholder="e.g. Points"
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-3 gap-6">
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-textMuted uppercase tracking-widest">Line</label>
                                        <input 
                                            type="number" 
                                            step="0.5"
                                            required
                                            value={newBet.line}
                                            onChange={(e) => setNewBet({...newBet, line: e.target.value})}
                                            className="w-full bg-lucrix-dark/50 border border-white/10 rounded-xl px-4 py-3 text-xs font-bold text-white focus:border-brand-primary/50 outline-none" 
                                            placeholder="e.g. 25.5"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-textMuted uppercase tracking-widest">Odds</label>
                                        <input 
                                            type="text" 
                                            required
                                            value={newBet.odds}
                                            onChange={(e) => setNewBet({...newBet, odds: e.target.value})}
                                            className="w-full bg-lucrix-dark/50 border border-white/10 rounded-xl px-4 py-3 text-xs font-bold text-white focus:border-brand-primary/50 outline-none" 
                                            placeholder="-110"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-[10px] font-black text-textMuted uppercase tracking-widest">Size (Units)</label>
                                        <input 
                                            type="number" 
                                            required
                                            value={newBet.stake}
                                            onChange={(e) => setNewBet({...newBet, stake: e.target.value})}
                                            className="w-full bg-lucrix-dark/50 border border-white/10 rounded-xl px-4 py-3 text-xs font-bold text-white focus:border-brand-primary/50 outline-none" 
                                            placeholder="1.0"
                                        />
                                    </div>
                                </div>

                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="w-full py-5 bg-brand-primary text-white font-black rounded-2xl hover:bg-brand-primary/90 transition-all shadow-xl shadow-brand-primary/20 disabled:opacity-50 flex items-center justify-center gap-2 uppercase tracking-widest text-xs"
                                >
                                    {isSubmitting ? <Loader2 className="animate-spin" /> : <>LOCK ENTRY <CheckCircle2 size={16} /></>}
                                </button>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}

function StatCard({ label, value, trend, color, icon }: any) {
    const colorStyles: Record<string, string> = {
        emerald: "text-brand-success border-brand-success/20 bg-brand-success/5 shadow-brand-success/5",
        red: "text-brand-danger border-brand-danger/20 bg-brand-danger/5 shadow-brand-danger/5",
        primary: "text-brand-primary border-brand-primary/20 bg-brand-primary/5 shadow-brand-primary/5",
        blue: "text-blue-400 border-blue-400/20 bg-blue-400/5 shadow-blue-400/5",
        slate: "text-textMuted border-white/10 bg-white/5"
    };

    return (
        <motion.div
            whileHover={{ y: -4 }}
            className={clsx(
                "p-8 rounded-3xl border backdrop-blur-sm transition-all shadow-lg",
                colorStyles[color]
            )}
        >
            <div className="flex justify-between items-start mb-6">
                <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-60 leading-none">{label}</span>
                <div className="opacity-40">{icon}</div>
            </div>
            <div className="flex flex-col">
                <span className="text-3xl font-black italic font-display leading-none">{value}</span>
                <span className="text-[9px] font-black uppercase tracking-widest mt-3 opacity-60 flex items-center gap-1.5 italic">
                    <span className="w-1 h-1 rounded-full bg-current" /> {trend}
                </span>
            </div>
        </motion.div>
    );
}

function ExposureBar({ label, percent, color }: any) {
    return (
        <div className="space-y-3">
            <div className="flex justify-between text-[9px] font-black uppercase tracking-widest italic">
                <span className="text-textMuted">{label}</span>
                <span className="text-white">{percent}%</span>
            </div>
            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${percent}%` }}
                    viewport={{ once: true }}
                    className={clsx("h-full rounded-full shadow-glow uppercase", color)}
                />
            </div>
        </div>
    );
}
