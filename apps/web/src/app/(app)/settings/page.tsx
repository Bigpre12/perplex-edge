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

    return (
        <div className="settings-page-wrapper">
            <div className="settings-inner">

                <h1 className="settings-title">⚙️ Settings</h1>

                {/* Profile */}
                <div className="settings-card">
                    <span className="settings-section-label">PROFILE</span>
                    <div className="settings-profile-row">
                        <div className="settings-avatar">
                            {user?.email?.[0].toUpperCase() ?? "U"}
                        </div>
                        <div>
                            <div className="settings-profile-name">{user?.user_metadata?.full_name ?? user?.email?.split('@')[0] ?? "User"}</div>
                            <div className="settings-profile-email">{user?.email ?? ""}</div>
                        </div>
                    </div>
                </div>

                {/* Subscription */}
                <div className="settings-card">
                    <span className="settings-section-label">SUBSCRIPTION TIER</span>
                    <div className="settings-tier-grid">
                        {(["free", "pro", "elite"] as const).map(tier => (
                            <button
                                key={tier}
                                onClick={() => setSubscription(tier)}
                                className={`settings-tier-btn ${subscription === tier ? 'settings-tier-btn-active' : ''}`}
                            >
                                <div className="settings-tier-icon-wrap">
                                    {tier === "free" ? "🔓" : tier === "pro" ? "⚡" : "👑"} {tier.toUpperCase()}
                                </div>
                                <div className={`settings-tier-desc ${subscription === tier ? 'settings-tier-desc-active' : ''}`}>
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
                <div className="settings-card">
                    <span className="settings-section-label">BANKROLL</span>
                    <div className="settings-bankroll-row">
                        <span className="settings-currency-symbol">$</span>
                        <input
                            type="number"
                            value={bankroll}
                            onChange={e => setBankroll(e.target.value)}
                            placeholder="Enter your bankroll"
                            className="settings-input-money"
                        />
                    </div>
                    {bankroll && (
                        <div className="settings-unit-calc">
                            1% unit = <span className="settings-unit-val">${(Number(bankroll) * 0.01).toFixed(2)}</span> &nbsp;|&nbsp;
                            2% unit = <span className="settings-unit-val">${(Number(bankroll) * 0.02).toFixed(2)}</span>
                        </div>
                    )}
                </div>

                {/* Sportsbooks */}
                <div className="settings-card">
                    <span className="settings-section-label">MY SPORTSBOOKS</span>
                    <div className="settings-chip-group">
                        {SPORTSBOOKS.map(b => (
                            <button key={b} onClick={() => toggleItem(selectedBooks, setSelectedBooks, b)} className={`settings-chip ${selectedBooks.includes(b) ? 'settings-chip-active' : ''}`}>
                                {b}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Sports */}
                <div className="settings-card">
                    <span className="settings-section-label">MY SPORTS</span>
                    <div className="settings-chip-group">
                        {SPORTS.map(s => (
                            <button key={s} onClick={() => toggleItem(selectedSports, setSelectedSports, s)} className={`settings-chip ${selectedSports.includes(s) ? 'settings-chip-active' : ''}`}>
                                {s}
                            </button>
                        ))}
                    </div>
                </div>
                

                {/* Notifications */}
                <div className="settings-card">
                    <span className="settings-section-label">NOTIFICATIONS</span>
                    {Object.entries(notifications).map(([key, val]) => (
                        <div key={key} className="settings-notif-row">
                            <div className="settings-notif-label">
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
                                aria-label={`Toggle ${key}`}
                                className={`settings-toggle-track ${val ? 'settings-toggle-track-active' : ''}`}
                            >
                                <div className={`settings-toggle-thumb ${val ? 'settings-toggle-thumb-active' : ''}`} />
                            </button>
                        </div>
                    ))}
                </div>

                {/* Save */}
                <button
                    onClick={handleSave}
                    className={`settings-btn-save ${saved ? 'settings-btn-save-success' : ''}`}
                >
                    {saved ? "✅ Saved!" : "Save Settings"}
                </button>
            </div>
        </div>
    );
}
