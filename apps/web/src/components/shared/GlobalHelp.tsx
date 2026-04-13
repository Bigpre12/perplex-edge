"use client";

import React, { useState } from "react";
import { HelpCircle, X, ExternalLink, BookOpen, Target, ShieldCheck, Zap } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const GUIDES: Record<string, any> = {
  "/brain": {
    title: "Neural Engine Guide",
    steps: [
      "View real-time correlated markets across all tracked sports.",
      "Monitor the 'Confidence' score for high-fidelity signals.",
      "Click any player to drill down into their historical performance matrix."
    ]
  },
  "/ev": {
    title: "EV+ Tracker Guide",
    steps: [
      "Markets are ranked by Expected Value percentage vs. Global Sharp lines.",
      "The 'Reasoning' column provides AI-augmented logic for the specific edge.",
      "Target edges > 4% for optimal long-term alpha."
    ]
  },
  "/parlays": {
    title: "Parlay Matrix Guide",
    steps: [
      "Use 'Build Me a Parlay' for a neural-selected high-correlation slip.",
      "Execute the 'Monte Carlo Simulation' to calculate true win probability.",
      "Institutional Grades (S/A/B/C) reflect risk-adjusted return potential."
    ]
  },
  "/ledger": {
    title: "Intelligence Ledger Guide",
    steps: [
      "Track your results manually or via automatic sync (selected books).",
      "Monitor your ROI and Win Rate across specific market sectors.",
      "Use 'Share' to publish your winning insights to the community feed."
    ]
  },
  "default": {
    title: "Perplex Edge Quick Start",
    steps: [
      "Navigate using the tactical sidebar to access specific intelligence modules.",
      "Use the Sport Selector to filter feeds by your preferred league.",
      "Access the Oracle Chat for ad-hoc deep dives and market analysis."
    ]
  }
};

export default function GlobalHelp() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  
  const guide = GUIDES[pathname] || GUIDES.default;

  return (
    <>
      {/* Floating Help Button */}
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-24 right-8 z-40 p-4 bg-brand-primary text-white rounded-full shadow-glow shadow-brand-primary/40 hover:scale-110 active:scale-95 transition-all"
        title="Help Guide"
      >
        <HelpCircle size={24} />
      </button>

      {/* Help Modal */}
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-6">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="absolute inset-0 bg-lucrix-dark/90 backdrop-blur-md"
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative w-full max-w-lg bg-lucrix-surface border border-white/10 rounded-[2.5rem] p-10 shadow-2xl overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 bg-brand-primary/10 rounded-full blur-3xl" />
              
              <button 
                onClick={() => setIsOpen(false)}
                className="absolute top-8 right-8 text-textMuted hover:text-white transition-colors"
                title="Close"
              >
                <X size={20} />
              </button>

              <div className="flex items-center gap-4 mb-8">
                 <div className="p-3 bg-brand-primary/10 border border-brand-primary/20 rounded-2xl text-brand-primary">
                    <BookOpen size={24} />
                 </div>
                 <div>
                    <h2 className="text-2xl font-black italic uppercase tracking-tighter text-white leading-none">{guide.title}</h2>
                    <p className="text-[9px] text-textMuted font-black uppercase tracking-widest mt-2">Tactical Operations Guide</p>
                 </div>
              </div>

              <div className="space-y-6 mb-10">
                 {guide.steps.map((step: string, i: number) => (
                   <div key={i} className="flex gap-4 group">
                      <div className="flex-none w-6 h-6 rounded-lg bg-white/5 border border-white/5 flex items-center justify-center text-[10px] font-black group-hover:bg-brand-primary group-hover:border-brand-primary transition-all">
                        {i + 1}
                      </div>
                      <p className="text-xs font-bold text-textSecondary leading-relaxed italic">{step}</p>
                   </div>
                 ))}
              </div>

              <div className="pt-8 border-t border-white/5 flex items-center justify-between">
                 <div className="flex items-center gap-4 text-textMuted">
                    <ShieldCheck size={18} className="text-emerald-400" />
                    <span className="text-[9px] font-black uppercase tracking-[0.2em]">Verified Logistics</span>
                 </div>
                 <a 
                   href="/support"
                   className="flex items-center gap-2 text-brand-primary hover:text-white transition-colors text-[10px] font-black uppercase tracking-widest"
                 >
                   Full Documentation <ExternalLink size={12} />
                 </a>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
