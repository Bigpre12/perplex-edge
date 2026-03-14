"use client";
import { useState, useEffect } from "react";
import { Search, X, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api, isApiError } from "@/lib/api";

export function GlobalSearch() {
    const [open, setOpen] = useState(false);
    const [query, setQuery] = useState("");
    const [debouncedQuery, setDebouncedQuery] = useState("");

    // Debounce the search input
    useEffect(() => {
        const timer = setTimeout(() => setDebouncedQuery(query), 300);
        return () => clearTimeout(timer);
    }, [query]);

    // Keyboard shortcut to open (Cmd/Ctrl + K)
    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setOpen(open => !open);
            }
        };
        document.addEventListener("keydown", down);
        return () => document.removeEventListener("keydown", down);
    }, []);

    const { data, isLoading } = useQuery({
        queryKey: ["search", debouncedQuery],
        queryFn: async () => {
            if (debouncedQuery.length < 3) return { results: [] };
            const res = await api.globalSearch(debouncedQuery);
            return isApiError(res) ? { results: [] } : res;
        },
        enabled: debouncedQuery.length >= 3,
    });

    if (!open) {
        return (
            <button
                onClick={() => setOpen(true)}
                className="flex items-center gap-2 bg-gray-900 border border-gray-800 hover:bg-gray-800 text-gray-500 hover:text-gray-300 px-3 py-1.5 rounded-full text-sm transition"
            >
                <Search size={16} />
                <span className="hidden sm:inline">Search props...</span>
                <kbd className="hidden sm:inline ml-2 text-[10px] bg-gray-800 px-1.5 rounded font-mono text-gray-500">⌘K</kbd>
            </button>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-start justify-center pt-24 px-4" onClick={() => setOpen(false)}>
            <div
                className="bg-gray-900 border border-gray-800 w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200"
                onClick={e => e.stopPropagation()}
            >
                <div className="flex items-center p-4 border-b border-gray-800">
                    <Search className="text-gray-500 mr-3" size={20} />
                    <input
                        autoFocus
                        type="text"
                        placeholder="Search players, teams..."
                        className="bg-transparent w-full outline-none text-lg text-white placeholder:text-gray-600"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                    <button onClick={() => setOpen(false)} className="text-gray-500 hover:text-white transition">
                        <X size={20} />
                    </button>
                </div>

                <div className="max-h-96 overflow-y-auto w-full p-2 space-y-1">
                    {query.length < 3 ? (
                        <div className="p-8 text-center text-gray-500 text-sm">Type at least 3 characters to search</div>
                    ) : isLoading ? (
                        <div className="p-8 flex justify-center text-gray-500"><Loader2 className="animate-spin" /></div>
                    ) : data?.results?.length > 0 ? (
                        data.results.map((prop: any) => (
                            <div key={prop.id} className="flex justify-between items-center p-3 hover:bg-gray-800 rounded-xl cursor-pointer group transition">
                                <div>
                                    <h4 className="font-bold text-white group-hover:text-blue-400 transition">{prop.player_name}</h4>
                                    <p className="text-xs text-gray-500">{prop.team} • {prop.sport}</p>
                                </div>
                                <div className="text-right flex items-center gap-4">
                                    {prop.edge_score > 5 && (
                                        <span className="bg-green-500/20 text-green-400 font-bold px-2 py-0.5 rounded text-xs uppercase tracking-wider hidden sm:inline-block">
                                            {prop.edge_score}% Edge
                                        </span>
                                    )}
                                    <div className="font-mono text-sm leading-tight text-right">
                                        <div className="text-gray-300">O {prop.line}</div>
                                        <div className="text-gray-600 text-[10px] uppercase">{prop.prop_type.replace("player_", "")}</div>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="p-8 text-center text-gray-500 text-sm">No active props found for "{query}"</div>
                    )}
                </div>
            </div>
        </div>
    );
}
