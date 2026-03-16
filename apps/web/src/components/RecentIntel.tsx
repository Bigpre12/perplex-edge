"use client";
import { useEffect, useState } from "react";
import { api, isApiError, API } from "@/lib/api";

interface IntelItem {
    id: string;
    type: "SHARP" | "INJURY" | "LINE" | "NEWS";
    message: string;
    timestamp: string;
}

export default function RecentIntel({ sport = "basketball_nba" }) {
    const [intel, setIntel] = useState<IntelItem[]>([]);
    const [loading, setLoading] = useState(true);

    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        const fetchIntel = async () => {
            const results: IntelItem[] = [];

            // 1. ESPN Injuries — real GTD/OUT data
            try {
                const injRes = await fetch(
                    "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries"
                );
                if (injRes.ok) {
                    const data = await injRes.json();
                    // DEBUG: Log raw response to verify structure
                    console.log("ESPN INJURIES RAW:", JSON.stringify(data, null, 2));

                    // ESPN injuries structure: data.injuries[] each has .team and .injuries[]
                    const teams = data.injuries ?? [];
                    let count = 0;

                    for (const teamEntry of teams) {
                        if (count >= 10) break; // Increased limit to show more data
                        const teamName = teamEntry.displayName ?? teamEntry.team?.displayName ?? "";

                        for (const inj of (teamEntry.injuries ?? [])) {
                            if (count >= 10) break;
                            const player = inj.athlete?.displayName ?? inj.athlete?.shortName ?? "";
                            const status = inj.status ?? inj.type?.description ?? "GTD";
                            const comment = inj.shortComment ?? "";
                            const date = inj.date ?? new Date().toISOString();

                            if (!player) continue;

                            results.push({
                                id: `inj-${count}-${player}`,
                                type: "INJURY",
                                message: comment ? `${comment} (${teamName})` : `${player} (${teamName}) — ${status}. Monitor for line movement.`,
                                timestamp: date,
                            });
                            count++;
                        }
                    }
                }
            } catch (e) {
                console.warn("ESPN Injuries error:", e);
            }

            // 2. ESPN NBA News — real headlines
            try {
                const newsRes = await fetch(
                    "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news"
                );
                if (newsRes.ok) {
                    const data = await newsRes.json();
                    const articles = data.articles ?? [];
                    articles.slice(0, 3).forEach((a: any, i: number) => {
                        results.push({
                            id: `news-${i}-${a.headline?.slice(0, 10)}`,
                            type: "NEWS",
                            message: a.headline ?? "",
                            timestamp: a.published ?? new Date().toISOString(),
                        });
                    });
                }
            } catch (e) {
                console.warn("ESPN News error:", e);
            }

            // 3. Sharp/Steam from your backend
            try {
                const data = await API.alerts(sport as any);
                if (!isApiError(data)) {
                    const alerts = Array.isArray(data.alerts) ? data.alerts : (Array.isArray(data) ? data : []);
                    alerts.slice(0, 3).forEach((a: any) => {
                        results.push({
                            id: a.id || Math.random().toString(),
                            type: "SHARP",
                            message: a.message || `${a.player} ${a.stat} move detected`,
                            timestamp: a.timestamp || a.alert_time || new Date().toISOString(),
                        });
                    });
                }
            } catch (e) {
                // silent fail — steam data is optional and might 404 until backend is fully stable
            }

            if (results.length > 0) {
                // 4. Deduplicate by message
                const seen = new Set<string>();
                const unique = results.filter(r => {
                    if (seen.has(r.message)) return false;
                    seen.add(r.message);
                    return true;
                });

                // Sort by timestamp
                setIntel(unique.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()));
            }
            setLoading(false);
        };

        fetchIntel();
        const timer = setInterval(fetchIntel, 5 * 60_000); // refresh every 5 min
        return () => clearInterval(timer);
    }, [sport]);

    const formatTime = (iso: string) => {
        try {
            const diff = Date.now() - new Date(iso).getTime();
            const mins = Math.floor(diff / 60000);
            if (mins < 1) return `just now`;
            if (mins < 60) return `${mins}m ago`;
            const hrs = Math.floor(mins / 60);
            if (hrs < 24) return `${hrs}h ago`;
            return new Date(iso).toLocaleDateString();
        } catch {
            return "—";
        }
    };

    const typeConfig: Record<string, { label: string; color: string; bgColor: string }> = {
        SHARP:  { label: "SHARP",  color: "text-brand-orange", bgColor: "bg-brand-orange/10" },
        INJURY: { label: "INJURY", color: "text-brand-danger", bgColor: "bg-brand-danger/10" },
        LINE:   { label: "LINE",   color: "text-brand-cyan",   bgColor: "bg-brand-cyan/10" },
        NEWS:   { label: "NEWS",   color: "text-brand-warning",bgColor: "bg-brand-warning/10" },
    };

    if (loading && intel.length === 0) {
        return (
            <div className="p-6 text-center bg-lucrix-surface h-full">
                <p className="text-[10px] text-textMuted font-black uppercase tracking-widest animate-pulse">
                    Fetching live intel...
                </p>
            </div>
        );
    }

    if (intel.length === 0) {
        return (
            <div className="p-6 text-center bg-lucrix-surface h-full">
                <p className="text-[10px] text-textMuted font-black uppercase tracking-widest">
                    No recent intel found
                </p>
            </div>
        );
    }

    return (
        <div className="divide-y divide-lucrix-border bg-lucrix-surface h-full">
            {intel.map((item) => {
                const cfg = typeConfig[item.type] ?? typeConfig.NEWS;
                const time = mounted ? formatTime(item.timestamp) : "—";

                return (
                    <div key={item.id} className="p-4 hover:bg-lucrix-dark transition-colors group">
                        <div className="flex items-start gap-3">
                            <div className="flex flex-col gap-1 min-w-[65px]">
                                <span className={`text-[9px] font-black px-1.5 py-0.5 rounded-sm text-center uppercase tracking-tighter ${cfg.color} ${cfg.bgColor} border border-transparent`}>
                                    {cfg.label}
                                </span>
                                <span className="text-[9px] text-textMuted font-bold text-center uppercase tracking-widest opacity-80 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                    {time}
                                </span>
                            </div>
                            <p className="text-[11px] text-textSecondary leading-relaxed font-medium">
                                {item.message}
                            </p>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
