"use client";

import { useState, useRef, useEffect, useCallback } from "react";

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

import { useGate } from "@/hooks/useGate";
import { api, isApiError } from "@/lib/api";

export default function OracleChatbot() {
    const { tier, oracleLimit } = useGate();
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
        const updated = [...messages, userMsg];
        setMessages(updated);
        setInput("");
        setLoading(true);

        try {
            const res = await api.oracle({ messages: updated });

            if (!isApiError(res)) {
                setMessages((prev) => [
                    ...prev,
                    { role: "assistant", content: res.message ?? "No response from Oracle." },
                ]);
            } else {
                throw new Error(res.message);
            }
        } catch {
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: "Connection lost. Try again." },
            ]);
        } finally {
            setLoading(false);
        }
    }, [messages, loading]);

    const reset = () => setMessages([INITIAL_MESSAGE]);

    return (
        <>
            {/* Floating Button — right side, above Command Center */}
            <button
                onClick={() => setOpen(!open)}
                aria-label="Toggle Oracle"
                className="fixed bottom-24 right-6 z-50 w-14 h-14 rounded-full bg-purple-600 hover:bg-purple-500 active:scale-95 text-white shadow-xl flex items-center justify-center text-2xl transition-all duration-200"
            >
                {open ? "✕" : "🔮"}
            </button>

            {/* Chat Window */}
            {open && (
                <div className="fixed bottom-40 right-6 z-50 w-80 sm:w-96 h-[520px] bg-gray-950 border border-purple-800/60 rounded-2xl shadow-2xl flex flex-col overflow-hidden">

                    {/* Header */}
                    <div className="flex items-center justify-between px-4 py-3 bg-purple-900/30 border-b border-purple-800/50">
                        <div className="flex items-center gap-2">
                            <span className="text-lg">🔮</span>
                            <span className="font-bold text-white text-sm tracking-wide">Oracle</span>
                            <span className="text-xs text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full border border-green-400/20">
                                LIVE
                            </span>
                        </div>
                        <button
                            onClick={reset}
                            className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
                        >
                            Clear
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-gray-700">
                        {messages.map((msg, i) => (
                            <div
                                key={i}
                                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                            >
                                {msg.role === "assistant" && (
                                    <span className="text-base mr-2 mt-1 flex-shrink-0">🔮</span>
                                )}
                                <div
                                    className={`max-w-[82%] px-3 py-2 rounded-xl text-sm leading-relaxed whitespace-pre-wrap ${msg.role === "user"
                                        ? "bg-purple-600 text-white rounded-br-none"
                                        : "bg-gray-800/80 text-gray-100 rounded-bl-none border border-gray-700/50"
                                        }`}
                                >
                                    {msg.content}
                                </div>
                            </div>
                        ))}

                        {/* Typing indicator */}
                        {loading && (
                            <div className="flex justify-start items-center gap-2">
                                <span className="text-base">🔮</span>
                                <div className="bg-gray-800 px-4 py-3 rounded-xl rounded-bl-none border border-gray-700/50">
                                    <div className="flex gap-1">
                                        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                                        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                                        <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>

                    {/* Suggestions — only on first message */}
                    {messages.length <= 1 && (
                        <div className="px-3 pb-2 flex flex-wrap gap-1.5">
                            {SUGGESTIONS.map((s) => (
                                <button
                                    key={s}
                                    onClick={() => ask(s)}
                                    className="text-xs bg-purple-900/40 hover:bg-purple-700/60 text-purple-300 px-2.5 py-1 rounded-full border border-purple-700/50 transition-all duration-150"
                                >
                                    {s}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input */}
                    <div className="flex flex-col border-t border-purple-800/50">
                        {messages.length > oracleLimit * 2 && tier === "free" ? (
                            <div className="p-4 text-center bg-purple-900/20">
                                <p className="text-xs text-gray-400">Daily Oracle limit reached</p>
                                <a href="/pricing" className="text-purple-400 font-bold text-xs hover:underline mt-1 inline-block">
                                    Upgrade to Pro for Unlimited Oracle →
                                </a>
                            </div>
                        ) : (
                            <div className="p-3 flex gap-2">
                                <input
                                    ref={inputRef}
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && ask(input)}
                                    placeholder="Ask Oracle..."
                                    disabled={loading}
                                    className="flex-1 bg-gray-800/80 text-white text-sm rounded-xl px-3 py-2 outline-none border border-gray-700/50 focus:border-purple-500 placeholder-gray-500 disabled:opacity-50 transition-colors"
                                />
                                <button
                                    onClick={() => ask(input)}
                                    disabled={loading || !input.trim()}
                                    className="bg-purple-600 hover:bg-purple-500 disabled:opacity-40 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-150 active:scale-95"
                                >
                                    {loading ? "..." : "→"}
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}
