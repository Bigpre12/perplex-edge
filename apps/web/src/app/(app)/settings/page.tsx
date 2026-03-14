"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { PRICING } from "@/constants/pricing";

const SPORTSBOOKS = ["DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet", "BetRivers", "ESPNBet"];
const SPORTS = ["NBA", "NFL", "MLB", "NHL", "NCAAB", "WNBA", "MMA", "Tennis"];

export default function SettingsPage() {
    const { user, loading, isSignedIn } = useAuth();
    const router = useRouter();
    const [bankroll, setBankroll] = useState("");
    const [selectedBooks, setSelectedBooks] = useState<string[]>(["DraftKings", "FanDuel"]);
    const [selectedSports, setSelectedSports] = useState<string[]>(["NBA", "NFL"]);
    const [notifications, setNotifications] = useState({
        lineMovement: true,
        injuryAlerts: true,
        highEVProps: true,
        parlayHits: false,
        dailyDigest: true,
    });
    const [subscription, setSubscription] = useState<"free" | "pro" | "elite">("free");
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        if (!loading && !isSignedIn) {
            router.push("/login");
            return;
        }

        const stored = localStorage.getItem("pe_settings");
        if (stored) {
            const s = JSON.parse(stored);
            setBankroll(s.bankroll || "");
            setSelectedBooks(s.selectedBooks || ["DraftKings", "FanDuel"]);
            setSelectedSports(s.selectedSports || ["NBA", "NFL"]);
            setNotifications(s.notifications || notifications);
            setSubscription(s.subscription || "free");
        }
    }, []);

    const handleSave = () => {
        localStorage.setItem("pe_settings", JSON.stringify({
            bankroll, selectedBooks, selectedSports, notifications, subscription
        }));
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const toggleItem = (list: string[], setList: (v: string[]) => void, item: string) => {
        setList(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);
    };

    const sectionStyle = { background: "#1a1d2e", borderRadius: "12px", padding: "20px", border: "1px solid #2d3748", marginBottom: "16px" };
    const labelStyle = { fontSize: "11px", color: "#6b7280", fontWeight: 700 as const, letterSpacing: "0.05em", marginBottom: "12px", display: "block" as const };
    const chipStyle = (active: boolean) => ({
        padding: "6px 14px", borderRadius: "6px", border: "none",
        background: active ? "#6366f1" : "#1f2937",
        color: active ? "#fff" : "#9ca3af",
        fontSize: "12px", fontWeight: 600 as const, cursor: "pointer" as const,
    });

    return (
        <div style={{ background: "#0f1117", minHeight: "100vh", padding: "24px", color: "#fff" }}>
            <div style={{ maxWidth: "700px", margin: "0 auto" }}>

                <h1 style={{ fontSize: "24px", fontWeight: 800, marginBottom: "24px" }}>⚙️ Settings</h1>

                {/* Profile */}
                <div style={sectionStyle}>
                    <span style={labelStyle}>PROFILE</span>
                    <div style={{ display: "flex", alignItems: "center", gap: "14px" }}>
                        <div style={{ width: "48px", height: "48px", borderRadius: "50%", background: "#6366f1", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "20px", fontWeight: 800 }}>
                            {user?.email?.[0].toUpperCase() ?? "U"}
                        </div>
                        <div>
                            <div style={{ fontWeight: 700 }}>{user?.user_metadata?.full_name ?? user?.email?.split('@')[0] ?? "User"}</div>
                            <div style={{ fontSize: "12px", color: "#6b7280" }}>{user?.email ?? ""}</div>
                        </div>
                    </div>
                </div>

                {/* Subscription */}
                <div style={sectionStyle}>
                    <span style={labelStyle}>SUBSCRIPTION TIER</span>
                    <div style={{ display: "flex", gap: "10px" }}>
                        {(["free", "pro", "elite"] as const).map(tier => (
                            <button
                                key={tier}
                                onClick={() => setSubscription(tier)}
                                style={{
                                    ...chipStyle(subscription === tier),
                                    flex: 1, padding: "12px",
                                    border: subscription === tier ? "1px solid #6366f1" : "1px solid #2d3748",
                                }}
                            >
                                <div style={{ fontSize: "14px", marginBottom: "4px" }}>
                                    {tier === "free" ? "🔓" : tier === "pro" ? "⚡" : "👑"} {tier.toUpperCase()}
                                </div>
                                <div style={{ fontSize: "10px", color: subscription === tier ? "#c7d2fe" : "#6b7280" }}>
                                    {tier === "free"
                                        ? PRICING.FREE.description
                                        : tier === "pro"
                                            ? `$${PRICING.PRO.monthly}/mo · ${PRICING.PRO.description}`
                                            : `$${PRICING.ELITE.monthly}/mo · ${PRICING.ELITE.description}`}
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Bankroll */}
                <div style={sectionStyle}>
                    <span style={labelStyle}>BANKROLL</span>
                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                        <span style={{ fontSize: "20px", color: "#10b981", fontWeight: 700 }}>$</span>
                        <input
                            type="number"
                            value={bankroll}
                            onChange={e => setBankroll(e.target.value)}
                            placeholder="Enter your bankroll"
                            style={{
                                background: "#0f1117", border: "1px solid #2d3748", borderRadius: "8px",
                                padding: "10px 14px", color: "#fff", fontSize: "16px", fontWeight: 700,
                                width: "100%", outline: "none"
                            }}
                        />
                    </div>
                    {bankroll && (
                        <div style={{ marginTop: "10px", fontSize: "12px", color: "#6b7280" }}>
                            1% unit = <span style={{ color: "#10b981", fontWeight: 700 }}>${(Number(bankroll) * 0.01).toFixed(2)}</span> &nbsp;|&nbsp;
                            2% unit = <span style={{ color: "#10b981", fontWeight: 700 }}>${(Number(bankroll) * 0.02).toFixed(2)}</span>
                        </div>
                    )}
                </div>

                {/* Sportsbooks */}
                <div style={sectionStyle}>
                    <span style={labelStyle}>MY SPORTSBOOKS</span>
                    <div style={{ display: "flex", flexWrap: "wrap" as const, gap: "8px" }}>
                        {SPORTSBOOKS.map(b => (
                            <button key={b} onClick={() => toggleItem(selectedBooks, setSelectedBooks, b)} style={chipStyle(selectedBooks.includes(b))}>
                                {b}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Sports */}
                <div style={sectionStyle}>
                    <span style={labelStyle}>MY SPORTS</span>
                    <div style={{ display: "flex", flexWrap: "wrap" as const, gap: "8px" }}>
                        {SPORTS.map(s => (
                            <button key={s} onClick={() => toggleItem(selectedSports, setSelectedSports, s)} style={chipStyle(selectedSports.includes(s))}>
                                {s}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Notifications */}
                <div style={sectionStyle}>
                    <span style={labelStyle}>NOTIFICATIONS</span>
                    {Object.entries(notifications).map(([key, val]) => (
                        <div key={key} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: "1px solid #1f2937" }}>
                            <div style={{ fontSize: "13px", fontWeight: 600 }}>
                                {{
                                    lineMovement: "📊 Line Movement Alerts",
                                    injuryAlerts: "🚑 Injury Alerts",
                                    highEVProps: "⚡ High EV Props",
                                    parlayHits: "🎯 Parlay Hits",
                                    dailyDigest: "📬 Daily Digest",
                                }[key]}
                            </div>
                            <button
                                onClick={() => setNotifications(n => ({ ...n, [key]: !val }))}
                                style={{
                                    width: "44px", height: "24px", borderRadius: "12px", border: "none",
                                    background: val ? "#6366f1" : "#374151", cursor: "pointer",
                                    position: "relative" as const, transition: "background 0.2s"
                                }}
                            >
                                <div style={{
                                    width: "18px", height: "18px", borderRadius: "50%", background: "#fff",
                                    position: "absolute" as const, top: "3px",
                                    left: val ? "23px" : "3px", transition: "left 0.2s"
                                }} />
                            </button>
                        </div>
                    ))}
                </div>

                {/* Save */}
                <button
                    onClick={handleSave}
                    style={{
                        width: "100%", padding: "14px", borderRadius: "10px", border: "none",
                        background: saved ? "#10b981" : "#6366f1",
                        color: "#fff", fontSize: "15px", fontWeight: 800, cursor: "pointer",
                        transition: "background 0.3s"
                    }}
                >
                    {saved ? "✅ Saved!" : "Save Settings"}
                </button>
            </div>
        </div>
    );
}
