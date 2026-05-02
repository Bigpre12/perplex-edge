"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

const COMMANDS = [
    { id: "props", label: "Player Props", icon: "⚡", path: "/player-props", tag: "page" },
    { id: "ev", label: "EV+ Edges", icon: "📈", path: "/ev", tag: "page" },
    { id: "sharp", label: "Sharp Money", icon: "🎯", path: "/sharp", tag: "page" },
    { id: "hitrate", label: "Hit Rate Tracker", icon: "📊", path: "/hit-rate", tag: "page" },
    { id: "parlay", label: "Parlay Builder", icon: "🎰", path: "/parlay", tag: "page" },
    { id: "live", label: "Live Games", icon: "🔴", path: "/live", tag: "page" },
    { id: "move", label: "Line Movement", icon: "📉", path: "/line-movement", tag: "page" },
    { id: "slate", label: "Today's Slate", icon: "📅", path: "/slate", tag: "page" },
    { id: "arb", label: "Arbitrage Finder", icon: "⚖️", path: "/arbitrage", tag: "page" },
    { id: "clv", label: "CLV Tracker", icon: "💹", path: "/clv", tag: "page" },
    { id: "tracker", label: "Bet Tracker", icon: "💰", path: "/bet-tracker", tag: "page" },
    { id: "settings", label: "Settings", icon: "⚙️", path: "/settings", tag: "page" },
    { id: "nba", label: "NBA Props", icon: "🏀", path: "/player-props?sport=basketball_nba", tag: "sport" },
    { id: "nfl", label: "NFL Props", icon: "🏈", path: "/player-props?sport=americanfootball_nfl", tag: "sport" },
    { id: "mlb", label: "MLB Props", icon: "⚾", path: "/player-props?sport=baseball_mlb", tag: "sport" },
    { id: "nhl", label: "NHL Props", icon: "🏒", path: "/player-props?sport=icehockey_nhl", tag: "sport" },
    { id: "mma", label: "MMA Props", icon: "🥊", path: "/player-props?sport=mma_mixed_martial_arts", tag: "sport" },
];

const TAG_COLORS: Record<string, string> = {
    page: "#6366f1",
    sport: "#10b981",
    action: "#f59e0b",
};

export default function CommandCenter() {
    const router = useRouter();
    const [open, setOpen] = useState(false);
    const [query, setQuery] = useState("");
    const [selected, setSelected] = useState(0);
    const [hasOpened, setHasOpened] = useState(false);

    // Keyboard shortcut — Cmd/Ctrl+K
    const handleKeyDown = useCallback((e: KeyboardEvent) => {
        if ((e.metaKey || e.ctrlKey) && e.key === "k") {
            e.preventDefault();
            setOpen(prev => !prev);
            setQuery("");
            setSelected(0);
        }
        if (e.key === "Escape") setOpen(false);
    }, []);

    useEffect(() => {
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [handleKeyDown]);

    const filtered = COMMANDS.filter(c =>
        c.label.toLowerCase().includes(query.toLowerCase()) ||
        c.tag.toLowerCase().includes(query.toLowerCase())
    );

    const handleSelect = (path: string) => {
        router.push(path);
        setOpen(false);
        setQuery("");
    };

    // Arrow key navigation
    const handleInputKey = (e: React.KeyboardEvent) => {
        if (e.key === "ArrowDown") {
            e.preventDefault();
            setSelected(s => Math.min(s + 1, filtered.length - 1));
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setSelected(s => Math.max(s - 1, 0));
        } else if (e.key === "Enter" && filtered[selected]) {
            handleSelect(filtered[selected].path);
        }
    };

    if (!open) return (
        // Floating button to reopen
        <button
            onClick={() => { setOpen(true); setQuery(""); setSelected(0); }}
            title="Command Center (⌘K)"
            className="floating-command-btn"
        >
            ⌘
        </button>
    );

    return (
        <>
            {/* Backdrop */}
            <div
                onClick={() => setOpen(false)}
                className="command-center-backdrop"
            />

            {/* Panel */}
            <div className="command-center-panel">

                {/* Header */}
                <div className="command-center-header">
                    <div className="command-header-row">
                        <span>⚡</span>
                        <span className="command-logo-text">
                            PERPLEX-EDGE COMMAND CENTER
                        </span>
                        <span className="command-esc-tag">ESC to close</span>
                    </div>

                    {/* Search */}
                    <div className="command-center-search-wrap">
                        <span className="command-search-icon">🔍</span>
                        <input
                            autoFocus
                            id="command-center-search"
                            name="command-search"
                            value={query}
                            onChange={e => { setQuery(e.target.value); setSelected(0); }}
                            onKeyDown={handleInputKey}
                            placeholder="Search pages, sports, actions..."
                            className="command-center-input"
                        />
                        <span className="command-kbd-tag">⌘K</span>
                    </div>
                </div>

                {/* Results */}
                <div className="command-center-results">
                    {filtered.length === 0 ? (
                        <div className="command-empty-state">
                            No results for "{query}"
                        </div>
                    ) : (
                        filtered.map((cmd, i) => (
                            <div
                                key={cmd.id}
                                onClick={() => handleSelect(cmd.path)}
                                onMouseEnter={() => setSelected(i)}
                                className={`command-center-item ${selected === i ? 'command-center-item-selected' : ''}`}
                            >
                                <span className="command-item-icon">{cmd.icon}</span>
                                <span className="command-item-label">
                                    {cmd.label}
                                </span>
                                <span className={`command-item-tag command-item-tag-${cmd.tag}`}>
                                    {cmd.tag}
                                </span>
                                {selected === i && (
                                    <span className="command-enter-icon">↵</span>
                                )}
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div className="command-center-footer">
                    <span>↑↓ Navigate</span>
                    <span>↵ Select</span>
                    <span>ESC Close</span>
                    <span className="command-center-footer-hint">⌘K to reopen anytime</span>
                </div>
            </div>

            <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to   { opacity: 1; }
        }
        @keyframes slideDown {
          from { opacity: 0; transform: translateX(-50%) translateY(-12px); }
          to   { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
      `}</style>
        </>
    );
}
