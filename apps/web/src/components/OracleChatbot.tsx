"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useGate } from "@/hooks/useGate";
import { useSport } from "@/hooks/useSport";
import { clsx } from "clsx";
import { motion } from "framer-motion";

interface Message {
    role: "user" | "assistant";
    content: string;
}

const INITIAL_MESSAGE: Message = {
    role: "assistant",
    content: "Oracle online. Ask me about tonight's props, sharp money, or parlays. What are you looking at?",
};

const SUGGESTIONS = [
    "Best props tonight?",
    "Any steam moves?",
    "Build me a 3-leg parlay",
    "Who's trending over?",
    "Sharp money report",
];

export default function OracleChatbot() {
    const { tier, oracleLimit } = useGate();
    const { sport } = useSport();
    const [open, setOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([INITIAL_MESSAGE]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        if (open) setTimeout(() => inputRef.current?.focus(), 100);
    }, [open]);

    const ask = useCallback(async (text: string) => {
        if (!text.trim() || loading) return;

        const userMsg: Message = { role: "user", content: text };
        // Store current messages for the API call
        const currentMessages = [...messages, userMsg];
        
        setMessages(currentMessages);
        setInput("");
        setLoading(true);

        try {
            const response = await fetch('/api/oracle/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    messages: currentMessages, 
                    sport: sport 
                }),
            });

            if (!response.ok) throw new Error("Oracle connection failed");

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();
            
            // Start with empty assistant message
            setMessages((prev) => [...prev, { role: "assistant", content: "" }]);
            
            let fullContent = "";

            if (reader) {
              while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                // We're expecting raw text or data: chunks. 
                // For a simple proxy, it might just be the raw tokens.
                fullContent += chunk;
                
                setMessages((prev) => {
                  const items = [...prev];
                  if (items.length > 0) {
                    items[items.length - 1] = { 
                      role: "assistant", 
                      content: fullContent 
                    };
                  }
                  return items;
                });
              }
            }
        } catch (e: any) {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: e.message || "Connection lost. Try again." },
            ]);
        } finally {
            setLoading(false);
        }
    }, [messages, loading, sport]);

    const reset = () => setMessages([INITIAL_MESSAGE]);

    return (
        <>
            {/* Floating Button */}
            <button
                onClick={() => setOpen(!open)}
                className="fixed bottom-24 right-6 z-50 w-14 h-14 rounded-full bg-brand-primary hover:bg-brand-primary/80 active:scale-95 text-white shadow-glow shadow-brand-primary/20 flex items-center justify-center text-2xl transition-all duration-200"
            >
                {open ? "✕" : "🔮"}
            </button>

            {/* Chat Window */}
            {open && (
                <div className="fixed bottom-40 right-6 z-50 w-80 sm:w-96 h-[520px] bg-gray-950 border border-brand-primary/30 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
                    {/* Header */}
                    <div className="flex items-center justify-between px-4 py-3 bg-brand-primary/10 border-b border-brand-primary/20">
                        <div className="flex items-center gap-2">
                            <span className="text-lg">🔮</span>
                            <span className="font-bold text-white text-sm tracking-wide uppercase">Oracle Neural Sync</span>
                            <span className="text-[9px] text-brand-success bg-brand-success/10 px-2 py-0.5 rounded-full border border-brand-success/20 font-black animate-pulse">
                                STREAMING
                            </span>
                        </div>
                        <button onClick={reset} className="text-[10px] text-textMuted hover:text-white transition-colors font-black uppercase tracking-widest">
                            Reset
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-none">
                        {messages.map((msg, i) => (
                            <div key={i} className={clsx("flex", msg.role === "user" ? "justify-end" : "justify-start")}>
                                {msg.role === "assistant" && (
                                    <span className="text-base mr-2 mt-1 flex-shrink-0">🔮</span>
                                )}
                                <div className={clsx(
                                    "max-w-[85%] px-4 py-2.5 rounded-2xl text-xs leading-relaxed whitespace-pre-wrap font-sans",
                                    msg.role === "user"
                                        ? "bg-brand-primary text-white rounded-br-none shadow-glow shadow-brand-primary/10"
                                        : "bg-white/5 text-slate-100 rounded-bl-none border border-white/5"
                                )}>
                                    {msg.content}
                                </div>
                            </div>
                        ))}
                        {loading && messages[messages.length-1]?.role !== 'assistant' && (
                            <div className="flex justify-start items-center gap-2">
                                <span className="text-base">🔮</span>
                                <div className="bg-white/5 px-4 py-3 rounded-2xl rounded-bl-none border border-white/5">
                                    <div className="flex gap-1">
                                        <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce" />
                                        <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce [animation-delay:0.2s]" />
                                        <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-bounce [animation-delay:0.4s]" />
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>

                    {/* Suggestions */}
                    {messages.length <= 1 && (
                        <div className="px-4 pb-4 flex flex-wrap gap-2">
                            {SUGGESTIONS.map((s) => (
                                <button
                                    key={s}
                                    onClick={() => ask(s)}
                                    className="text-[10px] font-black uppercase tracking-widest bg-white/5 hover:bg-brand-primary/20 text-textMuted hover:text-white px-3 py-1.5 rounded-lg border border-white/5 transition-all duration-150"
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input */}
                    <div className="p-4 border-t border-white/10 bg-white/5">
                        {messages.length > oracleLimit * 2 && tier === "free" ? (
                            <div className="text-center p-2">
                                <p className="text-[10px] text-textMuted uppercase font-black mb-2">Daily Signal Limit Exceeded</p>
                                <a href="/upgrade" className="text-brand-primary font-black uppercase tracking-widest text-[9px] hover:underline">
                                    Upgrade Terminal Access →
                                </a>
                            </div>
                        ) : (
                            <div className="flex gap-2">
                                <input
                                    ref={inputRef}
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && ask(input)}
                                    placeholder="Execute query..."
                                    disabled={loading}
                                    className="flex-1 bg-white/5 text-white text-xs rounded-xl px-4 py-2.5 outline-none border border-white/10 focus:border-brand-primary/50 placeholder-gray-600 disabled:opacity-50 transition-all"
                                />
                                <button
                                    onClick={() => ask(input)}
                                    disabled={loading || !input.trim()}
                                    className="bg-brand-primary hover:bg-brand-primary/80 disabled:opacity-30 disabled:cursor-not-allowed text-white px-5 rounded-xl text-xs font-black uppercase tracking-widest transition-all"
                                >
                                    {loading ? "..." : "Sync"}
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}
