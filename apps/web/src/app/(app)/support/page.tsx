"use client";

import React, { useState, Suspense } from "react";
import { useMutation } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { MessageSquare, Send, CheckCircle, Info, HelpCircle, LifeBuoy } from "lucide-react";
import { clsx } from "clsx";

export default function SupportPage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">CONNECTING TO SUPPORT...</div>}>
      <SupportContent />
    </Suspense>
  );
}

function SupportContent() {
  const { token } = useAuth();
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const mutation = useMutation({
    mutationFn: (ticket: any) => fetch(`${API_BASE}/api/support`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify(ticket)
    }).then(r => r.json()),
    onSuccess: () => {
      setSubmitted(true);
      setSubject("");
      setMessage("");
    }
  });

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto pt-24 text-center space-y-8 animate-in fade-in zoom-in duration-500 px-4">
        <div className="bg-brand-success/10 w-24 h-24 rounded-full flex items-center justify-center mx-auto border border-brand-success/20">
          <CheckCircle size={48} className="text-brand-success" />
        </div>
        <div>
          <h1 className="text-4xl font-black italic uppercase text-white font-display mb-4">Intel Received</h1>
          <p className="text-textSecondary font-bold italic">Our analysts are reviewing your ticket. Average response: 4.2h</p>
        </div>
        <button 
          onClick={() => setSubmitted(false)}
          className="bg-white text-black px-12 py-4 rounded-2xl text-xs font-black uppercase tracking-widest hover:bg-brand-success hover:text-white transition-all shadow-glow shadow-brand-success/20"
        >
          Open New Ticket
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto pb-24 space-y-12 pt-12 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-success/10 p-2 rounded-lg border border-brand-success/20">
              <LifeBuoy size={24} className="text-brand-success animate-spin-slow" />
            </div>
            <h1 className="text-4xl font-black italic tracking-tighter uppercase text-white font-display">Mission Support</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest italic">Encrypted communication channel for technical & billing inquiries</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
           <div className="bg-lucrix-surface border border-lucrix-border rounded-3xl p-8 shadow-card flex flex-col gap-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black text-textMuted uppercase tracking-widest ml-1">Context / Subject</label>
                <input 
                  type="text" 
                  placeholder="e.g. API latency on props feed..." 
                  className="w-full bg-lucrix-dark border border-lucrix-border rounded-xl py-4 px-6 text-sm font-bold text-white focus:border-brand-success/50 outline-none transition-all"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-black text-textMuted uppercase tracking-widest ml-1">Intelligence / Message</label>
                <textarea 
                  placeholder="Describe the issue in detail..." 
                  rows={8}
                  className="w-full bg-lucrix-dark border border-lucrix-border rounded-xl py-4 px-6 text-sm font-bold text-white focus:border-brand-success/50 outline-none transition-all resize-none"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                />
              </div>

              <button 
                onClick={() => mutation.mutate({ subject, message })}
                disabled={mutation.isPending || !subject || !message}
                className="w-full bg-brand-success text-white py-4 rounded-xl text-[10px] font-black uppercase tracking-widest hover:shadow-glow hover:shadow-brand-success/30 transition-all flex items-center justify-center gap-3 disabled:opacity-50 disabled:hover:shadow-none"
              >
                {mutation.isPending ? "Transmitting..." : <><Send size={14} /> Transmit Intelligence</>}
              </button>
           </div>
        </div>

        <div className="space-y-6">
           <SupportInfoCard 
             icon={<HelpCircle size={18} />} 
             title="Direct Intel" 
             value="support@perplex.edge" 
             description="24/7 institutional grade support for API clients."
           />
           <SupportInfoCard 
             icon={<MessageSquare size={18} />} 
             title="Community Alpha" 
             value="Join Discord" 
             description="Discuss strategies with 5k+ sharp bettors."
             color="text-brand-purple"
           />
           <div className="bg-lucrix-surface/50 border border-lucrix-border/50 rounded-2xl p-6">
              <div className="flex items-start gap-3">
                 <div className="p-1.5 bg-brand-success/10 rounded-lg text-brand-success mt-0.5">
                    <Info size={14} />
                 </div>
                 <p className="text-[10px] font-bold text-textSecondary italic leading-relaxed uppercase tracking-tighter">
                   "All support tickets are encrypted. Our typical response time for Elite members is under 30 minutes."
                 </p>
              </div>
           </div>
        </div>
      </div>
    </div>
  );
}

function SupportInfoCard({ icon, title, value, description, color = "text-brand-success" }: any) {
  return (
    <div className="bg-lucrix-surface border border-lucrix-border rounded-2xl p-6 shadow-card hover:border-brand-success/20 transition-all group">
      <div className="flex items-center gap-3 text-[9px] font-black text-textMuted uppercase tracking-widest mb-4">
        <div className={clsx("p-2 bg-lucrix-dark rounded-xl border border-lucrix-border transition-colors", color)}>
          {icon}
        </div>
        {title}
      </div>
      <div className="text-lg font-black text-white italic truncate font-display mb-1">{value}</div>
      <div className="text-[10px] font-bold text-textMuted italic leading-snug">{description}</div>
    </div>
  );
}
