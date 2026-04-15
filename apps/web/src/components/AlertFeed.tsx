"use client";
import { useState, useEffect } from 'react';
import { Zap, AlertTriangle, TrendingUp, Globe } from 'lucide-react';
import API, { isApiError } from "@/lib/api";

interface Alert {
    id: string;
    type: 'sharp' | 'steam' | 'injury' | 'news';
    message: string;
    timestamp: string;
    severity: 'low' | 'medium' | 'high';
}

export default function AlertFeed() {
    const [alerts, setAlerts] = useState<Alert[]>([]);

    useEffect(() => {
        const fetchAlerts = async () => {
            try {
                const data = await API.recentIntel('basketball_nba');
                if (!isApiError(data) && data.items && data.items.length > 0) {
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    setAlerts(data.items.map((item: any, i: number) => ({
                        id: String(i),
                        type: item.type,
                        message: item.title,
                        timestamp: item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'NOW',
                        severity: item.type === 'injury' ? 'high' : 'medium',
                    })));
                }
            } catch (err) {
                console.error("Failed to fetch alerts:", err);
            }
        };
        fetchAlerts();
        const interval = setInterval(fetchAlerts, 60000); // Check every minute
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-surface/50 border-b border-white/5 py-2 overflow-hidden h-10 flex items-center">
            <div className="flex animate-marquee whitespace-nowrap gap-12 items-center">
                {alerts.map((alert) => (
                    <div key={alert.id} className="flex items-center gap-2 px-4 border-r border-white/10 last:border-0">
                        {alert.type === 'sharp' && <Zap size={14} className="text-primary" />}
                        {alert.type === 'steam' && <TrendingUp size={14} className="text-amber-500" />}
                        {alert.type === 'injury' && <AlertTriangle size={14} className="text-red-500" />}
                        {alert.type === 'news' && <Globe size={14} className="text-blue-400" />}
                        <span className="text-[11px] font-black uppercase tracking-wider text-slate-300">
                            {alert.message}
                        </span>
                        <span className="text-[9px] font-bold text-slate-500 uppercase">{alert.timestamp}</span>
                    </div>
                ))}
                {/* Duplicate for seamless loop */}
                {alerts.map((alert) => (
                    <div key={`${alert.id}-loop`} className="flex items-center gap-2 px-4 border-r border-white/10 last:border-0">
                        {alert.type === 'sharp' && <Zap size={14} className="text-primary" />}
                        {alert.type === 'steam' && <TrendingUp size={14} className="text-amber-500" />}
                        {alert.type === 'injury' && <AlertTriangle size={14} className="text-red-500" />}
                        {alert.type === 'news' && <Globe size={14} className="text-blue-400" />}
                        <span className="text-[11px] font-black uppercase tracking-wider text-slate-300">
                            {alert.message}
                        </span>
                        <span className="text-[9px] font-bold text-slate-500 uppercase">{alert.timestamp}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
