import { motion } from 'framer-motion';
import { Radio } from 'lucide-react';

export default function MarketRadar() {
    return (
        <div className="flex items-center gap-4 px-4 py-2 bg-slate-900/50 border border-slate-800 rounded-full">
            <div className="relative flex items-center justify-center">
                <motion.div
                    animate={{
                        scale: [1, 1.5, 1],
                        opacity: [0.5, 0, 0.5],
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut",
                    }}
                    className="absolute size-4 rounded-full bg-primary/40"
                />
                <Radio size={16} className="text-primary relative z-10" />
            </div>
            <div className="flex flex-col">
                <span className="text-[10px] font-black text-white uppercase tracking-widest leading-none">Market Radar</span>
                <span className="text-[9px] text-slate-500 font-bold uppercase tracking-tighter mt-0.5">Sharp Velocity: +2.4pts/hr</span>
            </div>
            <div className="flex gap-1 ml-2">
                {[1, 2, 3].map((i) => (
                    <motion.div
                        key={i}
                        animate={{
                            opacity: [0.3, 1, 0.3],
                            scale: [1, 1.2, 1],
                        }}
                        transition={{
                            duration: 0.8,
                            repeat: Infinity,
                            delay: i * 0.1,
                        }}
                        className="size-1 rounded-full bg-emerald-primary"
                    />
                ))}
            </div>
        </div>
    );
}
