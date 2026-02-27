"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, X, Send, Loader2, Sparkles, BrainCircuit } from "lucide-react";
import { getAuthToken } from "@/lib/auth";
import { supabase } from "@/lib/supabaseClient";

import { API_ENDPOINTS } from "@/lib/apiConfig";

interface Message {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: Date;
}

export default function OracleChatbot() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "initial",
            text: "I am the Perplex Oracle. I have live awareness of the entire +EV betting slate. What edge are you looking for today?",
            isUser: false,
            timestamp: new Date()
        }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom of chat
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            text: input,
            isUser: true,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const { data: { session } } = await supabase.auth.getSession();

            const res = await fetch(API_ENDPOINTS.CHATTING, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${getAuthToken() || ''}`
                },
                body: JSON.stringify({
                    message: userMessage.text,
                    user_id: session?.user?.id || "anonymous"
                })
            });

            if (!res.ok) throw new Error("Oracle connection failed.");

            const data = await res.json();

            const oracleMessage: Message = {
                id: (Date.now() + 1).toString(),
                text: data.reply,
                isUser: false,
                timestamp: new Date()
            };

            setMessages(prev => [...prev, oracleMessage]);

        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                id: (Date.now() + 1).toString(),
                text: "My connection to the live engine was severed. Please try again.",
                isUser: false,
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <>
            {/* Floating Action Button */}
            <motion.button
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsOpen(true)}
                className={`fixed bottom-6 right-6 z-50 size-14 rounded-full bg-gradient-to-r from-primary to-emerald-500 shadow-[0_0_25px_rgba(13,242,51,0.4)] flex items-center justify-center border-2 border-primary/50 text-black overflow-hidden group ${isOpen ? 'hidden' : 'flex'}`}
            >
                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                <BrainCircuit size={24} className="relative z-10" />
            </motion.button>

            {/* Chat Panel */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 50, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 50, scale: 0.95 }}
                        transition={{ type: "spring", stiffness: 300, damping: 25 }}
                        className="fixed bottom-6 right-6 z-[60] w-[380px] h-[600px] max-h-[85vh] glass-premium rounded-2xl border border-white/10 shadow-2xl flex flex-col overflow-hidden backdrop-blur-3xl"
                    >
                        {/* Header */}
                        <div className="px-5 py-4 border-b border-slate-800/80 bg-[#0c1416]/80 flex items-center justify-between relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
                            <div className="flex items-center gap-3">
                                <div className="size-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary relative">
                                    <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping opacity-50" />
                                    <Bot size={16} />
                                </div>
                                <div>
                                    <h3 className="text-sm font-black text-white flex items-center gap-1.5">
                                        Perplex Oracle <Sparkles size={12} className="text-primary" />
                                    </h3>
                                    <p className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest flex items-center gap-1">
                                        <span className="size-1.5 rounded-full bg-emerald-400 animate-pulse" /> Live Engine Connected
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="text-slate-500 hover:text-white transition-colors bg-white/5 rounded-full p-1.5"
                            >
                                <X size={16} />
                            </button>
                        </div>

                        {/* Messages Area */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-black/40">
                            {messages.map((msg) => (
                                <motion.div
                                    key={msg.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm ${msg.isUser
                                            ? 'bg-primary text-black font-medium rounded-tr-sm'
                                            : 'glass-panel border-white/5 text-slate-200 rounded-tl-sm shadow-xl'
                                            }`}
                                    >
                                        <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                                        <span className={`text-[9px] mt-2 block font-medium ${msg.isUser ? 'text-black/60' : 'text-slate-500'}`}>
                                            {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </span>
                                    </div>
                                </motion.div>
                            ))}
                            {isLoading && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex justify-start"
                                >
                                    <div className="glass-panel border-white/5 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-2">
                                        <Loader2 size={14} className="animate-spin text-primary" />
                                        <span className="text-xs text-slate-400 font-medium italic">Analyzing edge markets...</span>
                                    </div>
                                </motion.div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="p-4 border-t border-slate-800/80 bg-[#0c1416]/90">
                            <div className="relative flex items-center">
                                <textarea
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={handleKeyPress}
                                    placeholder="Ask the Oracle about live props..."
                                    className="w-full bg-[#050505] border border-slate-700/50 rounded-xl pl-4 pr-12 py-3 text-sm text-white focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 resize-none transition-all custom-scrollbar placeholder:text-slate-600"
                                    rows={1}
                                    style={{ minHeight: '44px', maxHeight: '120px' }}
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={!input.trim() || isLoading}
                                    className="absolute right-2 p-2 bg-primary/10 text-primary hover:bg-primary hover:text-black rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary/10 disabled:hover:text-primary"
                                >
                                    <Send size={16} className={input.trim() && !isLoading ? 'translate-x-0.5 -translate-y-0.5 transition-transform' : ''} />
                                </button>
                            </div>
                            <p className="text-center text-[9px] text-slate-600 mt-2 font-medium">
                                The Oracle analyzes mathematical EV, not financial advice.
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
