"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Brain,
    X,
    Send,
    Loader2,
    Terminal,
    Sparkles,
    MessageSquare,
    TrendingUp,
    Target
} from "lucide-react";
import { getAuthToken } from "@/lib/auth";

export default function AIHandler() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        if (isOpen) scrollToBottom();
    }, [messages, isOpen]);

    const handleSend = async () => {
        if (!query.trim()) return;

        const userMsg = { role: "user", content: query };
        setMessages(prev => [...prev, userMsg]);
        setQuery("");
        setIsLoading(true);

        try {
            const token = getAuthToken();
            const res = await fetch("http://localhost:8000/ai/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(token && { "Authorization": `Bearer ${token}` })
                },
                body: JSON.stringify({ message: query })
            });

            if (res.ok) {
                const data = await res.json();
                setMessages(prev => [...prev, { role: "assistant", content: data.response }]);
            } else {
                setMessages(prev => [...prev, { role: "assistant", content: "I encountered a synchronization error with the Perplex brain. Please try again." }]);
            }
        } catch (err) {
            setMessages(prev => [...prev, { role: "assistant", content: "Connection failure to intelligence nodes." }]);
        } finally {
            setIsLoading(false);
        }
    };

    const QuickPrompt = ({ tip, icon: Icon }: any) => (
        <button
            onClick={() => { setQuery(tip); }}
            className="flex items-center gap-2 px-3 py-2 bg-white/[0.03] border border-white/[0.08] rounded-lg text-xs font-medium text-slate-300 hover:bg-white/[0.05] hover:text-primary transition-all text-left"
        >
            <Icon size={12} className="text-primary" />
            {tip}
        </button>
    );

    return (
        <>
            {/* Floating Button */}
            <motion.button
                layoutId="ai-bubble"
                onClick={() => setIsOpen(true)}
                className="fixed bottom-6 right-6 z-50 p-4 bg-primary text-background-dark rounded-full shadow-2xl shadow-primary/30 hover:scale-110 active:scale-95 transition-all group"
            >
                <Brain className="group-hover:animate-pulse" />
            </motion.button>

            <AnimatePresence>
                {isOpen && (
                    <div className="fixed inset-0 z-[60] flex items-end justify-end p-6 pointer-events-none">
                        <motion.div
                            layoutId="ai-bubble"
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            className="w-full max-w-md h-[600px] glass-premium rounded-3xl border-white/[0.1] shadow-2xl flex flex-col pointer-events-auto overflow-hidden"
                        >
                            {/* Header */}
                            <div className="p-5 border-b border-white/[0.05] bg-primary/10 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-primary/20 rounded-lg">
                                        <Brain className="text-primary" size={20} />
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-black text-white uppercase tracking-tight">Perplex Intelligence</h3>
                                        <div className="flex items-center gap-1.5">
                                            <div className="size-1.5 bg-primary rounded-full animate-pulse" />
                                            <span className="text-[10px] text-primary font-bold uppercase">Node Active</span>
                                        </div>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="p-2 hover:bg-white/10 rounded-lg text-slate-400 hover:text-white transition-all"
                                >
                                    <X size={18} />
                                </button>
                            </div>

                            {/* Chat View */}
                            <div className="flex-1 overflow-y-auto p-5 space-y-4 scrollbar-hide">
                                {messages.length === 0 && (
                                    <div className="space-y-6 pt-4">
                                        <div className="text-center space-y-2">
                                            <Sparkles className="mx-auto text-primary/40" size={32} />
                                            <p className="text-sm text-slate-400 font-medium">How can I optimize your strategy today?</p>
                                        </div>
                                        <div className="grid grid-cols-1 gap-2">
                                            <QuickPrompt icon={TrendingUp} tip="Analyze my L5 performance" />
                                            <QuickPrompt icon={Target} tip="Find top EV NBA props" />
                                            <QuickPrompt icon={Terminal} tip="Explain the Kelly Criterion edge" />
                                        </div>
                                    </div>
                                )}
                                {messages.map((m, i) => (
                                    <motion.div
                                        key={i}
                                        initial={{ opacity: 0, x: m.role === 'user' ? 20 : -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                    >
                                        <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed ${m.role === 'user'
                                            ? 'bg-primary text-background-dark font-bold'
                                            : 'bg-white/[0.05] border border-white/[0.08] text-slate-200'
                                            }`}>
                                            {m.content}
                                        </div>
                                    </motion.div>
                                ))}
                                {isLoading && (
                                    <div className="flex justify-start">
                                        <div className="bg-white/[0.05] border border-white/[0.08] p-4 rounded-2xl">
                                            <Loader2 className="animate-spin text-primary" size={16} />
                                        </div>
                                    </div>
                                )}
                                <div ref={chatEndRef} />
                            </div>

                            {/* Input Area */}
                            <div className="p-5 border-t border-white/[0.05] bg-white/[0.02]">
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={query}
                                        onChange={(e) => setQuery(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Ask Perplex about market edges..."
                                        className="w-full bg-white/[0.03] border border-white/[0.08] rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-primary/50 transition-colors pr-12"
                                    />
                                    <button
                                        onClick={handleSend}
                                        disabled={!query.trim() || isLoading}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-primary hover:text-white disabled:opacity-30 transition-colors"
                                    >
                                        <Send size={18} />
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </>
    );
}
