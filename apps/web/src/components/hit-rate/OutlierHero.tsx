"use client";
import { Zap, Target, Search, Clock } from "lucide-react";
import { motion } from "framer-motion";

interface OutlierHeroProps {
    count: number;
    lastSync: string;
}

export function OutlierHero({ count, lastSync }: OutlierHeroProps) {
    return (
        <div className="relative overflow-hidden rounded-3xl bg-lucrix-dark border border-white/5 p-8 mb-10">
            {/* Background Glow */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-brand-cyan/10 blur-[120px] rounded-full -mr-48 -mt-48 animate-pulse-slow" />
            <div className="absolute bottom-0 left-0 w-[300px] h-[300px] bg-brand-purple/10 blur-[100px] rounded-full -ml-32 -mb-32" />

            <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-8">
                <div className="space-y-4 max-w-2xl text-center md:text-left">
                    <motion.div 
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2 px-3 py-1 bg-brand-cyan/10 border border-brand-cyan/20 rounded-full text-brand-cyan text-[10px] font-black uppercase tracking-widest"
                    >
                        <Zap size={12} className="fill-brand-cyan" />
                        Live Outlier Alerts
                    </motion.div>
                    
                    <h1 className="text-5xl md:text-6xl font-black italic uppercase font-display leading-[0.9] text-white">
                        <span className="text-brand-cyan decoration-brand-cyan/30 underline-offset-8 underline decoration-4">
                            {count} Outliers
                        </span><br/> Detected Today
                    </h1>
                    
                    <p className="text-textSecondary text-lg font-medium max-w-lg">
                        Surface players hitting their prop lines at 70% or better. 
                        Instant edge detection across all major sports.
                    </p>
                </div>

                <div className="grid grid-cols-2 gap-4 w-full md:w-auto">
                    {[
                        { label: "Markets", val: "12+", icon: <Target className="text-brand-purple" /> },
                        { label: "Last Sync", val: "Live", icon: <Clock className="text-brand-success" /> },
                    ].map((stat, i) => (
                        <div key={i} className="bg-white/5 border border-white/10 p-4 rounded-2xl flex flex-col items-center gap-2 min-w-[140px]">
                            <div className="p-2 bg-white/5 rounded-lg">{stat.icon}</div>
                            <div className="text-2xl font-black text-white italic font-display leading-none">{stat.val}</div>
                            <div className="text-[10px] text-textMuted uppercase font-black tracking-widest">{stat.label}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
