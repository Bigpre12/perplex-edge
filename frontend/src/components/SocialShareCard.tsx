"use client";
import React from 'react';
import { Share2, Zap, Brain, ShieldCheck } from 'lucide-react';

interface SocialShareCardProps {
    data: {
        playerName: string;
        statType: string;
        line: number;
        side: string;
        odds: string;
        edge: number;
        sport?: string;
        team?: string;
        avatarUrl?: string;
        isVerified?: boolean;
    };
    id: string;
}

export const SocialShareCard: React.FC<SocialShareCardProps> = ({ data, id }) => {
    return (
        <div
            id="social-share-card"
            className="w-[1080px] h-[1920px] bg-[#050a08] flex flex-col items-center justify-between p-20 relative overflow-hidden"
            style={{
                backgroundImage: 'radial-gradient(circle at 50% 0%, rgba(13, 242, 51, 0.15) 0%, transparent 70%), radial-gradient(circle at 0% 100%, rgba(13, 242, 51, 0.05) 0%, transparent 50%)'
            }}
        >
            {/* Background Decorative Elements */}
            <div className="absolute top-[-10%] left-[-10%] w-[120%] h-[120%] opacity-20 pointer-events-none">
                <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-primary/20 rounded-full blur-[150px]"></div>
                <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-primary/10 rounded-full blur-[120px]"></div>
            </div>

            {/* Header / Branding */}
            <div className="w-full flex justify-between items-start z-10">
                <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-4">
                        <div className="size-16 bg-primary rounded-xl flex items-center justify-center shadow-[0_0_30px_rgba(13,242,51,0.4)]">
                            <Zap size={40} className="text-background-dark fill-background-dark" />
                        </div>
                        <h2 className="text-5xl font-black text-white tracking-tighter uppercase italic">Perplex <span className="text-primary">Edge</span></h2>
                    </div>
                    <p className="text-2xl font-bold text-slate-500 uppercase tracking-[0.3em] ml-20">Intelligence Hub</p>
                </div>
                {data.isVerified && (
                    <div className="flex items-center gap-3 bg-primary/10 border border-primary/30 px-6 py-3 rounded-full">
                        <ShieldCheck size={32} className="text-primary" />
                        <span className="text-2xl font-black text-primary uppercase tracking-widest">Verified Sharp</span>
                    </div>
                )}
            </div>

            {/* Main Content Area */}
            <div className="w-full space-y-16 z-10 flex-1 flex flex-col justify-center">
                {/* Player Profile */}
                <div className="flex flex-col items-center gap-8 text-center">
                    <div className="relative">
                        <div className="absolute inset-0 bg-primary/20 rounded-full blur-3xl"></div>
                        <img
                            src={data.avatarUrl || `https://ui-avatars.com/api/?name=${encodeURIComponent(data.playerName)}&background=101f19&color=0df233&size=256`}
                            className="size-64 rounded-full border-4 border-primary/50 shadow-[0_0_60px_rgba(13,242,51,0.2)] relative z-10 object-cover"
                            alt={data.playerName}
                        />
                    </div>
                    <div className="space-y-4">
                        <div className="flex items-center justify-center gap-4">
                            <span className="px-5 py-2 rounded-lg bg-primary/20 text-primary text-xl font-black uppercase tracking-[0.2em]">{data.sport || 'NBA'}</span>
                            <span className="text-3xl font-bold text-slate-400 uppercase tracking-widest">{data.team || 'PRO'}</span>
                        </div>
                        <h1 className="text-[120px] font-black text-white tracking-tighter leading-none">{data.playerName}</h1>
                    </div>
                </div>

                {/* The Prop & Edge */}
                <div className="grid grid-cols-1 gap-12">
                    <div className="p-16 rounded-[40px] bg-white/[0.03] border border-white/10 backdrop-blur-xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-12 opacity-5">
                            <Brain size={160} />
                        </div>

                        <div className="flex flex-col gap-12 items-center text-center">
                            <div className="space-y-4">
                                <p className="text-3xl text-slate-500 font-black uppercase tracking-[0.4em]">Market Intelligence</p>
                                <div className="text-[90px] font-black text-white leading-tight">
                                    {data.statType}
                                </div>
                                <div className="text-6xl font-black text-primary flex items-center justify-center gap-6">
                                    <span className="uppercase">{data.side}</span>
                                    <span>{data.line}</span>
                                </div>
                            </div>

                            <div className="w-full h-px bg-white/10"></div>

                            <div className="flex justify-around w-full items-center">
                                <div className="text-center">
                                    <p className="text-2xl text-slate-500 font-black uppercase tracking-widest mb-4">LOLA Edge</p>
                                    <p className="text-[100px] font-black text-primary leading-none shadow-primary/20 drop-shadow-[0_0_20px_rgba(13,242,51,0.3)]">
                                        +{(data.edge * 100).toFixed(1)}%
                                    </p>
                                </div>
                                <div className="text-center">
                                    <p className="text-2xl text-slate-500 font-black uppercase tracking-widest mb-4">Market Odds</p>
                                    <p className="text-8xl font-black text-white leading-none">
                                        {data.odds}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer / QR / Call to Action */}
            <div className="w-full flex items-end justify-between z-10 pt-10 border-t border-white/5">
                <div className="space-y-4">
                    <p className="text-3xl font-black text-white uppercase tracking-tighter italic">Join the <span className="text-primary italic">Sharpest</span> Edge</p>
                    <p className="text-xl font-bold text-slate-500 max-w-lg">Advanced algorithmic modeling and real-time steam tracking for elite bettors.</p>
                </div>

                <div className="flex flex-col items-end gap-6 text-right">
                    <div className="size-48 bg-white p-4 rounded-3xl flex items-center justify-center shadow-[0_0_40px_rgba(255,255,255,0.1)]">
                        <img
                            src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(`https://perplex-edge.com/share/${id}`)}&color=050a08&bgcolor=ffffff`}
                            className="size-full"
                            alt="Verification QR"
                            crossOrigin="anonymous"
                        />
                    </div>
                    <p className="text-xl font-black text-slate-400 uppercase tracking-[0.2em]">Scan to Verify</p>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="absolute bottom-0 left-0 w-full h-4 bg-primary shadow-[0_-10px_30px_rgba(13,242,51,0.3)]"></div>
        </div>
    );
};
