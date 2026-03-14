"use client";

import { motion } from 'framer-motion';

interface SparklineProps {
    velocity: number; // -1 to 1
}

export default function Sparkline({ velocity }: SparklineProps) {
    const isUp = velocity > 0;
    const color = isUp ? '#0df233' : '#ef4444'; // Primary green vs Red

    // Generate a simple zigzag path based on velocity
    const points = [
        "0,10",
        "5,8",
        "10,12",
        "15,7",
        "20,9",
        "25,5",
        "30,8",
        isUp ? "35,2" : "35,14"
    ];

    return (
        <div className="flex items-center gap-2">
            <svg width="40" height="16" viewBox="0 0 40 16" className="overflow-visible">
                <motion.polyline
                    fill="none"
                    stroke={color}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    points={points.join(" ")}
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 1, ease: "easeOut" }}
                />
            </svg>
            <div className={`flex flex-col ${isUp ? 'text-emerald-primary' : 'text-red-500'}`}>
                <span className="text-[8px] font-black uppercase tracking-tighter leading-none">
                    {isUp ? 'Sharp Buy' : 'Public Sell'}
                </span>
                <span className="text-[10px] font-bold font-mono tracking-tighter">
                    {velocity > 0 ? '+' : ''}{velocity.toFixed(2)}
                </span>
            </div>
        </div>
    );
}
