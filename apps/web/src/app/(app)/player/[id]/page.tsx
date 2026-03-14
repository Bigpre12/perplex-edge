// apps/web/src/app/(app)/player/[id]/page.tsx
"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, isApiError } from "@/lib/api";

interface PlayerProfile {
    player_name: string;
    team: string;
    sport: string;
    position: string;
    injury_status: string | null;
    stats: StatLine[];
    props: PropLine[];
    hit_rates: HitRate[];
}

interface StatLine {
    game_date: string;
    opponent: string;
    stat_type: string;
    value: number;
}

interface PropLine {
    stat_type: string;
    line: number;
    pick: string;
    odds: number;
    ev_percentage: number;
    confidence: string;
    book: string;
}

interface HitRate {
    stat_type: string;
    hit_rate: number;
    total_picks: number;
    hits: number;
    avg_ev: number;
}

export default function PlayerProfilePage() {
    const params = useParams();
    const id = params?.id;
    const playerName = decodeURIComponent(id as string).replace(/-/g, " ");
    const [profile, setProfile] = useState<PlayerProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<"props" | "stats" | "hitrate">("props");

    useEffect(() => {
        if (!playerName) return;
        const fetchProfile = async () => {
            try {
                const data = await api.playerProfile(playerName);
                if (!isApiError(data)) {
                    setProfile(data);
                } else {
                    setProfile(null);
                }
            } catch {
                setProfile(null);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [playerName]);

    if (loading) return <div style={{ background: "#0f1117", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", color: "#6b7280" }}>Loading player...</div>;
    if (!profile) return <div style={{ background: "#0f1117", minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", color: "#6b7280" }}>Player not found.</div>;

    const tabStyle = (active: boolean) => ({
        padding: "8px 20px", borderRadius: "8px", border: "none",
        background: active ? "#6366f1" : "transparent",
        color: active ? "#fff" : "#6b7280",
        fontSize: "13px", fontWeight: 700, cursor: "pointer"
    });

    return (
        <div style={{ background: "#0f1117", minHeight: "100vh", padding: "24px", color: "#fff" }}>
            <div style={{ maxWidth: "900px", margin: "0 auto" }}>

                {/* Header */}
                <div style={{ background: "#1a1d2e", borderRadius: "12px", padding: "24px", border: "1px solid #2d3748", marginBottom: "20px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <div>
                            <h1 style={{ fontSize: "28px", fontWeight: 900, margin: 0 }}>{profile.player_name}</h1>
                            <div style={{ fontSize: "14px", color: "#9ca3af", marginTop: "4px" }}>
                                {profile.team} · {profile.sport} · {profile.position}
                            </div>
                        </div>
                        {profile.injury_status && (
                            <span style={{
                                padding: "6px 14px", borderRadius: "8px", fontSize: "12px", fontWeight: 700,
                                background: "#7f1d1d", color: "#f87171"
                            }}>
                                🚑 {profile.injury_status}
                            </span>
                        )}
                    </div>

                    {/* Hit rate summary */}
                    <div style={{ display: "flex", gap: "16px", marginTop: "20px", flexWrap: "wrap" }}>
                        {profile.hit_rates.slice(0, 4).map((hr, i) => (
                            <div key={i} style={{ background: "#0f1117", borderRadius: "8px", padding: "12px 16px", minWidth: "120px" }}>
                                <div style={{ fontSize: "10px", color: "#6b7280", fontWeight: 700, letterSpacing: "0.05em" }}>
                                    {hr.stat_type.toUpperCase()}
                                </div>
                                <div style={{ fontSize: "22px", fontWeight: 900, color: hr.hit_rate >= 65 ? "#10b981" : hr.hit_rate >= 55 ? "#60a5fa" : "#9ca3af" }}>
                                    {hr.hit_rate}%
                                </div>
                                <div style={{ fontSize: "10px", color: "#4b5563" }}>{hr.hits}/{hr.total_picks} picks</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Tabs */}
                <div style={{ display: "flex", gap: "4px", marginBottom: "16px", background: "#1a1d2e", borderRadius: "10px", padding: "4px", border: "1px solid #2d3748" }}>
                    <button style={tabStyle(activeTab === "props")} onClick={() => setActiveTab("props")}>Today's Props</button>
                    <button style={tabStyle(activeTab === "stats")} onClick={() => setActiveTab("stats")}>Recent Stats</button>
                    <button style={tabStyle(activeTab === "hitrate")} onClick={() => setActiveTab("hitrate")}>Hit Rates</button>
                </div>

                {/* Props tab */}
                {activeTab === "props" && (
                    <div style={{ display: "grid", gap: "10px" }}>
                        {profile.props.length === 0 && <div style={{ color: "#6b7280", textAlign: "center", padding: "40px" }}>No props available today.</div>}
                        {profile.props.map((prop, i) => (
                            <div key={i} style={{ background: "#1a1d2e", borderRadius: "10px", padding: "16px 20px", border: "1px solid #2d3748", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <div>
                                    <div style={{ fontSize: "14px", fontWeight: 700 }}>{prop.stat_type} {prop.pick.toUpperCase()} {prop.line}</div>
                                    <div style={{ fontSize: "12px", color: "#6b7280" }}>{prop.book}</div>
                                </div>
                                <div style={{ fontSize: "22px", fontWeight: 900, color: "#10b981" }}>
                                    {prop.ev_percentage > 0 ? "+" : ""}{prop.ev_percentage}% EV
                                </div>
                                <div style={{ textAlign: "right" }}>
                                    <div style={{ fontSize: "15px", fontWeight: 700 }}>{prop.odds > 0 ? `+${prop.odds}` : prop.odds}</div>
                                    <div style={{
                                        padding: "2px 8px", borderRadius: "4px", fontSize: "10px", fontWeight: 700, marginTop: "4px",
                                        background: prop.confidence === "HIGH" ? "#064e3b" : "#1f2937",
                                        color: prop.confidence === "HIGH" ? "#10b981" : "#9ca3af",
                                        display: "inline-block"
                                    }}>{prop.confidence}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Stats tab */}
                {activeTab === "stats" && (
                    <div style={{ background: "#1a1d2e", borderRadius: "12px", border: "1px solid #2d3748", overflow: "hidden" }}>
                        <table style={{ width: "100%", borderCollapse: "collapse" }}>
                            <thead>
                                <tr style={{ background: "#111827" }}>
                                    {["Date", "Opponent", "Stat", "Value"].map(h => (
                                        <th key={h} style={{ padding: "12px 16px", fontSize: "11px", color: "#6b7280", fontWeight: 700, textAlign: "left" }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {profile.stats.map((s, i) => (
                                    <tr key={i} style={{ borderTop: "1px solid #1f2937" }}>
                                        <td style={{ padding: "12px 16px", fontSize: "12px", color: "#9ca3af" }}>{new Date(s.game_date).toLocaleDateString()}</td>
                                        <td style={{ padding: "12px 16px", fontSize: "13px", fontWeight: 600 }}>{s.opponent}</td>
                                        <td style={{ padding: "12px 16px", fontSize: "12px", color: "#9ca3af" }}>{s.stat_type}</td>
                                        <td style={{ padding: "12px 16px", fontSize: "15px", fontWeight: 800, color: "#fff" }}>{s.value}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Hit rate tab */}
                {activeTab === "hitrate" && (
                    <div style={{ display: "grid", gap: "10px" }}>
                        {profile.hit_rates.map((hr, i) => (
                            <div key={i} style={{ background: "#1a1d2e", borderRadius: "10px", padding: "16px 20px", border: "1px solid #2d3748", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                <div style={{ fontSize: "14px", fontWeight: 700 }}>{hr.stat_type}</div>
                                <div style={{ fontSize: "24px", fontWeight: 900, color: hr.hit_rate >= 65 ? "#10b981" : hr.hit_rate >= 55 ? "#60a5fa" : "#9ca3af" }}>
                                    {hr.hit_rate}%
                                </div>
                                <div style={{ textAlign: "center" }}>
                                    <div style={{ fontSize: "13px", color: "#9ca3af" }}>{hr.hits}/{hr.total_picks} hits</div>
                                    <div style={{ fontSize: "11px", color: "#6b7280" }}>Avg EV: +{hr.avg_ev}%</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
