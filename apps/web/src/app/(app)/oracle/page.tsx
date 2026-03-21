"use client";

import React, { useState, useRef, useEffect, Suspense } from "react";
import { useSport } from "@/hooks/useSport";
import { useAuth } from "@/hooks/useAuth";
import { useTierGate } from "@/hooks/useTierGate";
import { API_BASE } from "@/lib/api";
import { Skeleton } from "@/components/ui/Skeleton";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import SportSelector from "@/components/shared/SportSelector";
import { Brain, Send, User, Bot, Sparkles, Star, AlertCircle } from "lucide-react";
import { clsx } from "clsx";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function OraclePage() {
  return (
    <Suspense fallback={<div className="p-6 text-white font-black italic uppercase tracking-widest animate-pulse font-display text-center py-24">BOOTING ORACLE CORE...</div>}>
      <OracleContent />
    </Suspense>
  );
}

function OracleContent() {
  const { sport } = useSport();
  const { user, tier } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { isLocked, isLoading: isGateLoading } = useTierGate(
    { data: true, isLoading: false, error: null },
    { requiredTier: "pro" }
  );

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming || isLocked) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsStreaming(true);

    try {
      const response = await fetch(`${API_BASE}/api/oracle`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${user?.id}` // Placeholder for real token logic
        },
        body: JSON.stringify({ sport, question: input }),
      });

      if (!response.ok) throw new Error("Oracle connection lost.");

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let assistantMsg: Message = { role: "assistant", content: "" };
      setMessages(prev => [...prev, assistantMsg]);

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;
        const chunk = decoder.decode(value);
        assistantMsg.content += chunk;
        setMessages(prev => [...prev.slice(0, -1), { ...assistantMsg }]);
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: "assistant", content: "⚠️ System malfunction. The oracle is temporarily unavailable." }]);
    } finally {
      setIsStreaming(false);
    }
  };

  if (isGateLoading) {
    return <div className="p-24 text-center"><Skeleton className="h-64 w-full max-w-2xl mx-auto rounded-3xl" /></div>;
  }

  return (
    <div className="pb-24 flex flex-col h-[calc(100vh-140px)] pt-6 px-4">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-brand-cyan/10 p-2 rounded-lg border border-brand-cyan/20">
              <Brain size={24} className="text-brand-cyan shadow-glow shadow-brand-cyan/40" />
            </div>
            <h1 className="text-3xl font-black italic tracking-tighter uppercase text-white font-display">Oracle AI</h1>
          </div>
          <p className="text-[10px] text-textMuted font-black uppercase tracking-widest italic mb-4">Generative Sports Intelligence</p>
          <SportSelector />
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col bg-lucrix-surface border border-lucrix-border rounded-3xl shadow-2xl relative">
        {isLocked && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/40 backdrop-blur-sm rounded-3xl">
            <div className="bg-lucrix-surface border border-brand-cyan/30 p-10 rounded-3xl text-center max-w-sm shadow-2xl">
              <Star size={40} className="mx-auto text-brand-cyan mb-6 animate-pulse" />
              <h2 className="text-2xl font-black italic uppercase tracking-tighter mb-4 text-white font-display">Pro Intelligence Only</h2>
              <p className="text-textSecondary text-sm font-bold mb-8 italic">
                The Oracle requires advanced computational cycles reserved for Pro+ athletes.
              </p>
              <button 
                onClick={() => window.location.href = "/subscription"}
                className="bg-brand-cyan hover:bg-brand-cyan/90 text-black px-10 py-4 rounded-xl font-black uppercase tracking-widest text-sm transition-all"
              >
                Access Oracle →
              </button>
            </div>
          </div>
        )}

        {/* Chat Feed */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-50">
              <Sparkles size={48} className="text-brand-cyan" />
              <div className="space-y-1">
                <p className="text-white font-black uppercase tracking-widest text-sm">Awaiting Query</p>
                <p className="text-textMuted text-xs italic">Ask about lines, trends, or institutional flow...<br/>"Which NBA player has the highest CLV edge today?"</p>
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={clsx("flex gap-4", msg.role === "user" ? "flex-row-reverse" : "flex-row")}>
              <div className={clsx(
                "p-3 rounded-xl border flex-shrink-0",
                msg.role === "user" ? "bg-lucrix-dark border-lucrix-border" : "bg-brand-cyan/10 border-brand-cyan/20"
              )}>
                {msg.role === "user" ? <User size={18} className="text-white" /> : <Bot size={18} className="text-brand-cyan" />}
              </div>
              <div className={clsx(
                "p-4 rounded-2xl max-w-[80%] text-sm font-bold leading-relaxed",
                msg.role === "user" ? "bg-lucrix-dark text-white border border-lucrix-border" : "bg-brand-cyan/5 text-textSecondary border border-brand-cyan/10"
              )}>
                {msg.content}
              </div>
            </div>
          ))}
          {isStreaming && (
            <div className="flex gap-4 animate-pulse">
              <div className="p-3 rounded-xl border bg-brand-cyan/10 border-brand-cyan/20 flex-shrink-0">
                <Bot size={18} className="text-brand-cyan" />
              </div>
              <div className="bg-brand-cyan/5 border border-brand-cyan/10 p-4 rounded-2xl w-24 h-10" />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-6 border-t border-lucrix-border bg-lucrix-dark/30">
          <form onSubmit={handleSubmit} className="relative">
            <input 
              type="text" 
              placeholder={isLocked ? "Oracle Locked" : "Type your question to the oracle..."}
              className="w-full bg-lucrix-surface border border-lucrix-border rounded-2xl py-4 pl-6 pr-16 text-sm font-bold text-white outline-none focus:border-brand-cyan/50 transition-all disabled:opacity-50"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLocked || isStreaming}
            />
            <button 
              type="submit"
              disabled={isLocked || isStreaming || !input.trim()}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-brand-cyan hover:bg-brand-cyan/90 text-black rounded-xl transition-all disabled:opacity-30 disabled:hover:bg-brand-cyan"
            >
              <Send size={20} />
            </button>
          </form>
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center gap-2 opacity-60">
              <AlertCircle size={10} className="text-brand-cyan" />
              <span className="text-[9px] font-black uppercase text-textMuted tracking-widest">Rate Limited: 50 requests / day (Pro)</span>
            </div>
            <div className="flex gap-2">
              <span className="text-[8px] bg-lucrix-dark px-1.5 py-0.5 rounded text-white font-black italic border border-white/5 uppercase">H-100 Clusters Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
