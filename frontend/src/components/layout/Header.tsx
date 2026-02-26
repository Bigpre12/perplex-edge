"use client";
import { useState, useEffect } from 'react';
import { Search, HelpCircle } from 'lucide-react';
import PushSubscriber from '@/components/dashboard/PushSubscriber';

export default function Header() {
    const [status, setStatus] = useState<'checking' | 'online' | 'offline'>('checking');

    useEffect(() => {
        const checkHealth = async () => {
            try {
                const res = await fetch('http://localhost:8000/health', { signal: AbortSignal.timeout(3000) });
                setStatus(res.ok ? 'online' : 'offline');
            } catch {
                setStatus('offline');
            }
        };
        checkHealth();
        const interval = setInterval(checkHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    const statusLabel = status === 'checking' ? 'Checking...' : status === 'online' ? 'Online' : 'Offline';
    const dotColor = status === 'online' ? 'bg-accent-green animate-pulse' : status === 'offline' ? 'bg-red-500' : 'bg-amber-400 animate-pulse';

    return (
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-800/60 bg-[#102023]/80 backdrop-blur-md z-10 sticky top-0">
            <div className="flex items-center gap-4 text-white">
                <h2 className="text-lg font-bold tracking-tight flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${dotColor}`}></span>
                    Brain Status: {statusLabel}
                </h2>
            </div>

            <div className="flex items-center gap-6">
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-secondary group-focus-within:text-primary transition-colors">
                        <Search size={18} />
                    </div>
                    <input
                        className="bg-surface border border-slate-700 text-white text-sm rounded-lg focus:ring-primary focus:border-primary block w-64 pl-10 p-2 placeholder-secondary/50 transition-all hover:bg-surface-highlight"
                        placeholder="Search models, odds, or events..."
                        type="text"
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-2">
                        <span className="text-xs text-secondary/40 border border-slate-700 rounded px-1.5 py-0.5 font-mono">⌘K</span>
                    </div>
                </div>

                <PushSubscriber />

                <button className="p-2 text-secondary hover:text-white transition-colors rounded-lg hover:bg-surface-highlight">
                    <HelpCircle size={20} />
                </button>
            </div>
        </header>
    );
}
