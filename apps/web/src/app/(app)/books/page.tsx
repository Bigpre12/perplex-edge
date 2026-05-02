"use client";
import { useState, useEffect } from "react";
import { Database, ShieldCheck, Globe } from "lucide-react";
import { api } from "@/lib/api";

export default function BooksPage() {
    const [books, setBooks] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBooks = async () => {
            setLoading(true);
            const { data } = await api.get("/api/props/books/available?sport=basketball_nba");
            const items = data?.data || data;
            setBooks(Array.isArray(items) ? items : []);
            setLoading(false);
        };
        fetchBooks();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Database className="w-8 h-8 text-[#F5C518]" />
                        Sportsbooks
                    </h1>
                    <p className="text-slate-400 mt-1">Managed connections for real-time odds delivery.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {loading ? (
                    <p className="text-slate-500">Loading bookmaker registry...</p>
                ) : books.length === 0 ? (
                    <p className="text-slate-500">No active bookmakers found for this sport.</p>
                ) : books.map((book, i) => (
                    <div key={i} className="bg-[#12121e] border border-white/5 p-6 rounded-2xl flex items-center justify-between hover:border-[#F5C518]/30 transition-all cursor-pointer group">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-white/5 rounded-xl flex items-center justify-center group-hover:bg-[#F5C518]/10 transition-colors">
                                <Globe className="w-6 h-6 text-slate-400 group-hover:text-[#F5C518]" />
                            </div>
                            <div>
                                <p className="font-bold text-slate-200">{book.name}</p>
                                <p className="text-xs text-slate-500 uppercase tracking-tighter">{book.key}</p>
                            </div>
                        </div>
                        <ShieldCheck className="w-5 h-5 text-green-500/50" />
                    </div>
                ))}
            </div>

            <div className="bg-[#12121e] border border-[#F5C518]/10 p-6 rounded-2xl">
                <h3 className="text-sm font-bold text-[#F5C518] uppercase tracking-widest mb-2">Bookmaker Coverage</h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                    Perplex-Edge monitors over 40+ US and Global sportsbooks. For optimal results, we recommend using Pinnacle for market signals and local books like DraftKings or FanDuel for execution.
                </p>
            </div>
        </div>
    );
}
