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
    { id: "move", label: "Line Movement", icon: "📉", path: "/move", tag: "page" },
    { id: "slate", label: "Today's Slate", icon: "📅", path: "/today-slate", tag: "page" },
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

    // Open on first load
    useEffect(() => {
        const alreadyShown = sessionStorage.getItem("cmd-shown");
        if (!alreadyShown) {
            setTimeout(() => {
                setOpen(true);
                setHasOpened(true);
                sessionStorage.setItem("cmd-shown", "1");
            }, 600); // slight delay so page renders first
        }
    }, []);

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
            style={{
                position: "fixed",
                bottom: "24px",
                right: "24px",
                zIndex: 998,
                width: "48px",
                height: "48px",
                borderRadius: "50%",
                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                border: "none",
                color: "#fff",
                fontSize: "20px",
                cursor: "pointer",
                boxShadow: "0 4px 20px rgba(99,102,241,0.5)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                transition: "transform 0.2s",
            }}
            onMouseEnter={e => (e.currentTarget.style.transform = "scale(1.1)")}
            onMouseLeave={e => (e.currentTarget.style.transform = "scale(1)")}
        >
            ⌘
        </button>
    );

    return (
        <>
            {/* Backdrop */}
            <div
                onClick={() => setOpen(false)}
                style={{
                    position: "fixed", inset: 0, zIndex: 999,
                    background: "rgba(0,0,0,0.7)",
                    backdropFilter: "blur(4px)",
                    animation: "fadeIn 0.15s ease",
                }}
            />

            {/* Panel */}
            <div style={{
                position: "fixed",
                top: "15%",
                left: "50%",
                transform: "translateX(-50%)",
                zIndex: 1000,
                width: "min(620px, 92vw)",
                background: "#0f1117",
                borderRadius: "16px",
                border: "1px solid #2d3748",
                boxShadow: "0 25px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(99,102,241,0.2)",
                overflow: "hidden",
                animation: "slideDown 0.2s ease",
            }}>

                {/* Header */}
                <div style={{
                    padding: "16px 20px 0",
                    borderBottom: "1px solid #1f2937",
                }}>
                    <div style={{
                        display: "flex", alignItems: "center", gap: "12px",
                        marginBottom: "14px",
                    }}>
                        <span style={{ fontSize: "20px" }}>⚡</span>
                        <span style={{ fontWeight: 900, fontSize: "16px", color: "#fff", letterSpacing: "0.02em" }}>
                            LUCRIX COMMAND CENTER
                        </span>
                        <span style={{
                            marginLeft: "auto", fontSize: "10px", color: "#4b5563",
                            background: "#1f2937", padding: "3px 8px", borderRadius: "6px",
                            fontWeight: 700, letterSpacing: "0.05em"
                        }}>ESC to close</span>
                    </div>

                    {/* Search */}
                    <div style={{ position: "relative", marginBottom: "12px" }}>
                        <span style={{
                            position: "absolute", left: "12px", top: "50%",
                            transform: "translateY(-50%)", color: "#4b5563", fontSize: "16px"
                        }}>🔍</span>
                        <input
                            autoFocus
                            value={query}
                            onChange={e => { setQuery(e.target.value); setSelected(0); }}
                            onKeyDown={handleInputKey}
                            placeholder="Search pages, sports, actions..."
                            style={{
                                width: "100%", padding: "10px 12px 10px 38px",
                                background: "#1a1d2e", border: "1px solid #2d3748",
                                borderRadius: "10px", color: "#fff", fontSize: "14px",
                                outline: "none", boxSizing: "border-box",
                            }}
                        />
                        <span style={{
                            position: "absolute", right: "12px", top: "50%",
                            transform: "translateY(-50%)", fontSize: "10px",
                            color: "#4b5563", fontWeight: 700,
                            background: "#111827", padding: "2px 6px", borderRadius: "4px"
                        }}>⌘K</span>
                    </div>
                </div>

                {/* Results */}
                <div style={{ maxHeight: "380px", overflowY: "auto", padding: "8px" }}>
                    {filtered.length === 0 ? (
                        <div style={{ textAlign: "center", padding: "40px", color: "#4b5563", fontSize: "14px" }}>
                            No results for "{query}"
                        </div>
                    ) : (
                        filtered.map((cmd, i) => (
                            <div
                                key={cmd.id}
                                onClick={() => handleSelect(cmd.path)}
                                onMouseEnter={() => setSelected(i)}
                                style={{
                                    display: "flex", alignItems: "center", gap: "12px",
                                    padding: "10px 12px", borderRadius: "10px", cursor: "pointer",
                                    background: selected === i ? "#1a1d2e" : "transparent",
                                    border: selected === i ? "1px solid #2d3748" : "1px solid transparent",
                                    transition: "all 0.1s",
                                    marginBottom: "2px",
                                }}
                            >
                                <span style={{
                                    fontSize: "20px", width: "32px", height: "32px",
                                    display: "flex", alignItems: "center", justifyContent: "center",
                                    background: "#111827", borderRadius: "8px", flexShrink: 0,
                                }}>{cmd.icon}</span>
                                <span style={{ flex: 1, fontWeight: 600, fontSize: "14px", color: "#e5e7eb" }}>
                                    {cmd.label}
                                </span>
                                <span style={{
                                    fontSize: "10px", fontWeight: 700, padding: "2px 8px",
                                    borderRadius: "20px", letterSpacing: "0.05em",
                                    background: `${TAG_COLORS[cmd.tag]}20`,
                                    color: TAG_COLORS[cmd.tag],
                                    textTransform: "uppercase",
                                }}>
                                    {cmd.tag}
                                </span>
                                {selected === i && (
                                    <span style={{ fontSize: "11px", color: "#4b5563", fontWeight: 700 }}>↵</span>
                                )}
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div style={{
                    padding: "10px 20px",
                    borderTop: "1px solid #1f2937",
                    display: "flex", gap: "16px",
                    fontSize: "11px", color: "#4b5563",
                }}>
                    <span>↑↓ Navigate</span>
                    <span>↵ Select</span>
                    <span>ESC Close</span>
                    <span style={{ marginLeft: "auto" }}>⌘K to reopen anytime</span>
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
