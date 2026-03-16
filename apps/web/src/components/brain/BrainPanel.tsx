'use client';
import { useEffect, useState } from 'react';
import { api, isApiError } from '@/lib/api';
import { SportKey } from '@/lib/sports.config';
import { useLucrixStore } from '@/store';

interface BrainDecision {
    id: string;
    pick: string;
    confidence: number;
    edge: number;
    reasoning: string;
    sport: string;
    timestamp: string;
    result?: 'win' | 'loss' | 'pending';
}

interface BrainMetrics {
    winRate: number;
    roi: number;
    totalPicks: number;
    streak: number;
    avgEdge: number;
}

export default function BrainPanel({ sport }: { sport: SportKey }) {
    const [decisions, setDecisions] = useState<BrainDecision[]>([]);
    const [metrics, setMetrics] = useState<BrainMetrics | null>(null);
    const [tab, setTab] = useState<'live' | 'metrics'>('live');
    const { backendOnline } = useLucrixStore();

    useEffect(() => {
        if (!backendOnline) return;
        const load = async () => {
            const [d, m] = await Promise.all([
                api.brain.decisions(sport, 5),
                api.brain.metrics(),
            ]);

            if (!isApiError(d)) {
                const data = d as any;
                setDecisions(Array.isArray(data) ? data : (data.items || data.decisions || []));
            } else {
                setDecisions([]);
            }
            if (!isApiError(m)) {
                setMetrics(m as any);
            } else {
                setMetrics(null);
            }
        };
        load();
        const t = setInterval(load, 60000);
        return () => clearInterval(t);
    }, [sport, backendOnline]);

    return (
        <div className="brain-panel">
            <div className="brain-header">
                <div className="brain-title-wrap">
                    <span>🧠</span>
                    <h3>Lucrix Brain</h3>
                </div>
                <div className="brain-tab-btn-group">
                    <button
                        onClick={() => setTab('live')}
                        className={`brain-tab-btn ${tab === 'live' ? 'brain-tab-btn-active' : ''}`}
                    >
                        Live Picks
                    </button>
                    <button
                        onClick={() => setTab('metrics')}
                        className={`brain-tab-btn ${tab === 'metrics' ? 'brain-tab-btn-active' : ''}`}
                    >
                        Metrics
                    </button>
                </div>
            </div>

            {tab === 'live' && (
                <div className="brain-picks-container">
                    {decisions.length === 0 && (
                        <p className="brain-empty-state">
                            No active decisions — brain is analyzing...
                        </p>
                    )}
                    {decisions.map(d => (
                        <div key={d.id} className={`decision-card ${d.result === 'win' ? 'decision-card-win' : d.result === 'loss' ? 'decision-card-loss' : 'decision-card-pending'}`}>
                            <div className="decision-card-pick">{d.pick}</div>
                            <div className="decision-card-metrics">
                                <span className="decision-conf-bar-wrap">
                                    <span 
                                        className={`decision-conf-bar w-${Math.round(d.confidence / 10) * 10}p`} 
                                    />
                                    {d.confidence}% conf
                                </span>
                                <span className="decision-edge-tag">+{d.edge}% edge</span>
                            </div>
                            <div className="decision-reasoning">{d.reasoning}</div>
                            <div className="decision-timestamp">
                                {new Date(d.timestamp).toLocaleTimeString()}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {tab === 'metrics' && metrics && (
                <div className="brain-metrics-grid">
                    <MetricCard label="Win Rate" value={`${metrics.winRate}%`} good={metrics.winRate > 55} />
                    <MetricCard label="ROI" value={`${metrics.roi}%`} good={metrics.roi > 0} />
                    <MetricCard label="Total Picks" value={metrics.totalPicks} />
                    <MetricCard label="Streak" value={`${metrics.streak > 0 ? '+' : ''}${metrics.streak}`} good={metrics.streak > 0} />
                    <MetricCard label="Avg Edge" value={`${metrics.avgEdge}%`} good={metrics.avgEdge > 3} />
                </div>
            )}

            {tab === 'metrics' && !metrics && (
                <p className="brain-metrics-empty">
                    No metrics data available
                </p>
            )}
        </div>
    );
}

function MetricCard({ label, value, good }: { label: string; value: any; good?: boolean }) {
    return (
        <div className="metric-card">
            <span className="metric-card-label">{label}</span>
            <span className={`metric-card-value ${good === true ? 'metric-card-value-good' : good === false ? 'metric-card-value-bad' : ''}`}>
                {value}
            </span>
        </div>
    );
}
