"use client";

import React from "react";
import { motion } from "framer-motion";
import { TrendingUp, Clock, ExternalLink, ShieldCheck, Zap } from "lucide-react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";
import { clsx } from "clsx";
import CountUp from "react-countup";
import { formatDistanceToNow } from "date-fns";

export type EVSignal = {
  event_id: string;
  sport_key: string;
  player_name: string;
  market_key: string;
  line: number;
  bookmaker: string;
  current_price: number;
  ev_pct: number;
  edge_percent?: number;
  true_prob?: number;
  implied_prob?: number;
  confidence_score?: number;
  updated_at: string;
  outcome_key?: string;
};

interface EVCardProps {
  signal: EVSignal;
  index: number;
}

export const EVCard: React.FC<EVCardProps> = ({ signal, index }) => {
  const edgeVal = signal.ev_pct || signal.edge_percent || 0;
  const isHighEdge = edgeVal >= 5;
  const edgeColor = isHighEdge ? "#10b981" : "#3b82f6"; // Green-500 or Blue-500
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
      className="relative group h-full"
    >
      {/* Glow Effect */}
      <div className={clsx(
        "absolute -inset-0.5 rounded-2xl blur opacity-0 group-hover:opacity-30 transition duration-500",
        isHighEdge ? "bg-brand-success" : "bg-brand-primary"
      )} />
      
      <div className="relative bg-lucrix-surface/40 backdrop-blur-xl border border-white/5 rounded-2xl p-5 h-full flex flex-col justify-between overflow-hidden">
        {/* Background Accent */}
        <div className={clsx(
            "absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 rounded-full blur-3xl opacity-10",
            isHighEdge ? "bg-brand-success" : "bg-brand-primary"
        )} />

        <div className="relative flex justify-between items-start mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2 py-0.5 rounded-md bg-white/5 border border-white/10 text-[9px] font-black uppercase tracking-widest text-textMuted">
                {signal.sport_key.replace("basketball_", "").toUpperCase()}
              </span>
              <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-brand-success/10 border border-brand-success/20 text-[9px] font-black uppercase tracking-widest text-brand-success">
                <Zap size={8} /> LIVE
              </span>
            </div>
            <h3 className="text-lg font-black italic uppercase tracking-tight text-white line-clamp-1 group-hover:text-brand-success transition-colors">
              {signal.player_name || "Game Market"}
            </h3>
            <p className="text-xs font-bold text-textMuted uppercase tracking-wide">
              {signal.market_key.replace(/_/g, " ")} {signal.line && `@ ${signal.line}`}
            </p>
          </div>
          
          <div className="w-14 h-14 shrink-0">
            <CircularProgressbar
              value={edgeVal}
              maxValue={15}
              text={`${edgeVal.toFixed(1)}%`}
              styles={buildStyles({
                textSize: "24px",
                pathColor: edgeColor,
                textColor: "#ffffff",
                trailColor: "rgba(255,255,255,0.05)",
                pathTransitionDuration: 1.5,
              })}
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="bg-white/5 rounded-xl p-3 border border-white/5">
            <p className="text-[9px] font-black uppercase tracking-widest text-textMuted mb-1">Best Book</p>
            <div className="flex items-center gap-2">
              <span className="text-sm font-black text-white italic uppercase">{signal.bookmaker}</span>
              <span className="ml-auto text-lg font-black text-brand-success">
                {signal.current_price > 0 ? `+${Math.round((signal.current_price - 1) * 100)}` : signal.current_price}
              </span>
            </div>
          </div>
          
          <div className="bg-white/5 rounded-xl p-3 border border-white/5">
            <p className="text-[9px] font-black uppercase tracking-widest text-textMuted mb-1">Fair Odds</p>
            <div className="flex items-center gap-2">
              <ShieldCheck size={12} className="text-brand-primary" />
              <span className="text-sm font-black text-white/50 italic">
                {signal.true_prob && signal.true_prob > 0 ? `+${Math.round((1/signal.true_prob - 1) * 100)}` : "---"}
              </span>
            </div>
          </div>
        </div>

        <div className="relative pt-4 border-t border-white/5 mt-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-[9px] font-bold text-textMuted uppercase tracking-widest">
              <Clock size={10} />
              {formatDistanceToNow(new Date(signal.updated_at), { addSuffix: true })}
            </div>
            
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-primary hover:bg-brand-primary-hover text-white text-[10px] font-black uppercase tracking-widest transition-all shadow-lg shadow-brand-primary/20 hover:shadow-brand-primary/40 active:scale-95">
              Place Bet <ExternalLink size={10} />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};
