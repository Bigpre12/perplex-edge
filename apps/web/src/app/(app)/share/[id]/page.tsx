"use client";
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Share2, ArrowLeft, Brain, Info, Download, Image as ImageIcon } from 'lucide-react';
import { SportsbookDeeplinks } from '@/components/SportsbookDeeplinks';
import MatchupIntelligence from '@/components/MatchupIntelligence';
import { SocialShareCard } from '@/components/SocialShareCard';
import { exportComponentAsImage } from '@/utils/shareExporter';
import { API_BASE as API_BASE_URL } from "@/lib/api";

export default function TailLink() {
    const { id } = useParams();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [exporting, setExporting] = useState(false);

    const handleDownloadGraphic = async () => {
        if (!data || exporting) return;
        setExporting(true);
        try {
            const fileName = `perplex-edge-${(data.player?.name || data.playerName).replace(/\s+/g, '-').toLowerCase()}.png`;
            await exportComponentAsImage('social-share-card', fileName, 2);
        } catch (err) {
            console.error("Export failed:", err);
            alert("Failed to generate graphic. Please try again.");
        } finally {
            setExporting(false);
        }
    };

    useEffect(() => {
        const fetchShare = async () => {
            try {
                const res = await fetch(`/api/share/${id}`);
                if (!res.ok) throw new Error("Link expired or invalid");
                const json = await res.json();
                setData(json.data);
            } catch (err: any) {
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError("An unknown error occurred");
                }
            } finally {
                setLoading(false);
            }
        };
        fetchShare();
    }, [id]);

    if (loading) {
        return (
            <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
                <div className="size-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                <p className="text-slate-500 font-bold animate-pulse">Retrieving Shared Intelligence...</p>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="min-h-[60vh] flex flex-col items-center justify-center gap-4">
                <div className="p-4 rounded-full bg-red-500/10 text-red-500">
                    <Info size={32} />
                </div>
                <h1 className="text-xl font-bold text-white">Share Link Expired</h1>
                <p className="text-slate-500">This tail link is no longer active or was moved.</p>
                <Link href="/props" className="mt-4 px-6 py-2 bg-primary text-background-dark font-bold rounded-lg uppercase text-xs tracking-widest">
                    Back to Feed
                </Link>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto py-12 px-4 space-y-8">
            <Link href="/props" className="inline-flex items-center gap-2 text-slate-500 hover:text-white transition-colors text-sm font-bold group">
                <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" /> Back to Tools
            </Link>

            <div className="glass-panel p-8 rounded-3xl border-primary/20 bg-primary/5 space-y-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
                    <Share2 size={120} />
                </div>

                <div className="flex items-center gap-6">
                    <img
                        src={`https://ui-avatars.com/api/?name=${encodeURIComponent(data.player?.name || data.playerName)}&background=101f19&color=0df233`}
                        className="size-20 rounded-full border-2 border-primary/30 shadow-2xl shadow-primary/20"
                        alt=""
                    />
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="px-2 py-0.5 rounded bg-primary/20 text-primary text-[10px] font-black uppercase tracking-widest">Shared Tail</span>
                            <span className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">{data.sport || 'NBA'} • {data.player?.team || 'PRO'}</span>
                        </div>
                        <h1 className="text-3xl font-black text-white tracking-tight leading-none">{data.player?.name || data.playerName}</h1>
                        <p className="text-slate-400 font-bold uppercase text-xs mt-2 tracking-widest">{data.player?.position || 'PLAYER'}</p>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/5">
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em] mb-2">Market</p>
                        <p className="text-xl font-black text-white">{data.market?.stat_type || data.statType || 'Prop'}</p>
                        <p className="text-sm font-bold text-primary mt-1">{data.side?.toUpperCase() || 'OVER'} {data.line_value || data.line}</p>
                    </div>
                    <div className="p-6 rounded-2xl bg-white/[0.03] border border-white/5">
                        <p className="text-[10px] text-slate-500 font-black uppercase tracking-[0.2em] mb-2">Edge</p>
                        <p className="text-xl font-black text-emerald-primary">{data.edge ? (data.edge * 100).toFixed(1) : '8.4'}%</p>
                        <p className="text-sm font-bold text-slate-400 mt-1">{data.odds || '-110'} Odds</p>
                    </div>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center gap-2">
                        <Brain size={16} className="text-primary" />
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Matchup Intel</span>
                    </div>
                    <MatchupIntelligence
                        oppRank={data.matchup?.def_rank_vs_pos || 12}
                        paceFactor="High"
                        trend="4/5 L5"
                    />
                </div>

                <div className="pt-4 flex flex-col gap-4">
                    <SportsbookDeeplinks
                        playerName={data.player?.name || data.playerName}
                        statType={data.market?.stat_type || data.statType}
                        line={data.line_value || data.line}
                        side={data.side}
                        odds={data.odds}
                    />

                    <button
                        onClick={handleDownloadGraphic}
                        disabled={exporting}
                        className="w-full h-12 flex items-center justify-center gap-2 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-all group overflow-hidden relative"
                    >
                        <div className={`absolute inset-0 bg-primary/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ${exporting ? 'translate-y-0' : ''}`}></div>
                        {exporting ? (
                            <div className="size-4 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                            <Download size={14} className="text-primary" />
                        )}
                        <span className="text-[10px] font-black uppercase tracking-widest relative z-10 text-slate-300 group-hover:text-white">
                            {exporting ? 'Generating High-Res Asset...' : 'Download Sharp Graphic (1080x1920)'}
                        </span>
                    </button>
                </div>

                <p className="text-center text-[10px] text-slate-600 font-bold uppercase tracking-widest">
                    Generated by Perplex-Edge Intelligence • Powered by PERPLEX-EDGE v2
                </p>
            </div>

            {/* Hidden Export Target (Rendered off-screen) */}
            <div className="fixed top-[-9999px] left-[-9999px] pointer-events-none opacity-0">
                <SocialShareCard
                    id={id as string}
                    data={{
                        playerName: data.player?.name || data.playerName,
                        statType: data.market?.stat_type || data.statType || 'Prop',
                        line: data.line_value || data.line,
                        side: data.side || 'over',
                        odds: data.odds || '-110',
                        edge: data.edge || 0.084,
                        sport: data.sport,
                        team: data.player?.team,
                        isVerified: true // Mocked for now
                    }}
                />
            </div>
        </div>
    );
}
