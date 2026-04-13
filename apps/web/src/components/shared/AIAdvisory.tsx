"use client";

import React from "react";
import { Brain, Info, ShieldCheck, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { clsx } from "clsx";

interface AIAdvisoryProps {
  title?: string;
  content: string;
  type?: "info" | "warning" | "success";
  className?: string;
}

export default function AIAdvisory({ 
  title = "Neural Advisory", 
  content, 
  type = "info",
  className 
}: AIAdvisoryProps) {
  
  const typeStyles = {
    info: "border-brand-primary/20 bg-brand-primary/5 text-brand-primary",
    warning: "border-yellow-500/20 bg-yellow-500/5 text-yellow-400",
    success: "border-emerald-500/20 bg-emerald-500/5 text-emerald-400"
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        "p-6 rounded-[1.5rem] border backdrop-blur-md shadow-lg relative overflow-hidden",
        typeStyles[type],
        className
      )}
    >
      <div className="absolute top-0 right-0 w-24 h-24 -mr-12 -mt-12 opacity-10 bg-current rounded-full blur-2xl" />
      
      <div className="flex items-start gap-4 relative z-10">
        <div className="p-2 rounded-xl bg-current bg-opacity-10 border border-current border-opacity-20 shrink-0">
          <Brain size={18} />
        </div>
        <div className="space-y-1">
          <h4 className="text-[10px] font-black uppercase tracking-[0.2em] italic opacity-80">{title}</h4>
          <p className="text-[11px] font-bold text-white/70 leading-relaxed italic border-l border-current border-opacity-20 pl-3">
            {content}
          </p>
        </div>
      </div>
    </motion.div>
  );
}
