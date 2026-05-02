"use client";

import { useRef, useState } from "react";
import html2canvas from "html2canvas";
import { Download, Share2, Loader2, Check } from "lucide-react";

export default function BetSlipShare({ pick }: any) {
    const slipRef = useRef<HTMLDivElement>(null);
    const [generating, setGenerating] = useState(false);
    const [completed, setCompleted] = useState(false);

    const captureSlip = async () => {
        if (!slipRef.current) return;
        setGenerating(true);
        try {
            const canvas = await html2canvas(slipRef.current, {
                backgroundColor: "#000000",
                scale: 2, // High resolution for social media
                logging: false,
                useCORS: true
            });
            const image = canvas.toDataURL("image/png");

            // Create download link
            const link = document.createElement("a");
            link.href = image;
            link.download = `Lucrix_Verified_${pick.player_name || 'Shot'}.png`;
            link.click();

            setCompleted(true);
            setTimeout(() => setCompleted(false), 3000);
        } catch (err) {
            console.error("Failed to capture slip:", err);
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div className="relative inline-block">
            <button
                onClick={captureSlip}
                className="p-2.5 bg-white/5 hover:bg-emerald-500/20 border border-white/10 hover:border-emerald-500/30 rounded-xl text-slate-400 hover:text-emerald-400 transition-all flex items-center gap-2 group shadow-xl"
                title="Download Premium Social Slip"
            >
                {generating ? <Loader2 size={16} className="animate-spin text-emerald-500" /> : completed ? <Check size={16} className="text-emerald-500 animate-bounce" /> : <Share2 size={16} />}
                <span className="text-[10px] font-black uppercase tracking-widest hidden group-hover:block transition-all">Export Slip</span>
            </button>

            {/* Hidden Export Template - 1080x1920 Mobile-Optimized Layout */}
            <div className="fixed left-[-9999px] top-0 pointer-events-none select-none">
                <div
                    ref={slipRef}
                    className="w-[1080px] h-[1920px] bg-[#050505] p-24 flex flex-col justify-between relative overflow-hidden"
                >
                    {/* Atmospheric Lighting */}
                    <div className="absolute top-0 right-0 w-[1200px] h-[1200px] bg-emerald-500/[0.08] blur-[180px] rounded-full -translate-y-1/2 translate-x-1/2" />
                    <div className="absolute bottom-0 left-0 w-[800px] h-[800px] bg-emerald-500/[0.03] blur-[150px] rounded-full translate-y-1/2 -translate-x-1/2" />

                    {/* Header: Brand Identity */}
                    <div className="relative z-10 flex items-center justify-between border-b-4 border-white/10 pb-20">
                        <div>
                            <div className="flex items-center gap-4 mb-6">
                                <span className="px-5 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-3xl font-black uppercase tracking-[0.4em]">Verified</span>
                            </div>
                            <h1 className="text-white text-[120px] font-black tracking-[-0.05em] leading-[0.8] mb-2">PERPLEX-EDGE</h1>
                            <h1 className="text-emerald-500 text-[120px] font-black tracking-[-0.05em] leading-[0.8]">EDGE</h1>
                        </div>
                        <div className="size-48 bg-emerald-500 rounded-[3rem] flex items-center justify-center shadow-[0_0_80px_rgba(16,185,129,0.4)] rotate-3">
                            <span className="text-black text-9xl font-black italic">E</span>
                        </div>
                    </div>

                    {/* Body: Pick Intelligence */}
                    <div className="relative z-10 flex-1 flex flex-col justify-center py-20">
                        <div className="bg-gradient-to-br from-white/[0.03] to-transparent p-24 rounded-[5rem] border-2 border-white/10 shadow-2xl relative">
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 px-10 py-4 bg-emerald-500 rounded-full text-black text-3xl font-black uppercase tracking-widest shadow-[0_0_30px_rgba(16,185,129,0.5)]">
                                Institutional Intel
                            </div>

                            <h2 className="text-white text-[140px] font-black leading-[1.1] mb-8 tracking-tighter text-center italic">
                                {pick.player?.name || pick.player_name}
                            </h2>
                            <p className="text-slate-400 text-5xl font-black uppercase tracking-[0.3em] text-center mb-24 pb-12 border-b-2 border-white/5">
                                {pick.market?.stat_type || pick.stat_type} • {pick.sportsbook || 'Sharp Model'}
                            </p>

                            <div className="grid grid-cols-2 gap-20">
                                <div className="text-center space-y-4">
                                    <p className="text-slate-500 text-3xl font-black uppercase tracking-widest bg-white/5 py-4 rounded-3xl">Target Line</p>
                                    <p className="text-white text-[100px] font-black tracking-tighter">{pick.side?.toUpperCase()} {pick.line_value || pick.line}</p>
                                </div>
                                <div className="text-center space-y-4">
                                    <p className="text-slate-500 text-3xl font-black uppercase tracking-widest bg-white/5 py-4 rounded-3xl">AI Edge</p>
                                    <p className="text-emerald-500 text-[100px] font-black tracking-tighter">+{((pick.edge || 0.052) * 100).toFixed(1)}%</p>
                                </div>
                            </div>
                        </div>

                        {/* Model Confidence Tags */}
                        <div className="grid grid-cols-3 gap-10 mt-20">
                            {[
                                { l: "Model", v: "PHASE 11" },
                                { l: "Certainty", v: "HIGH" },
                                { l: "Liquidity", v: "VERIFIED" }
                            ].map((tag, idx) => (
                                <div key={idx} className="p-10 rounded-[2.5rem] bg-white/[0.01] border-2 border-white/5 text-center">
                                    <p className="text-slate-600 text-2xl font-black uppercase tracking-widest mb-4">{tag.l}</p>
                                    <p className="text-white text-4xl font-black tracking-tight">{tag.v}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Footer: Scarcity & Social Link */}
                    <div className="relative z-10 flex items-center justify-between border-t-4 border-white/10 pt-20">
                        <div className="space-y-4">
                            <p className="text-slate-500 text-4xl font-bold">Access the Engine:</p>
                            <p className="text-white text-5xl font-black tracking-tight">perplex-edge.ai</p>
                        </div>
                        <div className="flex flex-col items-end gap-3 text-emerald-500">
                            <div className="flex items-center gap-4">
                                <Check size={50} className="stroke-[4]" />
                                <span className="text-5xl font-black uppercase tracking-widest italic">Sharp Signal</span>
                            </div>
                            <p className="text-2xl font-medium text-slate-500 uppercase tracking-widest">TS: {new Date().toLocaleDateString()}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
