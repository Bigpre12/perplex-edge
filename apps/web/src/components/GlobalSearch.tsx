"use client";
import { useState, useEffect } from "react";
import { Search, X, Loader2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import API, { isApiError } from "@/lib/api";

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
            const res = await API.search(debouncedQuery);
            return isApiError(res) ? { results: [] } : res;
        },
        enabled: debouncedQuery.length >= 3,
    });

    if (!open) {
        return (
            <button
                onClick={() => setOpen(true)}
                className="flex items-center gap-2 bg-lucrix-surface border border-lucrix-border hover:bg-lucrix-elevated text-textSecondary hover:text-white px-3 py-1.5 rounded-full text-sm transition"
            >
                <Search size={16} />
                <span className="hidden sm:inline">Search props...</span>
                <kbd className="hidden sm:inline ml-2 text-[10px] bg-lucrix-border px-1.5 rounded font-mono text-textMuted">⌘K</kbd>
            </button>
        );
    }

    return (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-start justify-center pt-24 px-4" onClick={() => setOpen(false)}>
            <div
                className="bg-lucrix-dark border border-lucrix-border w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200"
                onClick={e => e.stopPropagation()}
            >
                <div className="flex items-center p-4 border-b border-lucrix-border">
                    <Search className="text-textSecondary mr-3" size={20} />
                    <input
                        autoFocus
                        id="global-search-overlay"
                        name="overlay-search"
                        type="text"
                        placeholder="Search players, teams..."
                        className="bg-transparent w-full outline-none text-lg text-white placeholder:text-textMuted font-display"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                    <button onClick={() => setOpen(false)} className="text-textSecondary hover:text-white transition" aria-label="Close search">
                        <X size={20} />
                    </button>
                </div>

                <div className="max-h-96 overflow-y-auto w-full p-2 space-y-1 scrollbar-none">
                    {query.length < 3 ? (
                        <div className="p-8 text-center text-textMuted text-sm font-medium">Type at least 3 characters to search</div>
                    ) : isLoading ? (
                        <div className="p-8 flex justify-center text-textSecondary"><Loader2 className="animate-spin" /></div>
                    ) : (data as any)?.results?.length > 0 ? (
                        (data as any).results.map((prop: any) => (
                            <div key={prop.id} className="flex justify-between items-center p-3 hover:bg-lucrix-elevated rounded-xl cursor-pointer group transition">
                                <div>
                                    <h4 className="font-bold text-white group-hover:text-brand-cyan transition">{prop.player_name}</h4>
                                    <p className="text-xs text-textSecondary">{prop.team} • {prop.sport}</p>
                                </div>
                                <div className="text-right flex items-center gap-4">
                                    {prop.edge_score > 5 && (
                                        <span className="bg-brand-success/10 text-brand-success font-bold px-2 py-0.5 rounded text-[10px] uppercase tracking-wider hidden sm:inline-block">
                                            {prop.edge_score}% Edge
                                        </span>
                                    )}
                                    <div className="font-mono text-sm leading-tight text-right">
                                        <div className="text-white font-bold">O {prop.line}</div>
                                        <div className="text-textMuted text-[10px] uppercase">{(prop.prop_type || "").replace("player_", "")}</div>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="p-8 text-center text-textMuted text-sm font-medium">No active props found for "{query}"</div>
                    )}
                </div>
            </div>
        </div>
    );
}
