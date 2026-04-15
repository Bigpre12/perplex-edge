// apps/web/src/app/(app)/player/[id]/page.tsx
"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import API, { isApiError } from "@/lib/api";

interface PlayerProfile {
    player_name: string;
    team: string;
    sport: string;
    position: string;
    injury_status: string | null;
    stats: StatLine[];
    props: PropLine[];
    hit_rates: HitRate[];
}

interface StatLine {
    game_date: string;
    opponent: string;
    stat_type: string;
    value: number;
}

interface PropLine {
    stat_type: string;
    line: number;
    pick: string;
    odds: number;
    ev_percentage: number;
    confidence: string;
    book: string;
}

interface HitRate {
    stat_type: string;
    hit_rate: number;
    total_picks: number;
    hits: number;
    avg_ev: number;
}

export default function PlayerProfilePage() {
    const params = useParams();
    const id = params?.id;
    const playerName = decodeURIComponent(id as string).replace(/-/g, " ");
    const [profile, setProfile] = useState<PlayerProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<"props" | "stats" | "hitrate">("props");

    useEffect(() => {
        if (!playerName) return;
        const fetchProfile = async () => {
            try {
                const data = await API.playerProfile(playerName);
                if (!isApiError(data)) {
                    setProfile(data);
                } else {
                    setProfile(null);
                }
            } catch {
                setProfile(null);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [playerName]);

    if (loading) return (
        <div className="min-h-screen bg-[#0f1117] flex items-center justify-center text-slate-500 font-bold uppercase tracking-widest animate-pulse">
            Loading player...
        </div>
    );
    
    if (!profile) return (
        <div className="min-h-screen bg-[#0f1117] flex items-center justify-center text-slate-500 font-bold uppercase tracking-widest">
            Player not found.
        </div>
    );

    const tabClass = (active: boolean) => `
        px-5 py-2 rounded-lg transition-all duration-200
        ${active ? "bg-[#6366f1] text-white shadow-[0_0_15px_rgba(99,102,241,0.3)]" : "bg-transparent text-slate-500 hover:text-slate-300"}
        text-[13px] font-bold cursor-pointer
    `;

    return (
        <div className="min-h-screen bg-[#0f1117] p-6 text-white pb-24">
            <div className="max-w-[900px] mx-auto">

                {/* Header */}
                <div className="bg-[#1a1d2e] rounded-xl p-6 border border-[#2d3748] mb-5 group hover:border-[#6366f1]/30 transition-colors">
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-3xl font-black m-0 tracking-tight italic uppercase">{profile.player_name}</h1>
                            <div className="text-sm text-slate-400 mt-1 font-bold uppercase tracking-widest flex items-center gap-2">
                                <span className="text-[#6366f1]">{profile.team}</span>
                                <span className="opacity-30">/</span>
                                <span>{profile.sport}</span>
                                <span className="opacity-30">/</span>
                                <span>{profile.position}</span>
                            </div>
                        </div>
                        {profile.injury_status && (
                            <span className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-[#7f1d1d] text-[#f87171] border border-[#f87171]/20">
                                🚑 {profile.injury_status}
                            </span>
                        )}
                    </div>

                    {/* Hit rate summary */}
                    <div className="flex gap-4 mt-6 flex-wrap">
                        {profile.hit_rates.slice(0, 4).map((hr, i) => (
                            <div key={i} className="bg-[#0f1117] rounded-lg p-4 min-w-[130px] border border-white/5 hover:border-white/10 transition-all">
                                <div className="text-[10px] text-slate-500 font-black tracking-widest uppercase mb-1">
                                    {hr.stat_type}
                                </div>
                                <div className={`text-2xl font-black ${hr.hit_rate >= 65 ? "text-[#10b981]" : hr.hit_rate >= 55 ? "text-[#60a5fa]" : "text-white"}`}>
                                    {hr.hit_rate}%
                                </div>
                                <div className="text-[10px] text-slate-600 font-bold mt-1 uppercase tracking-tighter">{hr.hits}/{hr.total_picks} PICKS</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-1 mb-6 bg-[#1a1d2e] rounded-xl p-1 border border-[#2d3748]">
                    <button className={tabClass(activeTab === "props")} onClick={() => setActiveTab("props")}>Today's Props</button>
                    <button className={tabClass(activeTab === "stats")} onClick={() => setActiveTab("stats")}>Recent Stats</button>
                    <button className={tabClass(activeTab === "hitrate")} onClick={() => setActiveTab("hitrate")}>Hit Rates</button>
                </div>

                {/* Props tab */}
                {activeTab === "props" && (
                    <div className="grid gap-3">
                        {profile.props.length === 0 && (
                            <div className="text-slate-500 text-center py-16 bg-[#1a1d2e] rounded-xl border border-dashed border-[#2d3748] font-bold italic">
                                No props available for today's slate.
                            </div>
                        )}
                        {profile.props.map((prop, i) => (
                            <div key={i} className="bg-[#1a1d2e] rounded-xl p-5 border border-[#2d3748] flex justify-between items-center group hover:border-[#10b981]/30 transition-all">
                                <div>
                                    <div className="text-[15px] font-black italic uppercase tracking-tight">
                                        {prop.stat_type} <span className="text-[#6366f1]">{prop.pick}</span> {prop.line}
                                    </div>
                                    <div className="text-xs text-slate-500 font-bold uppercase tracking-widest mt-1 opacity-60">{prop.book}</div>
                                </div>
                                <div className="text-2xl font-black text-[#10b981] drop-shadow-[0_0_10px_rgba(16,185,129,0.2)]">
                                    {prop.ev_percentage > 0 ? "+" : ""}{prop.ev_percentage}% <span className="text-[10px] opacity-60">EV</span>
                                </div>
                                <div className="text-right">
                                    <div className="text-lg font-black">{prop.odds > 0 ? `+${prop.odds}` : prop.odds}</div>
                                    <div className={`
                                        mt-1 px-2.5 py-0.5 rounded text-[10px] font-black tracking-widest
                                        ${prop.confidence === "HIGH" ? "bg-[#10b981]/10 text-[#10b981]" : "bg-slate-800 text-slate-400"}
                                    `}>
                                        {prop.confidence}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Stats tab */}
                {activeTab === "stats" && (
                    <div className="bg-[#1a1d2e] rounded-xl border border-[#2d3748] overflow-hidden shadow-xl">
                        <table className="w-full border-collapse">
                            <thead>
                                <tr className="bg-[#111827]">
                                    {["Date", "Opponent", "Stat", "Value"].map(h => (
                                        <th key={h} className="p-4 px-6 text-[10px] text-slate-500 font-black uppercase tracking-widest text-left">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {profile.stats.map((s, i) => (
                                    <tr key={i} className="border-t border-[#1f2937] hover:bg-white/[0.02] transition-colors">
                                        <td className="p-4 px-6 text-xs text-slate-400 font-medium">{new Date(s.game_date).toLocaleDateString()}</td>
                                        <td className="p-4 px-6 text-sm font-black italic uppercase tracking-tight text-white">{s.opponent}</td>
                                        <td className="p-4 px-6 text-xs text-slate-400 font-bold uppercase tracking-tighter">{s.stat_type}</td>
                                        <td className="p-4 px-6 text-lg font-black text-white">{s.value}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Hit rate tab */}
                {activeTab === "hitrate" && (
                    <div className="grid gap-3">
                        {profile.hit_rates.map((hr, i) => (
                            <div key={i} className="bg-[#1a1d2e] rounded-xl p-5 border border-[#2d3748] flex justify-between items-center group hover:border-[#6366f1]/30 transition-all">
                                <div className="text-[15px] font-black uppercase italic tracking-tight">{hr.stat_type}</div>
                                <div className={`text-3xl font-black ${hr.hit_rate >= 65 ? "text-[#10b981]" : hr.hit_rate >= 55 ? "text-[#60a5fa]" : "text-white"}`}>
                                    {hr.hit_rate}%
                                </div>
                                <div className="text-right">
                                    <div className="text-xs font-black italic text-slate-400 uppercase">{hr.hits}/{hr.total_picks} hits</div>
                                    <div className="text-[10px] text-slate-600 font-bold uppercase mt-0.5 tracking-tighter">Avg EV: +{hr.avg_ev}%</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
